# Domain Docs

How engineering skills should consume this repo's domain documentation.

## Layout

This is a single-context repo.

- Read `CONTEXT.md` at the repo root before domain-heavy planning or implementation.
- Read ADRs under `docs/adr/` when they exist and touch the area being changed.
- If a file does not exist yet, proceed silently.

## Vocabulary

Use the domain terms defined in `CONTEXT.md` when writing PRDs, issues, implementation plans, tests, and architecture notes.

Avoid inventing synonyms for existing terms. If a needed concept is missing, note the gap and update `CONTEXT.md` when the term becomes stable.

## ADR Conflicts

If a proposed change contradicts an existing ADR, call that out explicitly before proceeding.

