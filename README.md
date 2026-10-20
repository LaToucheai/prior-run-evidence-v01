# When Does a Prior Failure Count? — five-case v0.4 reproducible research release

A bounded synthetic experiment about the **prior-run** branch of section 5.4 of the *Agent Conformance Reporting Format v0.1*, originally published by the W3C Agent Conformance and Benchmarking Community Group:
https://lists.w3.org/Archives/Public/public-agent-conformance/2026Sep/0087.html

Research contribution: **Raphael A. La Touche** (ORCID: https://orcid.org/0009-0000-2943-5786). Prepared with AI assistance. This is an **experimental, non-normative study profile**, not a general W3C validator, certification, or official W3C specification.

This public research release incorporates technical feedback from **Nicolás Rocchia** on 17 and 19 October 2026. Nicolás reproduced the original three-case study at immutable public commit [`69819ec`](https://github.com/LaToucheai/prior-run-evidence-v01/commit/69819ec8501a3e9e56acacefd84dbede91d2948a). He separately reproduced the **private v0.2 five-case ZIP** on Linux x86_64 with Python 3.13.16 (5/5 expected results, 15/15 tests, 15/15 hashes), then identified one remaining binding gap: the assessor read the expected digest from a build-step argument and used positional `checks[0]`, rather than the prior reference and check identity declared by the **current** v0.1 report. He also reproduced **v0.3** on Linux x86_64 with Python 3.13.16 (5/5 expected results, 20/20 tests, 15/15 hashes) and confirmed the current-report binding gap was closed for his test. He identified one remaining leaf-count gap: a current report can declare a reference leaf-count of 5 for an envelope containing one check; the pinned reader accepts the current report and the v0.3 assessor incorrectly established the witness. **v0.4** adds a local single-leaf check to prevent that result. Nicolás reran the v0.4 archive as a second operator on Linux x86_64 with Python 3.13.16, confirming 5/5 expected results, 23/23 tests, 15/15 hashes, and refusal of leaf counts 5, 0 and 2. He stated that the specific issues he raised were resolved within the study's declared scope. This remains reproduction and technical review, not independent validation of the study's interpretation.

## Research question

Under a conservative study interpretation, when can a report of an earlier observed failure act as evidence for a current check? How do a resolution failure, an integrity failure, a changed checker revision, and changed relevant constraints differ?

## Five controlled cases

All current fixtures actually execute a synthetic integer-ceiling check with input **5** and return `pass`. All original prior fixtures actually execute the check with input **11** and ceiling **10** and return `fail` using the two pinned source files. Cases A–C maintain the original comparison design: each near miss changes exactly one relevant declared field from A.

| Case | Change relative to A | Local reference status | Local witness decision |
| --- | --- | --- | --- |
| A — valid | None; matching checker source and ceiling | `matched` | `established` under this profile |
| B — configuration drift | Current ceiling becomes 12 instead of 10 | `matched` | `not-established` |
| C — revision drift | Prior checker uses different source digest | `matched` | `not-established` |
| D — integrity mismatch | Resolved JSON bytes differ from pinned SHA-256 (one trailing whitespace byte) | `integrity-failure` | `not-established` |
| E — unresolved reference | The study-local reference resolver supplies no bytes | `unchecked` | `undetermined` |

D and E add **reference-resolution** scenarios rather than new checker-mutation controls. Their input/checker/configuration declarations are otherwise identical to case A. In D, altered bytes are parseable JSON, but the digest no longer matches; in E, no retrieved bytes exist and no integrity comparison is possible. These three reference-state labels are **study-defined illustrations** of the distinction noted in section 3 of the reporting format; they are **not normative W3C statuses**.

## Reproduce

Python 3.10+ standard library; no network connection or dependency installation is needed. From the root of a clean checkout of **the exact revision being reviewed**:

```sh
python3 experiment.py
python3 -m unittest -v test_experiment.py
sha256sum -c SHA256SUMS
```

Expected for v0.4: **5/5** experiment cases, **23/23** unit tests, **15/15** manifest hashes. The command recomputes the synthetic execution fixtures, runs the pinned v0.1 reader on the report structures, applies a separate study-local witness assessment, and byte-compares the output against `results.json`.

## What changed after outside feedback

1. **Source and environment boundary:** Case A works with source digests because the synthetic checker has no compiled binary and no clock-dependent behaviour. Real checkers with binaries or timing dependencies require additional bindings; this experiment does **not** implement or validate such cases.
2. **Unresolved vs integrity mismatch:** Case D now represents a resolved object whose bytes fail the reference digest; E represents an unavailable object. Their outcomes are intentionally distinct and do not collapse into the original generic “not established” response.
3. **Historical replay removed from witness assessment:** The revised `assess()` compares a digest-matched prior declaration and its relevant bindings, but **does not execute** the historical checker. Executions of synthetic prior and current fixtures still take place when *constructing* the experiment. A specific regression test makes assessment fail if it invokes the checker. This separation isolates what the recorded prior-run claim can support, rather than silently requiring extra proof by replay.

4. **The report is the source of the witness claim (v0.3):** `assess(current_report, prior_bytes)` now reads the digest from `current_report['roll-up']['negative-capable']['reference']` and the check identity from that field's `check-identity` list. It first asks the pinned reader to validate the current report. A deliberately wrong identity (`other.check`) is rejected under **W3C-R-014** and can no longer produce a study-level `established` result. The prior report must contain a recorded fail for the identity the current report actually declares, rather than whichever check happens to appear at index zero. The study remains limited to a one-check synthetic example.

5. **Single-leaf reference consistency (v0.4):** Before establishing a matched witness, the study assessor now compares the current report's declared reference `leaf-count` with both the actual number of checks and the check-set leaf count in the resolved prior envelope. This synthetic profile only supports a **single flat leaf**. A declared count of 5 for a one-check prior run now produces `prior-reference-leaf-count-mismatch`, even though the pinned v0.18.1 reader accepts the current report's structure. Regression tests also cover count 0 and preserve the positive count-1 case. The assessor checks the supported flat shape, but this is **not** a normative or general-purpose tree resolver.

See [`CHANGELOG.md`](CHANGELOG.md) for the revision history against the public original commit.

## Claims and limitations

- **Reader acceptance is not historical-event verification.** The current and prior JSON report structures are accepted by the pinned third-party reference reader's `shape_errors()` and `rejections()` checks, but the study's prior-reference *envelope* and `assess()` method are not part of the published v0.1 format. A matching digest binds bytes of that study-specific envelope, not independently observed execution.
- **Removing replay does not confer trust.** A prior `fail` in a digest-matched, reader-accepted report is still a recorded claim. The revised experiment does not prove a historical run occurred outside this controlled synthetic fixture, nor prevent a dishonest party from generating a different self-consistent report and digest.
- **Conservative checker identity:** Cases B and C demonstrate insufficient matching relevant bindings, not behavioral inequality or inability of a current checker to fail. Source revision alone works for this toy check, not every production checker.
- **Reference resolution is simulated:** The D/E resolver is study-local. No network fetch, signature validation, content-addressed registry, W3C normative reference-resolution algorithm, or external authentication is implemented. Section 3 semantics are illustrated, not certified.
- **Current-report binding is now checked:** The assessor reads the reference and the single claimed check identity from the current v0.1 report, refuses reader-invalid current reports, and matches the named check to the prior report. The assessor remains study-specific; it does not establish independently trustworthy provenance or prove the historical run happened.
- **External review is bounded:** Nicolás separately reproduced the original three-case public commit, the private **v0.2** five-case ZIP and **v0.3**, and confirmed the report-binding gap was closed in v0.3 for what he raised. He then identified the leaf-count case addressed locally in v0.4. **Nicolás reproduced the v0.4 package with 5/5 expected results, 23/23 tests and 15/15 hashes, and confirmed that his specific leaf-count concern was resolved; independent validation of the study interpretation has not been established**, and reproduction of earlier versions did not independently validate the study interpretation.
- This work is synthetic and does not establish compliance, correctness of the published specification, security properties, or real-world deployment outcomes.

## Licence and source

The original synthetic experiment files are under the repository [MIT licence](LICENSE), with copyright attributed to La Touche Holdings Ltd to the extent of its rights. The three unmodified third-party reader modules are separately licensed under upstream **Apache-2.0** (see [`vendor/LICENSE`](vendor/LICENSE) and [`THIRD_PARTY_NOTICES.md`](THIRD_PARTY_NOTICES.md)). The source modules and notices have not changed in this revision; no upstream authorship is claimed.

The externally runnable study and published conclusions must remain separate from any unrelated private platform architecture or commercial systems.
