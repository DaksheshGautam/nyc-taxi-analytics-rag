# NYC Taxi Evidence Assistant

A local retrieval-augmented question-answering app for the NYC yellow taxi project. The actual ten-page analysis PDF is indexed with page citations, alongside original SQL result tables and supporting documents. The interface uses the project’s navy, taxi yellow, teal and charcoal palette.

## Start

Use Python 3.10 or later. From this folder run `python server.py`, or right-click `Start_RAG.ps1` and run with PowerShell. Open http://127.0.0.1:8765. Keep the terminal running; Ctrl+C stops the app. The prebuilt index needs no additional Python packages.

**Evidence search works now without a key. Groq Cloud is configured as the default provider; live answers are pending your new key.** Search results are source excerpts, not generated answers. Questions are independent; conversation history is not sent.

## Included evidence

- `corpus/Analysis_Report.pdf`: the original report, indexed page by page.
- `corpus/Verified_Evidence_FAQ.md`: 27 findings with references to retained result tables.
- `corpus/Metric_Guide.md`: populations, denominators, units and aggregation rules.
- `corpus/Evidence_Limits.md`: coverage and questions the evidence cannot resolve.
- Data dictionary, cleaning investigation, scope, 20 selected CSV result tables and corresponding SQL files for audit.

The generated documents summarize existing evidence; they add no new measured outcomes. Original table rows remain independently searchable. SQL files are downloadable for provenance, not executed by the assistant. Historical published volume is kept distinct from detailed 2025 operational and fare-eligible populations.

## Retrieval and LLM connection

Questions → local BM25 keyword retrieval with domain synonyms → six excerpts → provider → structured claims and supporting quotes → citation and number checks → interface. This version uses lexical retrieval, not embeddings or model fine-tuning. The local version does not query PostgreSQL live or load the complete trip dataset into an LLM.

The OpenAI adapter uses the Responses API with JSON Schema structured output and `store: false`, following the [official structured outputs guide](https://developers.openai.com/api/docs/guides/structured-outputs). A separate OpenAI-compatible chat-completions adapter is included; compatibility depends on the provider supporting strict JSON Schema.

Groq Cloud uses `https://api.groq.com/openai/v1/chat/completions` and defaults to `openai/gpt-oss-20b`, which supports strict structured output according to [Groq’s official documentation](https://console.groq.com/docs/structured-outputs), checked 13 October 2026. This is a Groq-hosted model and requires a Groq key, not an OpenAI key. Model availability and account access must be verified with your key.

When you are ready, put `GROQ_API_KEY` securely in `.env.local` or an environment variable. `.env.example` lists the names; it contains no key. Do not paste credentials into chat or commit them. For a different compatible provider set `LLM_PROVIDER=compatible`, `LLM_BASE_URL`, `LLM_MODEL` and `LLM_API_KEY`. Restart after changing provider configuration.

Only the question and retrieved excerpts are sent to the selected provider when you explicitly use “Ask LLM.” Local evidence search sends no requests to an LLM provider. No prompt or credential logging is implemented. Provider retention policies still apply; `store: false` is not a promise of zero provider retention.

## Grounding limits

The server rejects unknown citation IDs, quotes absent from their cited excerpts, unsupported numeric tokens and malformed or incomplete responses. It withholds rejected generated answers while retaining searchable excerpts. These checks **do not prove semantic entailment**: a model can misinterpret an authentic quote. Review the supplied quotes, populations and original tables before using an answer. Unsupported causes, profits, forecasts and refund interpretations are explicitly excluded by the prompt and evidence guide.

The app binds to localhost, restricts source downloads to a manifest, blocks foreign browser origins, renders text without HTML interpolation and never runs model-generated SQL. It is a local portfolio prototype, not a public multi-user deployment.

## Verification and rebuilding

Run `python test_rag.py` for offline retrieval, grounding, adapter-contract and HTTP checks. `test_validation.json` records results. These tests use a fake provider response; they do not verify live model behavior, billing, latency or provider compatibility.

`index_validation.json` checks all ten report pages, unique chunk IDs, source paths and population reconciliation. `knowledge.json` contains 835 chunks and a SHA-256 source manifest.

To rebuild, install `pypdf`, then run `python build_knowledge.py`. It uses the neighboring project outputs when available, otherwise the included corpus. Rebuild after changing any source. SQL tables are a retained snapshot, not automatically refreshed data.

No live LLM request has been made. Your Groq key is still required for end-to-end LLM verification.


## Neon PostgreSQL deployment

The Streamlit entrypoint is `streamlit_app.py`; it reads verified evidence from Neon PostgreSQL through a SELECT-only role. See `CLOUD_DEPLOYMENT.md`. The project also retains more detailed typed aggregate tables, described in `corpus/DETAILED_DATA_GUIDE.md`. Keyword search alone does not execute arbitrary analytical questions against these large tables.


## Detailed cloud queries

The Streamlit explorer runs parameterized SELECT queries over five compatible table grains (2,254,686 groups). Users select a date range and available dimensions; selected results are added to the next evidence question with their scope. This is a filtered query interface, not an unrestricted natural-language SQL agent. Monthly views use whole source months. Daily views use pickup date, including the drop-off view. Unsupported intersections require the local raw records. Combined means use summed numerators and denominators, never averages of group means or percentiles.

The verified Neon tables and indexes occupy 416,833,536 bytes. All five annual operational and fare-eligible totals reconcile. Nineteen migrated result queries reconcile to retained originals; original MariaDB division rounding is allowed within 0.000051. The raw trip analysis SQL is PostgreSQL-compatible and semantically planned, but raw records remain local and those raw queries were not rerun in Neon.


## Live verification

On 13 October 2026, the deployed Groq adapter returned a busiest-hour answer with exact supporting quotes from the FAQ, report page 6 and hourly results. Invalid generated answers were withheld by grounding checks. This verifies that test question, not every possible answer. See live_llm_validation.json.
