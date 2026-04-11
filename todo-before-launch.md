# cliche-mcp — TODO before launch

## Blockers (must do before PyPI / GitHub public)

- [ ] **`clichefactory` SDK must be on PyPI first** — this package depends on `clichefactory` which isn't published yet. The MCP package can't go to PyPI until the SDK does.

- [ ] **Remove `[tool.uv.sources]` local path** — `pyproject.toml` has `clichefactory = { path = "../aio" }` which is dev-only. Remove before pushing to GitHub (anyone cloning won't have `../aio`). Can keep it locally via `uv.toml` or a dev override if needed.

- [ ] **Move local parsing deps to optional extras** — the heavy local stack (pymupdf, docling, tesserocr, etc. ~2GB+) is currently required for all installs. Service-only users don't need any of it. Change to:
  ```toml
  dependencies = [
      "mcp[cli]>=1.0.0,<2",
      "clichefactory",
  ]

  [project.optional-dependencies]
  local = ["clichefactory[local]"]
  ```
  So `pip install clichefactory-mcp` is lightweight and `pip install clichefactory-mcp[local]` pulls the full stack.

## Should do

- [ ] **Pin `mcp[cli]` version range** — currently unpinned. Add at least `"mcp[cli]>=1.0.0,<2"` (or whatever range has been tested).

- [ ] **Stabilize private SDK imports** — `helpers.py` imports from `clichefactory._config` (private module). Either:
  - Promote those resolvers to public API in the SDK (preferred), or
  - Pin `clichefactory` version tightly (e.g. `>=0.1.0,<0.2.0`) and accept the coupling.

- [ ] **Add PyPI metadata to `pyproject.toml`** — missing `readme`, `license`, `authors`, `urls`, `keywords`, `classifiers`:
  ```toml
  readme = "README.md"
  license = {text = "..."}
  authors = [{name = "ClicheFactory", email = "..."}]
  keywords = ["mcp", "document-extraction", "pydantic", "ocr", "pdf"]
  classifiers = [
      "Development Status :: 3 - Alpha",
      "Programming Language :: Python :: 3",
  ]

  [project.urls]
  Homepage = "https://clichefactory.com"
  Repository = "https://github.com/ClicheFactory/cliche-mcp"
  ```

- [ ] **Add LICENSE file** — README references a license but no file exists in the repo.

## Nice to have

- [ ] **Commit `uv.lock`** — `.gitignore` currently excludes it. For an application/server, committing the lock file gives reproducible installs.

- [ ] **Publish OpenClaw skill to ClawHub** — once the MCP server is on PyPI, run:
  ```bash
  clawhub skill publish ./integrations/openclaw --slug clichefactory --name "ClicheFactory" --version 0.1.0 --tags latest
  ```
