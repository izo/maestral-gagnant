# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project

`maestral-gagnant` is a maintained fork of [Maestral](https://github.com/SamSchott/maestral)
(upstream archived 2026-07-28), a light-weight, open-source Dropbox client for macOS and
Linux. The importable Python module is still `maestral`; only the distribution name and
project metadata are fork-specific. GUI frontends (`maestral-qt`, `maestral-cocoa`) live in
separate upstream packages — this repo is the headless core + CLI.

Requires Python 3.10+.

## Commands

Install for development (editable, with all lint/test/bump tooling):

```bash
pip install -e '.[dev]'
```

### Lint

The `lint` CI job runs these four in order and fails on the first non-zero exit. Run the
same locally; the last two auto-fix:

```bash
black --check --diff src tests   # check formatting   → fix with: black src tests
flake8 src tests                 # style
mypy src                         # strict type checking (src only, not tests)
isort --check --diff src tests   # import order        → fix with: isort src tests
```

`pre-commit run -a` runs the equivalent hooks in one shot.

> **CI version drift:** the `[lint]` extra pins no versions, so CI installs the latest
> `black`/`isort`/`mypy` and often flags formatting/typing the repo was last formatted
> against an older tool. When touching a file, run the auto-fixers and pin the tool to the
> version CI resolved (visible in the failed job's install log) before pushing.

### Tests

Tests split into **offline** (pure unit tests, no account) and **linked** (need a real
Dropbox account). CI runs offline on every PR touching `src/**.py` or `tests/**.py`.

```bash
pytest tests/offline                                   # offline suite (CI PR gate)
pytest tests/offline/test_main.py::test_check_for_updates   # a single test
pytest --cov=maestral --cov-report=xml tests/offline   # with coverage (as CI runs it)

pytest tests/linked/unit                               # linked unit tests
pytest tests/linked/integration --fs-observer <auto|inotify|fsevents|polling>
```

Linked tests connect to a real account via the `DROPBOX_ACCESS_TOKEN` or
`DROPBOX_REFRESH_TOKEN` environment variable and **delete the entire Dropbox folder before
and after each test** — only ever point them at a dedicated throwaway account. They acquire
a `test.lock` folder at the Dropbox root to avoid concurrent runs clobbering each other;
fixtures for config/lock setup are in `tests/linked/conftest.py`.

Note: `tests/offline/test_main.py::test_check_for_updates` actually hits the live GitHub
releases API (`GITHUB_RELEASES_API`) and skips when the fork has fewer than two releases.

### Run

```bash
maestral start        # start the sync daemon (headless); -f runs in foreground
maestral gui          # start GUI, spawning a daemon if needed (requires a GUI frontend)
maestral --help       # full CLI reference
```

## Architecture

The client is a layered stack. A request from the CLI/GUI flows top-to-bottom:

```
CLI (click) / GUI  →  Maestral (public API)  →  SyncManager  →  SyncEngine  →  DropboxClient  →  Dropbox SDK
     cli/                  main.py               manager.py       sync.py        client.py
```

- **`main.py` — `Maestral`**: the single public API surface exposed to CLI, GUI, and the
  daemon. Everything external goes through this class (linking, status, config, sync
  control, `check_for_updates`).
- **`manager.py` — `SyncManager`**: coordinates the sync threads (upload, download, local
  file-system observer, connection monitoring) and their lifecycle/locking.
- **`sync.py` — `SyncEngine`**: the heart of the client. Reconciles local and remote state,
  emits/consumes sync events, applies `.mignore` rules, and drives indexing. Largest and
  most regression-sensitive module; integration tests are the primary safety net here.
- **`client.py` — `DropboxClient`**: wraps the Dropbox Python SDK, handling chunked
  up/downloads, pagination, retries, and translating SDK exceptions.

### The daemon and IPC

`daemon.py` runs a `Maestral` instance as a **Pyro5** daemon listening on a unix domain
socket. The CLI and GUI are thin clients that connect through **`MaestralProxy`**, which
transparently forwards attribute/method access to the running daemon (or to an in-process
`Maestral` when no daemon is running). When adding a public method to `Maestral`, remember
it becomes part of the remote-callable surface — arguments and return values must be
serializable by Pyro5.

### State & persistence

- **`database/`**: a small custom SQLite ORM (`orm.py`, `core.py`, `query.py`). Tables are
  defined in **`models.py`** as `Model` subclasses (sync index, sync history, content-hash
  cache).
- **`config/`**: ini-file configuration and persistent state (`config/main.py`,
  `config/user.py`). Supports multiple named configs — each maps to one Dropbox account and
  its own Dropbox folder.
- **`core.py`**: plain dataclasses for internal and external (API-boundary) data.

### Supporting modules

- **`fsevents/`**: local file-system watching (watchdog-backed, with a `polling.py`
  fallback observer). The `--fs-observer` test option selects the backend.
- **`constants.py`**: app identity and paths — `BUNDLE_ID`, app dirs, and
  `GITHUB_RELEASES_API` (the repo the update check polls; fork-pointed).
- **`notify.py`** desktop notifications, **`keyring.py`** credential storage,
  **`errorhandling.py` / `exceptions.py`** SDK-error → Maestral-exception mapping.
- **`cli/`**: click command groups. `cli_main.py` assembles the top-level `main` group;
  `core.py` holds custom click `ParamType`s and the ordered help group.

## Fork-specific notes

- Distribution/metadata is `maestral-gagnant` (author `izo`); the import path stays
  `maestral` for compatibility.
- The `[gui]` extras still reference the upstream `maestral-qt`/`maestral-cocoa`, which
  depend on the upstream `maestral` distribution and may conflict with this fork — prefer
  running headless.
- Publishing workflows tied to upstream infrastructure (DockerHub push/description, Sparkle
  appcast) are disabled with `if: ${{ false }}`; the PyPI publish job is repointed at
  `maestral-gagnant`.
