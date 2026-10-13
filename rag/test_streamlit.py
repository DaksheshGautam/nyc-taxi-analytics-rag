"""Streamlit UI behavior test; no live Groq calls."""
from pathlib import Path
import json
from streamlit.testing.v1 import AppTest
root=Path(__file__).resolve().parent
app=AppTest.from_file(str(root/'streamlit_app.py'),default_timeout=30).run()
assert not app.exception
assert app.title[0].value=='Ask the analysis.'
assert list(app.radio[0].options)==['Search evidence']
app.text_area[0].set_value('Which pickup hour was busiest in 2025?')
next(b for b in app.button if b.label=='Find evidence').click().run()
assert not app.exception
assert any('busiest pickup hour' in x.label.lower() for x in app.expander)
assert any('Analysis report - page 6' in x.label for x in app.expander)
next(b for b in app.button if b.label=='Zone balance').click().run()
assert app.text_area[0].value=='Which zones have more drop-offs than pickups?'
# Submit the synchronized shortcut, without a batched form value overwriting it.
next(b for b in app.button if b.label=='Find evidence').click().run()
assert not app.exception
assert not any('at least three' in w.value for w in app.warning)
assert app.text_area[0].value=='Which zones have more drop-offs than pickups?'
assert any('drop-offs' in x.label.lower() or 'zone' in x.label.lower() for x in app.expander)
app.text_area[0].set_value('Which pickup hour was busiest in 2025?')
next(b for b in app.button if b.label=='Find evidence').click().run()
assert app.session_state['result']['question']=='Which pickup hour was busiest in 2025?'
public=AppTest.from_file(str(root/'streamlit_app.py'),default_timeout=30)
public.secrets['GROQ_API_KEY']='test-only-placeholder'
public.secrets['LLM_PROVIDER']='groq'
public.secrets['LLM_MODEL']='openai/gpt-oss-20b'
public.run()
assert not public.exception
assert list(public.radio[0].options)==['Ask LLM','Search evidence']
assert public.radio[0].value=='Ask LLM'
assert not any(x.label=='LLM access code' for x in public.text_input)
assert not any('Private LLM access' in x.label for x in public.expander)
from unittest.mock import patch
from rag import KnowledgeBase
evidence=KnowledgeBase().by_id['fact-peak-hour']
fake_answer={'status':'answered','claims':[{'statement':'The busiest pickup hour is 18:00-18:59 in 2025.','evidence':[{'source_id':evidence['id'],'quote':evidence['text'].split('Evidence:')[0].strip()}]}]}
with patch('rag.llm_answer',return_value=fake_answer) as mocked:
    public.text_area[0].set_value('Which pickup hour was busiest in 2025?')
    next(b for b in public.button if b.label=='Ask with evidence').click().run()
    assert not public.exception
    before=public.session_state['result']['question']
    public.text_area[0].set_value('How do payment types compare?')
    next(b for b in public.button if b.label=='Ask with evidence').click().run()
    assert public.session_state['result']['question']==before
    assert mocked.call_count==1
    assert any('ten seconds' in w.value for w in public.warning)
checks={'interface_runs':True,'cooldown_preserves_previous_answer_and_chart_scope':True,'shortcut_empty_form_race_fixed':True,'llm_disabled_without_key':True,'public_llm_without_access_code':True,'busiest_hour_retrieval':True,'report_page_citation':True,'live_llm_tested':False}
(root/'streamlit_validation.json').write_text(json.dumps(checks,indent=2));print(json.dumps(checks))
