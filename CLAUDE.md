# CLAUDE.md

## Agent skills

### Issue tracker

Issues and PRDs are tracked in GitHub Issues for `wh-kerwin/Alarm-AgentForIC`. See `docs/agents/issue-tracker.md`.

### Triage labels

This repo uses the default five-label triage vocabulary. See `docs/agents/triage-labels.md`.

### Domain docs

This repo uses a single-context domain documentation layout with `CONTEXT.md` at the repo root and ADRs under `docs/adr/`. See `docs/agents/domain.md`.

## Frontend conventions

- Keep Vue single-file components focused and small. Prefer keeping each `.vue` file under 300 lines.
- Componentize frontend code when a page, panel, form, list, or repeated UI block grows beyond a narrow responsibility.
- Do not put CSS styles inline in DOM/template markup. Move styles into the appropriate CSS or SCSS file.
