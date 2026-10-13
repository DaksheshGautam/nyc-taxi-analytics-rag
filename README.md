# NYC Taxi Analytics and Evidence Assistant

NYC yellow taxi analysis with a Tableau dashboard, an evidence-based report, a Neon PostgreSQL database and a Streamlit RAG assistant. Detailed operational analysis covers 2025; published historical volumes are a separate population.

- [Analysis report](analysis/Analysis_Report.pdf)
- [Tableau workbook](tableau/NYC%20Taxi%20Operations.twbx)
- [Analysis documentation and SQL](analysis/README.md)
- [Assistant setup](rag/README.md)
- [Cloud deployment](rag/CLOUD_DEPLOYMENT.md)
- [Detailed data definitions](analysis/DETAILED_DATA_GUIDE.md)
- [PostgreSQL verification](analysis/postgresql_execution_validation.json)

Neon holds 2,254,686 detailed groups, plus retained result tables and checksummed report evidence. All five detailed table totals reconcile to 48,157,684 operational trips and 44,727,165 fare-eligible records. Raw trips remain local. The cloud explorer supports compatible filtered dimensions and adds selected results to question evidence; it is not an unrestricted natural-language SQL agent.

Evidence search works without an API key. Groq answers require a private server-side key and access code. Live LLM testing is pending key entry.

No owner credentials, database passwords, API keys or private access codes are included.
