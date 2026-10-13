"""Streamlit Cloud UI backed by the Neon PostgreSQL evidence snapshot."""
import json,hmac,time,mimetypes
import streamlit as st
from rag import KnowledgeBase,config,readiness,llm_answer,GroundingError,LLMError,ROOT
from cloud_store import load_knowledge,load_source

st.set_page_config(page_title='NYC Taxi Evidence Assistant',page_icon='🚕',layout='wide')
def settings():
    try:return st.secrets.to_dict()
    except FileNotFoundError:return {}

@st.cache_resource(ttl=300)
def knowledge(_db,fingerprint):return KnowledgeBase(data=load_knowledge(_db))

values=settings();llm=config()
for k in ['GROQ_API_KEY','LLM_PROVIDER','LLM_MODEL','LLM_BASE_URL']:
    if k in values:llm[k]=values[k]
db=values.get('postgres',{})
st.caption('NYC YELLOW TAXI · SOURCE SNAPSHOT: 12 OCTOBER 2026')
st.title('Ask the analysis.')
st.write('Explore the report, definitions and recorded results. Inspect the evidence behind each answer.')
try:
    if db.get('url'):
        import hashlib
        kb=knowledge(db,hashlib.sha256(db['url'].encode()).hexdigest());storage='Neon PostgreSQL'
    else:kb=KnowledgeBase();storage='Bundled snapshot — Neon connection pending'
except Exception:
    st.error('The evidence database could not be verified. Please try again later.');st.stop()
st.caption(f'{storage} · {len(kb.manifest)} documents · {len(kb.chunks)} excerpts · detailed analysis: 2025')
with st.sidebar:
    st.header('Answer mode')
    access=st.text_input('LLM access code',type='password',help='Evidence search is public. The private access code enables requests using the project’s Groq key.')
    expected=values.get('LLM_ACCESS_CODE','')
    unlocked=bool(expected and access and hmac.compare_digest(access,expected))
    enabled=readiness(llm) and unlocked
    mode=st.radio('Choose a mode',['Search evidence','Ask LLM'] if enabled else ['Search evidence'])
    if not readiness(llm):st.info('Groq key setup pending. Evidence search works now.')
    elif not unlocked:st.info('Enter the private access code to enable LLM answers.')
    st.caption('Questions are independent. No chat history is stored. LLM mode sends your question and retrieved excerpts to Groq.')
if db.get('url'):
    from detailed_store import GRAINS,zones,summary
    import datetime
    with st.expander('Explore detailed database numbers'):
        st.caption('Each view supports only its listed dimensions. Monthly views use whole source months; daily views use pickup date, including the drop-off view. Means use summed numerators and denominators. Raw trip records are retained locally.')
        grain=st.selectbox('Available analysis',list(GRAINS))
        available=GRAINS[grain][2]
        zone_choices={'All zones':None}
        try:
            for zid,borough,name in zones(db):zone_choices[f'{borough} · {name} ({zid})']=zid
        except Exception:st.error('Zone lookup unavailable. Please try again later.')
        with st.form('detail_filters'):
            start=st.date_input('From',datetime.date(2025,1,1),min_value=datetime.date(2025,1,1),max_value=datetime.date(2025,12,31))
            end=st.date_input('Through',datetime.date(2025,12,31),min_value=datetime.date(2025,1,1),max_value=datetime.date(2025,12,31))
            filters={}
            for dimension in available:
                if dimension.endswith('_zone'):
                    label=st.selectbox(dimension.replace('_',' ').title(),list(zone_choices));value=zone_choices[label]
                elif dimension=='pickup_hour':value=st.selectbox('Pickup hour',['All hours']+list(range(24)));value=None if value=='All hours' else value
                else:
                    payments={'All payments':None,'0 · Flex Fare':0,'1 · Credit card':1,'2 · Cash':2,'3 · No charge':3,'4 · Dispute':4,'5 · Unknown':5,'6 · Voided trip':6}
                    value=payments[st.selectbox('Payment type',list(payments))]
                if value is not None:filters[dimension]=value
            run_detail=st.form_submit_button('Retrieve supporting numbers')
        if run_detail:
            try:
                with st.spinner('Querying Neon…'):st.session_state['detail_result']=summary(db,grain,start,end,filters)
            except ValueError as e:st.error(str(e))
            except Exception:st.error('The detailed query could not complete. Please try again later.')
        if 'detail_result' in st.session_state:
            d=st.session_state['detail_result'];st.json(d['scope'])
            a,b=st.columns(2);a.metric('Operational trips',f"{d['data']['operational_trips']:,}");b.metric('Fare-eligible records',f"{d['data']['fare_eligible_records']:,}")
            st.json(d['data']);st.code(d['sql'],language='sql');st.caption('Parameters: '+json.dumps(d['parameters']))
            st.download_button('Download selected results',json.dumps(d,default=str,indent=2),'nyc_taxi_query_result.json','application/json')
            st.caption('This selected scope is included as evidence for your next question below. Clear it before asking about a different scope.')
            if st.button('Clear selected query evidence'):del st.session_state['detail_result'];st.rerun()
with st.form('question_form'):
    question=st.text_area('Your question',placeholder='Which pickup hour was busiest in 2025?',max_chars=2000)
    submitted=st.form_submit_button('Find evidence' if mode=='Search evidence' else 'Ask with evidence')
if submitted:
    if len(question.strip())<3:st.warning('Enter a question of at least three characters.')
    else:
        chunks=kb.search(question)
        if 'detail_result' in st.session_state:chunks=[st.session_state['detail_result']['chunk']]+chunks
        if not chunks:st.info('No matching project evidence was found.')
        elif mode=='Ask LLM':
            last=st.session_state.get('last_llm_request',0)
            if time.monotonic()-last<10:st.warning('Please wait ten seconds between LLM requests.')
            else:
                st.session_state['last_llm_request']=time.monotonic()
                try:
                    with st.spinner('Checking an answer against retrieved evidence…'):result=llm_answer(question,chunks,llm)
                    st.session_state['result']={'claims':result['claims'],'sources':chunks,'message':'No supported answer was established.' if result['status']=='insufficient_evidence' else 'Review the supporting quotes before relying on this answer.'}
                except GroundingError:st.session_state['result']={'claims':[],'sources':chunks,'message':'The generated answer failed grounding checks and was withheld.'}
                except LLMError as e:st.session_state['result']={'claims':[],'sources':chunks,'message':str(e)}
        else:st.session_state['result']={'claims':[],'sources':chunks,'message':'Retrieved excerpts only — no LLM-generated answer.'}
if 'result' in st.session_state:
    result=st.session_state['result'];st.subheader('Answer and evidence' if result['claims'] else 'Retrieved evidence');st.info(result['message'])
    for claim in result['claims']:
        st.write(claim['statement'])
        for ref in claim['evidence']:
            source=next(c for c in result['sources'] if c['id']==ref['source_id'])
            st.text(ref['quote']);st.caption(source['source']+(f" · page {source['page']}" if source.get('page') else ''))
    for c in result['sources']:
        with st.expander(c['title'],expanded=False):
            st.caption(c['source']+(f" · page {c['page']}" if c.get('page') else '')+(f" · CSV row {c['row']}" if c.get('row') else ''))
            st.text(c['text'])
with st.expander('Evidence library and original report'):
    sources={m['path']:m for m in kb.manifest}
    chosen=st.selectbox('Choose a document',list(sources))
    if st.button('Prepare source download'):
        try:
            m=sources[chosen];content=load_source(db,chosen,m['sha256']) if db.get('url') else (ROOT/'corpus'/chosen).read_bytes()
            st.download_button('Download '+chosen.split('/')[-1],content,file_name=chosen.split('/')[-1],mime=mimetypes.guess_type(chosen)[0] or 'application/octet-stream')
        except Exception:st.error('The source could not be verified for download.')
st.caption('Citation, quote and numeric checks do not prove semantic correctness. This snapshot cannot establish causes, driver profit, refunds or future demand. Search is lexical BM25, not embedding retrieval.')
