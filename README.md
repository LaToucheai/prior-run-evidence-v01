# When Does a Prior Failure Count?

A bounded, synthetic experiment illustrating the **prior-run** branch of section 5.4 of the *Agent Conformance Reporting Format v0.1*, published in the W3C Agent Conformance and Benchmarking Community Group archive on 30 September 2026:
https://lists.w3.org/Archives/Public/public-agent-conformance/2026Sep/0087.html

Research contribution: **Raphael A. La Touche** (ORCID: https://orcid.org/0009-0000-2943-5786). Prepared with AI assistance, with results verified locally. This is an experimental study, not a W3C standard or an independently reviewed result.

## Question

When a current report has only a passing check, does a prior observed fail establish a witness for that check when checker identity, revision and relevant configuration are taken into account?

## Three controlled comparisons

All current runs actually execute an integer-ceiling check with input **5** and return `pass`. All prior runs actually execute a check with input **11** and ceiling **10** and return `fail`. A source-file digest distinguishes the separately implemented checker revisions. There are no real-world data, clocks, network calls or external dependencies beyond the bundled reference reader.

| Case | Current threshold | Prior threshold | Current vs prior source | Expected prior-witness conclusion |
|---|---:|---:|---|---|
| A — valid witness | 10 | 10 | Same source revision | Established in this study profile |
| B — configuration drift | 12 | 10 | Same source revision | Not established: relevant configuration differs |
| C — revision drift | 10 | 10 | Different source revisions | Not established: checker revision differs |

Only **one declared relevant variable** changes from A to B or from A to C. The historical `fail` remains an observed result in each case. In B, input 11 would pass under the current threshold of 12; this does **not** prove that the current checker is unable to fail for other inputs. C uses two distinct pinned source files with equivalent logic, demonstrating the conservative revision-identity requirement rather than proving that their behaviours are different.

## Reproduce

Requires Python 3.10+ standard library. From the root of a clean checkout, with network disabled if desired:

```sh
python3 experiment.py
python3 -m unittest -v test_experiment.py
sha256sum -c SHA256SUMS
```

The first command re-executes the checker, assembles all three current and prior reports, verifies current report structure with the **pinned third-party v0.1 reader**, evaluates the study's separate reference/replay predicate, and byte-compares the generated results with `results.json`. The second executes seven regression tests. The third checks the tracked file digests. There is no package installation.

## Precisely what is, and is not, validated

`current_v01_report` contains report-shaped JSON accepted by the vendored reader's `shape_errors` and `rejections` checks, pinned to agent-evidence-vectors **v0.18.1**, source commit `33d545104ff2f8c124cff465c96c013eeb809156`. It is a third-party *reference reader*, not independently written by the study author. Each prior report is validated too.

`prior_reference` is an SHA-256 digest of a study-specific JSON envelope containing the prior observation and its synthetic input/configuration. That **envelope and the study's `assess()` function are not part of the v0.1 schema**, do not purport to be a general v0.1 prior-run resolver, and do not add any normative rejection code. The reported `established` / `not-established` outcomes are **experiment-local interpretations** of the stated section 5.4 boundary. Acceptance of the report-shaped JSON by the reference reader is a different claim from acceptance of its historical witness.

All fixed source-revision and constraint digests identify actual source/configuration bytes; the local report-envelope hash uses a documented deterministic Python `json.dumps` encoding, **not RFC 8785**. We do not claim trusted execution or independent evidence of what any externally operated checker did.

## Falsifiability, independence, and limits

- If the frozen v0.1 text allows a changed checker revision or relevant configuration to count as the same effective prior witness without further justification, this study's interpretation should be rejected or revised.
- Matching the expected outcomes is a **local self-test**, not independent confirmation. No independent reviewer has checked the interpretation, the code or the chosen negative cases.
- The checker and witness assessor were prepared for this study; their correctness and the broader security of the v0.1 format have not been established.
- The same simple numerical rule in the two source files is intentional. A revision mismatch does not demonstrate different behaviour; it shows only that revision identity is no longer established.
- The study does not test conformance of arbitrary implementations, authentic production evidence, semantic equivalence of configurations, digital signatures, membership proofs or adversarial runners.
- A matching artifact digest establishes which prior bytes were obtained, but not by itself that the prior run bears on the current declaration.

## Licence

The original synthetic experiment materials in this repository are available under the [MIT License](LICENSE), with copyright attributed to La Touche Holdings Ltd. The bundled third-party reference reader is **not** covered by that MIT grant: its three source modules remain under the upstream Apache License 2.0 in [`vendor/LICENSE`](vendor/LICENSE). See [`THIRD_PARTY_NOTICES.md`](THIRD_PARTY_NOTICES.md).

## Source and attribution

The bundled `vendor/agent_evidence_vectors/` reader modules are **unmodified third-party material**, originally published by Probity under Apache-2.0. See `vendor/LICENSE` and `THIRD_PARTY_NOTICES.md` for attribution. No upstream authorship is claimed.

Original research materials and the separately licensed third-party reader are identified in `LICENSE`, `THIRD_PARTY_NOTICES.md` and `vendor/LICENSE`.

Suggested independent-review task: rerun unchanged inputs from an immutable commit and separately assess whether the two near-misses are correctly interpreted under the frozen section 5.4 text. Reproducing the bytes is not an independent validation of the interpretation.
