# Streamlit and Neon PostgreSQL deployment

Run `streamlit run streamlit_app.py` from this directory after installing `requirements.txt`. The cloud app reads the retained evidence snapshot and original documents from Neon PostgreSQL when `[postgres]` is configured. Without the database connection it clearly labels a bundled snapshot fallback. A failed configured database connection stops the app instead of silently switching evidence.

The `nyc_taxi` database has separate `results`, `detail`, `taxi_analysis` and `evidence` schemas. It stores typed analysis-result tables, a checksummed index, original source bytes and excerpt records. The full raw trip history remains local. Active extraction and result queries use PostgreSQL syntax; original DuckDB/MySQL scripts are archived locally for provenance. Runtime uses fixed, parameterized SELECT queries, a dedicated SELECT-only reader and read-only sessions. Connections verify the certificate and hostname using a trusted CA bundle.

Deploy the GitHub directory containing this app through Streamlit Community Cloud; entrypoint is `streamlit_app.py`. Store the reader connection and Groq key in Streamlit secrets, using `secrets.example.toml` as the template. Never commit `.streamlit/secrets.toml`. Provider setup follows [Groq documentation](https://console.groq.com/docs/structured-outputs); cloud secret handling follows [Streamlit documentation](https://docs.streamlit.io/deploy/streamlit-community-cloud/deploy-your-app/secrets-management).

Evidence search and Groq answers are public and require no visitor access code or sign-in. The Groq key and SELECT-only Neon connection stay in server-side secrets. A ten-second per-session cooldown reduces accidental repeat requests; provider quotas still apply. Prompts and answers are not persisted in PostgreSQL. The full verified PDF is available directly beneath the title.

The Neon free plan has resource limits and may suspend idle compute. This prototype does not promise continuous availability. A live busiest-hour answer was verified with report and result citations on 13 October 2026.
