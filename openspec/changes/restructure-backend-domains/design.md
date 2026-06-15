## Context

The `tradingassistant/` package currently houses 5 backend domain sub-packages (charting, indicators, infrastructure, market_data, transport), 4 standalone backend modules (events.py, diagnostics.py, runtime.py, redis_upgrade.py), and 1 frontend sub-package all in a flat namespace. This makes it unclear where the backend/frontend boundary is and complicates selective tooling (e.g., linting only backend code, excluding frontend Reflex components).

The project already has a clean internal dependency graph: frontend imports backend domains, backend domains import each other. The restructure will make this dependency explicit in the directory tree.

### Current vs Target

```
Before:                          After:
tradingassistant/                tradingassistant/
??? charting/            ?       ??? backend/
??? indicators/          ?       ?   ??? charting/
??? infrastructure/      ?       ?   ??? indicators/
??? market_data/         ?       ?   ??? infrastructure/
??? transport/           ?       ?   ??? market_data/
??? frontend/                    ?   ??? transport/
??? events.py            ?       ?   ??? events.py
??? diagnostics.py       ?       ?   ??? diagnostics.py
??? runtime.py           ?       ?   ??? runtime.py
??? redis_upgrade.py     ?       ?   ??? redis_upgrade.py
??? settings.py                  ?   ??? __init__.py
??? __init__.py                  ??? frontend/
                                 ??? settings.py
                                 ??? __init__.py
```

## Goals / Non-Goals

**Goals:**
- Move all backend domain modules under `tradingassistant/backend/`
- Update all absolute import paths consistently
- Preserve identical runtime behavior (zero behavioral diffs)
- Keep `settings.py` at root as shared config
- Keep all OpenSpec specs valid

**Non-Goals:**
- Do not change any public API signatures
- Do not refactor module internals
- Do not add or remove functionality
- Do not touch `tradingassistant/frontend/` contents
- Do not modify test logic

## Decisions

### Decision 1: Move strategy ? fileglide `path move` for directories, `file move` for modules

**Rationale**: Using fileglide ensures atomic moves with verification, UTF-8 encoding safety, and consistent JSON output for scripting. Git will track these as renames, preserving file history.

**Alternative considered**: Manual `Move-Item` in PowerShell. Rejected because fileglide provides encoding verification and atomic operation guarantees per the project's AGENTS.md constraints.

### Decision 2: Import path rewrite ? bulk `str.replace()` across all 19 affected files

**Rationale**: All import changes follow a simple `<old> ? <new>` pattern. A scripted approach is faster and less error-prone than manual editing 70 lines.

**Patterns to replace**:
| Old prefix | New prefix |
|---|---|
| `from tradingassistant.charting` | `from tradingassistant.backend.charting` |
| `from tradingassistant.indicators` | `from tradingassistant.backend.indicators` |
| `from tradingassistant.infrastructure` | `from tradingassistant.backend.infrastructure` |
| `from tradingassistant.market_data` | `from tradingassistant.backend.market_data` |
| `from tradingassistant.transport` | `from tradingassistant.backend.transport` |
| `from tradingassistant.events` | `from tradingassistant.backend.events` |
| `from tradingassistant.diagnostics` | `from tradingassistant.backend.diagnostics` |
| `from tradingassistant.runtime` | `from tradingassistant.backend.runtime` |
| `from tradingassistant.redis_upgrade` | `from tradingassistant.backend.redis_upgrade` |
| `import tradingassistant.settings` | (unchanged ? stays at root) |

**Alternative considered**: Using `ruff` or `isort` auto-fix. Rejected because these tools don't know about our custom package restructure and may produce incorrect results.

### Decision 3: `settings.py` stays at root

**Rationale**: `settings.py` is imported by both `main.py` (backend entry), `rxconfig.py` (frontend config), and modules inside `backend/`. Keeping it at `tradingassistant.settings` avoids a circular dependency where backend needs frontend config or vice versa.

### Decision 4: Verification strategy

**Sequence**: file moves ? import rewrites ? ruff check ? ruff format ? run test suite ? git commit

## Risks / Trade-offs

- **Risk**: Relative imports within backend modules may break if not carefully handled ? **Mitigation**: All intra-backend imports already use absolute paths; no `from ..` cross-boundary imports exist
- **Risk**: Test files are the largest consumer of imports (8 files, ~40 lines) ? **Mitigation**: Apply the same `str.replace()` logic uniformly; tests use the same import patterns as source code
- **Risk**: `rxconfig.py` has a hardcoded `app_module_import="tradingassistant.frontend.app"` which references frontend ? **Mitigation**: This path is unchanged since frontend stays at root
