## Relevant Files

- `web/integrations/dropbox/dropbox_service.py` - Main Dropbox service; update internals to workspace-first with fallback.
- `web/integrations/dropbox/workspace_handler.py` - Implement shared folder lookup + caching; update `workspace_call`.
- `web/integrations/views.py` - Remove `dropbox_list` dev endpoint.
- `web/integrations/urls.py` - Remove URL pattern for the dev endpoint.
- `web/orders/services/lease_directory_search.py` - Smoke-check compatibility; no behavior change expected.
- `tasks/prd-dropbox-workspace-first-simplification.md` - Source PRD for this task list.

### Notes

- Unit tests should typically be placed alongside the code files they are testing.
- Use your project's test runner (pytest or Django tests) as applicable.

## Tasks

- [x] 1.0 Implement workspace-first resolution in the workspace handler
  - [x] 1.1 Add first-segment parser and shared-folder cache (name → namespace_id) using `sharing_list_folders()`
  - [x] 1.2 Implement `get_workspace_client(path)` to return namespaced client via `PathRoot.namespace_id(...)` when a match exists
  - [x] 1.3 Implement `get_relative_path(path)` to drop the first segment only when a shared folder match exists
  - [x] 1.4 Refactor `workspace_call(path, api_func)` to: use namespaced client + relative path; return `None` on failure without raising
  - [x] 1.5 Initialize/reset the cache on authenticate (new client instance)
- [x] 2.0 Update Dropbox service internals to use workspace-first, then fallback
  - [x] 2.1 Change `_list_folder` to call workspace-first via handler; on `None`, call regular client
  - [x] 2.2 Change `_get_metadata` to call workspace-first; on `None`, call regular client
  - [x] 2.3 Update `_list_items` to remove exception-driven workspace fallback and use deterministic flow
  - [x] 2.4 Ensure `create_share_link` path → file-id resolution works under workspace-first logic
- [ ] 3.0 Remove the dev-only Dropbox listing endpoint
  - [x] 3.1 Delete `dropbox_list` view from `web/integrations/views.py`
  - [x] 3.2 Remove the `dropbox/list/` URL pattern from `web/integrations/urls.py`
  - [x] 3.3 Search for and remove any references to `dropbox_list`
- [x] 4.0 Add logging and verify background task flows continue to work
  - [x] 4.1 Add INFO/DEBUG logs indicating workspace vs regular mode used for each call
  - [x] 4.2 Manually test `lease_directory_search` happy path (shared folder) and fallback path (non-shared) locally
  - [x] 4.3 Validate no change to public interface; background tasks succeed
- [x] 5.0 Documentation and cleanup
  - [x] 5.1 Update PRD status notes and remove any comments that reference substring-based detection
  - [x] 5.2 Ensure type hints and docstrings are accurate and concise
  - [x] 5.3 Add brief README note for workspace-first behavior and cache
