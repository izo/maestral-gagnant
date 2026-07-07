# Fork backlog — `maestral-gagnant`

Follow-up work identified while preparing this fork of the archived upstream
[Maestral](https://github.com/SamSchott/maestral). Each entry is written to be
copy-pasteable into the GitHub issue tracker.

> **Note:** the GitHub **Issues** tab is currently disabled on this repository
> (a fork default). Enable it under *Settings → General → Features → Issues* to
> track these items as real issues; until then this file is the backlog.

---

## 1. CI: macOS offline daemon tests fail at startup

**Labels:** `bug` · `ci` · `macos` · `help wanted`

On `macos-latest` runners the offline suite fails because the sync daemon cannot
start. Independent of Python version (reproduced on 3.10 **and** 3.14) and
**macOS-only** — the same tests pass on `ubuntu-latest` at every version.

Failing tests:

```
tests/offline/test_cli.py::test_start_already_running  - assert <Start.Failed: 2> is <Start.Ok: 0>
tests/offline/test_cli.py::test_stop                   - assert <Start.Failed: 2> is <Start.Ok: 0>
tests/offline/test_cli.py::test_notify_level           - Pyro5.errors.CommunicationError: Could not get proxy for 'test-config-0'
tests/offline/test_cli.py::test_notify_snooze          - Pyro5.errors.CommunicationError: Could not get proxy for 'test-config-0'
tests/offline/test_daemon.py::test_lifecycle           - assert <Start.Failed: 2> is <Start.Ok: 0>
tests/offline/test_daemon.py::test_connection          - assert <Start.Failed: 2> is <Start.Ok: 0>
tests/offline/test_daemon.py::test_remote_exceptions   - Pyro5.errors.CommunicationError: Could not get proxy for 'test-config-0'
```

**Mechanism:** `start_maestral_daemon_process()` (`src/maestral/daemon.py`)
spawns the daemon as a separate process via `os.spawnve(... "-c", "import
maestral.daemon; maestral.daemon.start_maestral_daemon(...)")` and then
`wait_for_startup()` polls for 30 s. On macOS the spawned process appears to
crash before binding its Pyro5 unix socket → `Start.Failed`.

**Ruled out:**
- `fork()`-of-multithreaded / Python 3.14 semantics — also fails on 3.10, and
  startup uses `spawnve`, not `fork`.
- Unix socket path length limit (104 bytes on macOS) — the path
  `~/Library/Application Support/maestral/test-config-0.sock` is ≈ 69 chars.

**Likely nature:** environment/runner drift (current `macos-latest` image + newer
deps such as Pyro5 / desktop-notifier), **not** a regression from the fork prep
(Linux is fully green on the same tree).

**Next steps:**
1. Capture the daemon subprocess's own stderr/log — CI only shows the client
   side. Surface the spawned daemon's stderr (or point `setup_logging` at a file
   the job uploads) to get the real traceback.
2. Reproduce on a local macOS machine if available.
3. Fix root cause, or gate/skip the daemon tests on macOS with a tracked reason.

---

## 2. CI: validate the offline matrix Python pin

**Labels:** `ci` · `chore`

The offline test matrix is pinned to `['3.10', '3.13']` in
`.github/workflows/test.yml` (was `['3.10', '3.x']`, which resolved to 3.14).
3.14 is not in the project's supported classifiers. Because the workflow runs on
`pull_request_target`, this matrix is read from the **default branch**, so the
pin was applied on `main` to take effect for PR checks. Revisit and bump to 3.14
once the daemon is validated there (see #1).

---

## 3. Packaging: GUI frontends depend on the upstream `maestral` distribution

**Labels:** `packaging` · `enhancement`

The `[gui]` extra still references upstream `maestral-qt` (Linux) and
`maestral-cocoa` (macOS), which depend on the upstream `maestral` distribution
and can conflict with this fork (distribution renamed to `maestral-gagnant`; the
importable module stays `maestral`). Decide on a fork GUI strategy: fork the
frontends, vendor them, or document headless-only usage. Currently documented as
a caveat in `README.md` and `pyproject.toml`.

---

## 4. Release infra: stand up fork publishing pipelines

**Labels:** `ci` · `packaging`

- `publish.yml` PyPI job is repointed at `maestral-gagnant` but has not been
  exercised; verify trusted publishing / environment config for the fork.
- `docker-hub` job and `dockerhub-repo-description.yml` are disabled
  (`if: ${{ false }}`) — they target the upstream `maestraldbx/maestral` image
  and upstream secrets. Re-enable with a fork DockerHub repo + secrets, or drop.
- `appcast.yml` (Sparkle) is disabled — it checks out the upstream `website`
  branch and uses upstream signing secrets. Re-enable only if the fork ships a
  signed macOS app bundle.

---

## 5. Update check depends on published releases

**Labels:** `chore`

`GITHUB_RELEASES_API` now points at `izo/maestral-gagnant/releases`
(`src/maestral/constants.py`), consumed by `Maestral.check_for_updates()`. The
repo has no releases yet, so `tests/offline/test_main.py::test_check_for_updates`
is skipped when fewer than two releases exist. Cut fork releases (and confirm the
update-check UX) to exercise this path.

---

## 6. Housekeeping: residual upstream references

**Labels:** `chore` · `docs`

Historical links to upstream issues remain in code comments
(`src/maestral/sync.py`, `src/maestral/models.py`) — intentionally kept as valid
references. The `docs/` site config and README still point at some upstream docs
(`maestral.app`, `maestral.readthedocs.io`) where the content is still accurate;
revisit if/when the fork hosts its own docs.
