# Experiment revisions

## v0.4 — public single-leaf reference check, 20 October 2026

**Baseline:** Nicolás reproduced the v0.3 ZIP, confirming 5/5 expected results, 20/20 tests, and 15/15 file hashes on Linux x86_64 / Python 3.13.16. He confirmed his earlier current-report-binding gap was closed, but found that a reference with `leaf-count: 5` could still establish a witness for a single-check resolved envelope even though the reference reader accepted its report structure.

**Fix:** The study assessor now compares the declared reference leaf count against the number of resolved prior checks and the resolved prior report’s declared check-set leaf count; exactly **one** is supported in this synthetic profile. The flat tree shape is also checked against the resolved prior report’s declared flat shape. Mismatch cannot yield `established`. This is an experimental single-leaf consistency test, **not** validation of general multi-leaf trees.

**Regressions:** Explicit test that `leaf-count: 5` (accepted by the pinned reader) is refused by the study assessor; test for count 0; preserve the positive single-flat-leaf case. Total: 23 unit tests.

**Unchanged:** Original A–E expected outcomes and byte-identical `results.json`; no historical replay; existing checker source, third-party reader and licence files; public v0.1 repository. **External review:** Nicolás reproduced the private v0.4 ZIP on Linux x86_64 / Python 3.13.16: 5/5 results, 23/23 tests, 15/15 SHA256SUMS. He separately challenged leaf counts 5, 0 and 2 and found the assessor returned `not-established` while the positive single-leaf and invalid-current-report cases remained as expected. He said the specific concerns he raised were closed within the stated scope and recommended a public commit and an additional rerun by another person. This does not amount to independent semantic validation.

---

## v0.3 — private report-binding correction, 19 October 2026

**Baseline:** Nicolás's reproduced private v0.2 ZIP (SHA-256 `953da35399a51d390e5b0193ad06bedab230ebaf59a42cb75ec3f8a2d6dcf47b`). Nicolas confirmed 5/5 cases, 15/15 tests and 15/15 manifest hashes, then observed that `assess()` took its digest from the build step and its check identity from positional `checks[0]` instead of the current v0.1 report's negative-capable field.

**Fix:** `assess(current_report, prior_bytes)` now obtains the digest and one check identity exclusively from the current report's `roll-up.negative-capable` declaration, first validates the current report with the vendored v0.18.1 reader, and looks up the named check in both reports. A report containing `other.check` is rejected under W3C-R-014 rather than being treated as established. Additional tests verify wrong identity, changed reference digest, missing declaration and a mismatched prior-envelope configuration.

**Unchanged:** Five study-specific expected outcomes; original public three-case commit; checker source files; vendored reader files; licences. Historical checker replay remains absent in assessment. `results.json` is still byte-identical to v0.2's deterministic output; changed source and test hashes are recorded in the new manifest.

**Local reproduction:** 5/5 expected cases, 20/20 tests and 15/15 hashes. **Not yet externally rerun.** The study's local labels are not normative W3C decisions, and successful reader acceptance does not authenticate a historical event.

---

## v0.2 — review candidate, 17 October 2026

**Baseline:** Public original commit `69819ec8501a3e9e56acacefd84dbede91d2948a`, three cases, seven unit tests and fourteen SHA-256 manifest entries.

**Motivation:** Nicolás Rocchia reproduced that original commit as another operator on Linux x86_64 with Python 3.13.16 and described three improvements: make checker source/binary/clock limits explicit; distinguish reference-resolution statuses; avoid treating prior replay as an extra normative requirement for the historical-witness route.

**Bounded changes:**

- Preserve A/B/C's original one-change boundaries while making reference status explicit.
- Add D: parseable bytes failing pinned SHA-256 -> `integrity-failure`.
- Add E: prior reference is unavailable -> `unchecked`, `undetermined` (distinct from an observed failure to match).
- Replace the study's replay-dependent positive witness test with a no-replay assessment. Synthetic runs *are still executed* to construct input records; external truth of the recorded `fail` is not established.
- Add test showing an assessment can run while the local checker invocation is disabled.
- Expand tests and regenerate `results.json` and the content-hash manifest.

**Not changed:** checker source files, prior/current v0.1 schema construction, third-party vendored reader, MIT and Apache-2.0 notices, original immutable public commit. No new RI implementation, business methods or confidential data are introduced.

**Status:** Author-local reproduction only; not yet externally rerun or accepted into a W3C paper. The change is a suggested empirical clarification and **not** a normative interpretation.
