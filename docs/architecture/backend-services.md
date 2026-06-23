# Backend Services Direction

## Relational Storage

The backend storage direction is:

- Development: SQLite
- Production: PostgreSQL

The current MVP uses SQLite for write-path application data in development:

- feedback records
- audit records
- local engineer-created knowledge cases

JSON files remain for checked-in seed/fixture data:

- mock alerts
- mock events
- SOP actions
- context policies
- seed knowledge cases
- role policies

PostgreSQL is reserved for production. The code recognizes PostgreSQL-style `DATABASE_URL` values as a production target, but the active repository implementation is SQLite.

Planned environment variable:

```text
DATABASE_URL=sqlite:///data/alarm_agent.db
DATABASE_URL=postgresql://user:password@host:5432/alarm_agent
```

Initialize SQLite locally:

```powershell
& 'C:\Python313\python.exe' scripts\init_db.py
```

## Vector Database

The process knowledge base should use ChromaDB.

Planned responsibilities:

- Store SOP/OCAP chunks.
- Store process notes and historical case embeddings.
- Retrieve evidence candidates for the RCA pipeline.
- Keep retrieval output separate from deterministic facts until cited in the evidence chain.

Planned environment variables:

```text
CHROMA_PERSIST_DIRECTORY=data/chroma
CHROMA_COLLECTION=process_knowledge
```

The current code provides a reserved `ChromaProcessKnowledgeStore` boundary so the retrieval implementation can be added without changing the analyzer interface later.

## LLM Explanation Layer

The LLM layer is evidence-only:

- It explains already-collected evidence.
- It does not create new root causes.
- It does not invent data sources, SOPs, measurements, or actions.
- It must degrade cleanly when disabled or unavailable.

Provider direction:

- Active implementation: OpenAI Responses API through standard-library HTTP.
- Reserved adapters: DeepSeek and Qwen.

Environment variables:

```text
LLM_PROVIDER=disabled
OPENAI_API_KEY=
OPENAI_MODEL=gpt-4.1-mini
DEEPSEEK_API_KEY=
QWEN_API_KEY=
```
