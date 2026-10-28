# Recovery verification — 28 October 2026

**Repository:** `LaToucheai/prior-run-evidence-v01`  
**Purpose:** Verify that the full five-case v0.4 study remains reproducible after source restoration and the correction of one stale README checksum.  
**Verification status:** **PASS**, within the bounded experiment's documented scope.

## Exact source and environment

- `main` checksum-correction commit before adding this record: [`41f4bef4d2a9157b6d5209d62222acb0bae16d61`](https://github.com/LaToucheai/prior-run-evidence-v01/commit/41f4bef4d2a9157b6d5209d62222acb0bae16d61).
- The checksum fix edited **only `SHA256SUMS`**: `README.md` SHA-256 changed from `3cfa7068c12bc0530fbadc82ed4c8cb051f5de8e354ca06fad57ae7e87cfc588` to `930829cd47d0e983d34e3b8623ab1424038e40b87ecc797786f110eed889d13c`; no experimental source, tests, results or README contents were changed.
- Tested clean-checkout commit: [`3839267fb88d4bc3dbe604a416208c7922663965`](https://github.com/LaToucheai/prior-run-evidence-v01/commit/3839267fb88d4bc3dbe604a416208c7922663965), on temporary `audit/clean-checkout-verification-20261028` branch.
- The branch differs from the checksum-corrected `main` commit by **one added test workflow file only**, `.github/workflows/verify-prior-run-recovery.yml`. All study materials, including `SHA256SUMS`, are identical to corrected `main`.
- Environment: GitHub-hosted `ubuntu-latest` runner, Python **3.13.16**, `actions/checkout@v4`, `actions/setup-python@v5`. Repository checked out afresh; no installed third-party Python dependencies required.

## Executed commands and results

| Command | Observed result |
| --- | --- |
| `python3 experiment.py` | **PASS** — `5/5 local expectations matched; reference reader accepted all five current report structures` |
| `python3 -m unittest -v test_experiment.py` | **PASS** — `Ran 23 tests`, `OK` |
| `sha256sum -c SHA256SUMS` | **PASS** — all **15 of 15** tracked files reported `OK`, including the corrected `README.md` |
| `test -z "$(git status --porcelain)"` | **PASS** — no tracked or untracked changes after running the experiment and tests |

**Independent run records (same checked source):**
- [GitHub Actions push verification, run 40688051682](https://github.com/LaToucheai/prior-run-evidence-v01/actions/runs/40688051682), job `122815434916` — **completed, success**, 28 October 2026 12:28 UTC.
- [GitHub Actions pull request verification, run 40688067984](https://github.com/LaToucheai/prior-run-evidence-v01/actions/runs/40688067984), job `122815490686` — **completed, success**, 28 October 2026 12:28 UTC.

The two runs execute the same test code in separate GitHub Actions jobs; **they are not independent implementations or independent scientific validation**. The pull-request run uses GitHub's temporary merge checkout; the push run checks out the audit branch directly.

## Publication-branch and history checks

- Default branch remains **`main`**. No merge of the audit verification workflow into `main` is authorised or required.
- `published-record` remains a separate reading-copy branch, with head `a2ebb908a82f1954e5091e881ad9816351a58df5`.
- Both the earlier reading-copy commit `c63921f9db159e042db4a3a35156d1cc11c7ee42` and `a2ebb908a82f1954e5091e881ad9816351a58df5` are present in the `published-record` branch history, **not merged into `main`**.
- Original three-case release `69819ec8501a3e9e56acacefd84dbede91d2948a` and original five-case v0.4 frozen release `98366047dd322b9fe0ea3ef822cf0c410283fe9f` remain reachable in `main` history and unchanged.
- The original v0.4 frozen source/test/result/vendored file Git blobs match the current technical files. The current `README.md` contains a subsequent attribution clarification, now accurately reflected in the corrected `SHA256SUMS`.

## Evidential scope and limits

This is **operational reproducibility of a bounded synthetic experiment**, not confirmation that a historical event happened, independent validation of the interpretation, W3C approval, formal RI conformance, L-SCAN product validation, security certification or commercial deployment readiness.

This dated supplementary record is *outside* the 15-file v0.4 checksum manifest; its creation intentionally does not revise the frozen experiment or rehash original research materials.

**Audit workflow location:** [draft audit-only PR #5](https://github.com/LaToucheai/prior-run-evidence-v01/pull/5), to be closed unmerged after verification. The audit branch may remain as a traceable technical record but is not the default public entry point.
