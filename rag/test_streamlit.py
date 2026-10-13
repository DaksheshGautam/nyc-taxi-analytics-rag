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
checks={'interface_runs':True,'llm_disabled_without_key':True,'busiest_hour_retrieval':True,'report_page_citation':True,'live_llm_tested':False}
(root/'streamlit_validation.json').write_text(json.dumps(checks,indent=2));print(json.dumps(checks))
