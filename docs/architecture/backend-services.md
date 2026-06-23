# Backend Services Direction

## Relational Storage

The backend storage direction is:

- Development: SQLite
- Production: PostgreSQL

The current MVP still uses JSON files for feedback, audit records, local knowledge cases, and mock fixtures. The next persistence slice should replace those JSON stores with repository interfaces backed by SQLite in development and PostgreSQL in production.

Planned environment variable:

```text
DATABASE_URL=sqlite:///data/alarm_agent.db
DATABASE_URL=postgresql://user:password@host:5432/alarm_agent
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
