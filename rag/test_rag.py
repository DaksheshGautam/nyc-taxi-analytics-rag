"""Offline behavior checks; no live API calls or real credentials."""
import unittest,json,threading,urllib.request,urllib.error,os
from unittest.mock import patch
from http.server import ThreadingHTTPServer
from rag import KnowledgeBase,validate_answer,GroundingError,llm_answer,LLMError,ROOT
import server
KB=KnowledgeBase()
QUERIES=[('Which pickup hour was busiest in 2025?','fact-peak-hour'),('When does recorded meter fare revenue peak?','fact-fare-peak'),('Why were 564,918 records excluded?','fact-funnel'),('What does payment code 0 mean?','fact-flex-fare'),('Are negative fares refunds?','fact-negative-money'),('Which zones receive more drop-offs than pickups?','fact-arrivals'),('Why are operational trips different from fare eligible records?','fact-fare-eligibility')]

class RetrievalTests(unittest.TestCase):
    def test_questions_find_expected_evidence(self):
        for q,expected in QUERIES:
            with self.subTest(question=q):self.assertIn(expected,[c['id'] for c in KB.search(q)])
    def test_report_pages_and_hashes(self):
        import hashlib
        self.assertEqual({c['page'] for c in KB.chunks if c['kind']=='report'},set(range(1,11)))
        for m in KB.manifest:self.assertEqual(hashlib.sha256((ROOT/'corpus'/m['path']).read_bytes()).hexdigest(),m['sha256'])
    def test_unrelated_query_has_no_evidence(self):self.assertEqual(KB.search('Tokyo semiconductor GDP'),[])

class AnswerTests(unittest.TestCase):
    def setUp(self):
        self.chunks=[KB.by_id['fact-peak-hour']]
        self.quote=self.chunks[0]['text'].split('Evidence:')[0].strip()
        self.result={'status':'answered','claims':[{'statement':'The busiest pickup hour is 18:00-18:59 in 2025.','evidence':[{'source_id':'fact-peak-hour','quote':self.quote}]}]}
    def test_supported_answer_passes(self):self.assertEqual(validate_answer(self.result,self.chunks),self.result)
    def test_fabricated_id_rejected(self):
        self.result['claims'][0]['evidence'][0]['source_id']='invented'
        with self.assertRaises(GroundingError):validate_answer(self.result,self.chunks)
    def test_fabricated_quote_rejected(self):
        self.result['claims'][0]['evidence'][0]['quote']='Trips were caused by commuter traffic.'
        with self.assertRaises(GroundingError):validate_answer(self.result,self.chunks)
    def test_unsupported_number_rejected(self):
        self.result['claims'][0]['statement']='There were 999999999 trips.'
        with self.assertRaises(GroundingError):validate_answer(self.result,self.chunks)
    def test_insufficient_has_no_claims(self):
        self.result['status']='insufficient_evidence'
        with self.assertRaises(GroundingError):validate_answer(self.result,self.chunks)
    def test_openai_adapter_contract(self):
        def fake(url,payload):
            self.assertTrue(url.endswith('/responses'));self.assertFalse(payload['store']);self.assertTrue(payload['text']['format']['strict'])
            return {'status':'completed','output':[{'content':[{'type':'output_text','text':json.dumps(self.result)}]}]}
        result=llm_answer('Busiest hour?',self.chunks,{'OPENAI_API_KEY':'offline-test-placeholder','LLM_MODEL':'test','LLM_BASE_URL':'https://api.openai.com/v1'},fake)
        self.assertEqual(result,self.result)
    def test_missing_config_never_calls_provider(self):
        with self.assertRaises(LLMError):llm_answer('Busiest hour?',self.chunks,{},lambda *a:self.fail('Provider must not be called'))
    def test_groq_adapter_contract(self):
        def fake(url,payload):
            self.assertEqual(url,'https://api.groq.com/openai/v1/chat/completions')
            self.assertEqual(payload['model'],'openai/gpt-oss-20b')
            self.assertTrue(payload['response_format']['json_schema']['strict'])
            refs=payload['response_format']['json_schema']['schema']['properties']['claims']['items']['properties']['source_ids']['items']
            self.assertEqual(refs['enum'],['fact-peak-hour'])
            self.assertIn('fact-peak-hour',payload['messages'][1]['content'])
            return {'choices':[{'finish_reason':'stop','message':{'content':json.dumps(self.result)}}]}
        self.assertEqual(llm_answer('Busiest hour?',self.chunks,{'LLM_PROVIDER':'groq','GROQ_API_KEY':'offline-placeholder','LLM_MODEL':'openai/gpt-oss-20b'},fake),self.result)
    def test_openai_key_does_not_activate_groq(self):
        from rag import readiness
        self.assertFalse(readiness({'LLM_PROVIDER':'groq','OPENAI_API_KEY':'offline-placeholder','LLM_MODEL':'test'}))
    def test_source_ids_attach_exact_evidence(self):
        answer={'status':'answered','claims':[{'statement':self.result['claims'][0]['statement'],'source_ids':['fact-peak-hour']}]}
        def fake(*args):return {'choices':[{'finish_reason':'stop','message':{'content':json.dumps(answer)}}]}
        actual=llm_answer('Busiest hour?',self.chunks,{'LLM_PROVIDER':'groq','GROQ_API_KEY':'offline-placeholder','LLM_MODEL':'openai/gpt-oss-20b'},fake)
        self.assertEqual(actual['claims'][0]['evidence'][0]['quote'],self.chunks[0]['text'])
        answer['claims'][0]['statement']='There were 999999999 trips.'
        with self.assertRaises(GroundingError):llm_answer('Busiest hour?',self.chunks,{'LLM_PROVIDER':'groq','GROQ_API_KEY':'offline-placeholder','LLM_MODEL':'openai/gpt-oss-20b'},fake)
    def test_groq_schema_failure_retried_and_validated(self):
        import io
        calls=[]
        def fake(url,payload):
            calls.append(payload)
            if len(calls)==1:raise urllib.error.HTTPError(url,400,'Bad Request',{},io.BytesIO(b'{"error":{"code":"json_validate_failed"}}'))
            self.assertEqual(payload['response_format']['type'],'json_object')
            return {'choices':[{'finish_reason':'stop','message':{'content':json.dumps(self.result)}}]}
        self.assertEqual(llm_answer('Busiest hour?',self.chunks,{'LLM_PROVIDER':'groq','GROQ_API_KEY':'offline-placeholder','LLM_MODEL':'openai/gpt-oss-20b'},fake),self.result)
        self.assertEqual(len(calls),2)
    def test_rate_limit_has_actionable_message(self):
        import io
        def fake(url,payload):raise urllib.error.HTTPError(url,429,'Limited',{},io.BytesIO(b'{"error":{"code":"rate_limit_exceeded"}}'))
        with self.assertRaisesRegex(LLMError,'limit resets'):
            llm_answer('Busiest hour?',self.chunks,{'LLM_PROVIDER':'groq','GROQ_API_KEY':'offline-placeholder','LLM_MODEL':'openai/gpt-oss-20b'},fake)
    def test_incomplete_response_withheld(self):
        with self.assertRaises(LLMError):llm_answer('Busiest hour?',self.chunks,{'OPENAI_API_KEY':'placeholder','LLM_MODEL':'test'},lambda *a:{'status':'incomplete','output':[]})

class HTTPTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        server.KB=KB;cls.http=ThreadingHTTPServer(('127.0.0.1',0),server.Handler);cls.thread=threading.Thread(target=cls.http.serve_forever,daemon=True);cls.thread.start();cls.url=f'http://127.0.0.1:{cls.http.server_port}'
    @classmethod
    def tearDownClass(cls):cls.http.shutdown();cls.http.server_close();cls.thread.join()
    def request(self,path,body=None,headers=None):
        h=headers or {}
        if body is not None:h['Content-Type']='application/json'
        req=urllib.request.Request(self.url+path,json.dumps(body).encode() if body is not None else None,h)
        try:
            with urllib.request.urlopen(req) as r:return r.status,r.read()
        except urllib.error.HTTPError as e:return e.code,e.read()
    def test_search_returns_sources(self):
        code,data=self.request('/api/ask',{'question':'Busiest pickup hour?','mode':'search'});self.assertEqual(code,200);self.assertTrue(json.loads(data)['sources'])
    def test_llm_pending_without_key(self):
        with patch.dict(os.environ,{'OPENAI_API_KEY':'','GROQ_API_KEY':'','LLM_API_KEY':'','LLM_MODEL':''}):
            code,data=self.request('/api/ask',{'question':'Busiest pickup hour?','mode':'llm'});self.assertEqual(code,409);self.assertEqual(json.loads(data)['status'],'setup_pending')
    def test_foreign_origin_rejected(self):self.assertEqual(self.request('/api/ask',{'question':'Busiest hour?'},{'Origin':'https://untrusted.example'})[0],403)
    def test_secret_and_traversal_inaccessible(self):
        for path in ['/.env.local','/sources/../rag.py','/sources/%2e%2e/rag.py']:self.assertEqual(self.request(path)[0],404)
    def test_static_and_report_available(self):
        self.assertEqual(self.request('/')[0],200);self.assertTrue(self.request('/sources/Analysis_Report.pdf')[1].startswith(b'%PDF'))

if __name__=='__main__':
    suite=unittest.defaultTestLoader.loadTestsFromModule(__import__(__name__));result=unittest.TextTestRunner(verbosity=2).run(suite)
    (ROOT/'test_validation.json').write_text(json.dumps({'tests_run':result.testsRun,'failures':len(result.failures),'errors':len(result.errors),'retrieval_cases':len(QUERIES),'live_llm_tested':False},indent=2))
    raise SystemExit(not result.wasSuccessful())

