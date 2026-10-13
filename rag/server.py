"""Loopback-only local app. No database mutations or arbitrary document uploads."""
from pathlib import Path
from http.server import ThreadingHTTPServer,BaseHTTPRequestHandler
from urllib.parse import urlparse,unquote
import argparse,json,mimetypes,threading
from rag import ROOT,KnowledgeBase,readiness,llm_answer,LLMError,GroundingError

KB=None
LLM_SLOTS=threading.BoundedSemaphore(2)
class Handler(BaseHTTPRequestHandler):
    def log_message(self,*args):pass  # Never log prompts or credentials.
    def send(self,status,body,kind='application/json'):
        if kind=='application/json':body=json.dumps(body,ensure_ascii=False).encode()
        self.send_response(status);self.send_header('Content-Type',kind+'; charset=utf-8' if kind.startswith('text/') else kind)
        self.send_header('Content-Length',str(len(body)));self.send_header('X-Content-Type-Options','nosniff')
        self.send_header('Cache-Control','no-store');self.send_header('Referrer-Policy','no-referrer')
        self.send_header('Content-Security-Policy',"default-src 'self'; script-src 'self'; style-src 'self'; connect-src 'self'; frame-src 'self'; object-src 'none'; base-uri 'none'")
        self.end_headers();self.wfile.write(body)
    def local(self):
        allowed={f'127.0.0.1:{self.server.server_port}',f'localhost:{self.server.server_port}'}
        return self.headers.get('Host','') in allowed
    def do_GET(self):
        if not self.local():return self.send(403,{'error':'Local access only.'})
        path=unquote(urlparse(self.path).path)
        if path=='/api/status':return self.send(200,{'llm_ready':readiness(),'chunks':len(KB.chunks),'sources':len(KB.manifest),'snapshot':'12 October 2026','mode':'LLM with evidence' if readiness() else 'Evidence search only'})
        if path=='/api/sources':return self.send(200,{'sources':KB.manifest})
        static={'/':'static/index.html','/app.js':'static/app.js','/style.css':'static/style.css'}
        if path in static:p=ROOT/static[path]
        elif path.startswith('/sources/'):
            relative=path[len('/sources/'):]
            allowed={m['path'] for m in KB.manifest}
            if relative not in allowed:return self.send(404,{'error':'Source not found.'})
            p=ROOT/'corpus'/relative
            if not p.resolve().is_relative_to((ROOT/'corpus').resolve()):return self.send(403,{'error':'Invalid source path.'})
        else:return self.send(404,{'error':'Not found.'})
        if not p.is_file():return self.send(404,{'error':'File not found.'})
        kind=mimetypes.guess_type(p.name)[0] or 'application/octet-stream'
        return self.send(200,p.read_bytes(),kind)
    def do_POST(self):
        if not self.local():return self.send(403,{'error':'Local access only.'})
        origin=self.headers.get('Origin')
        allowed={f'http://127.0.0.1:{self.server.server_port}',f'http://localhost:{self.server.server_port}'}
        if origin and origin not in allowed:return self.send(403,{'error':'Request origin rejected.'})
        if self.path!='/api/ask':return self.send(404,{'error':'Not found.'})
        if self.headers.get('Content-Type','').split(';')[0]!='application/json':return self.send(415,{'error':'JSON required.'})
        try:
            length=int(self.headers.get('Content-Length','0'))
            if length<1 or length>12000:return self.send(413,{'error':'Request size rejected.'})
            obj=json.loads(self.rfile.read(length));question=obj.get('question')
            if not isinstance(question,str) or not 3<=len(question.strip())<=2000:return self.send(400,{'error':'Use a question of 3 to 2,000 characters.'})
            question=question.strip();mode=obj.get('mode','search')
            if mode not in ['search','llm']:return self.send(400,{'error':'Invalid mode.'})
        except (ValueError,AttributeError):return self.send(400,{'error':'Invalid request.'})
        chunks=KB.search(question)
        if not chunks:return self.send(200,{'status':'insufficient_evidence','mode':mode,'claims':[],'sources':[],'message':'No matching evidence was found in this project.'})
        if mode=='search':return self.send(200,{'status':'evidence_found','mode':'search','claims':[],'sources':chunks,'message':'These are retrieved source excerpts, not an LLM-generated answer.'})
        if not readiness():return self.send(409,{'status':'setup_pending','mode':'search','claims':[],'sources':chunks,'message':'LLM setup is pending. You can inspect the evidence now.'})
        if not LLM_SLOTS.acquire(blocking=False):return self.send(429,{'error':'Two answers are already running. Try again shortly.'})
        try:
            result=llm_answer(question,chunks)
            return self.send(200,dict(result,mode='llm',sources=chunks,message='Check the supporting quotes before relying on the answer.'))
        except GroundingError:
            return self.send(422,{'status':'grounding_rejected','mode':'search','claims':[],'sources':chunks,'message':'The generated answer failed a citation, quote or number check. It was withheld; inspect the source excerpts instead.'})
        except LLMError as e:return self.send(502,{'status':'llm_error','mode':'search','claims':[],'sources':chunks,'message':str(e)})
        finally:LLM_SLOTS.release()

def main():
    global KB
    parser=argparse.ArgumentParser();parser.add_argument('--port',type=int,default=8765);args=parser.parse_args()
    KB=KnowledgeBase();http=ThreadingHTTPServer(('127.0.0.1',args.port),Handler)
    print(f'NYC Taxi Evidence Assistant: http://127.0.0.1:{args.port}',flush=True)
    print('LLM configured.' if readiness() else 'Evidence search available. Live LLM setup pending.',flush=True)
    try:http.serve_forever()
    except KeyboardInterrupt:pass
    finally:http.server_close()
if __name__=='__main__':main()
