# When Does a Prior Failure Count?
## Research evidence and reproduction record

**Researcher:** Raphael A. La Touche · **Research release:** five-case synthetic study, v0.4 · **October 2026**

This public record brings together the research question, frozen experiment, documented external reproduction and technical review. It is a non-normative study related to the *Agent Conformance Reporting Format v0.1*. It is not a W3C publication or Responsibility Infrastructure conformance assessment.

## Research question

When can recorded evidence of a previous software test failure support a claim about a current check? The study examines the effects of changes in configuration, checker revision, evidence integrity and reference availability, without treating an unverified prior claim as an established historical event.

## Study results

At the [frozen five-case source revision](https://github.com/LaToucheai/prior-run-evidence-v01/tree/98366047dd322b9fe0ea3ef822cf0c410283fe9f), the documented expected results are:

| Check | Outcome |
| --- | --- |
| Five synthetic scenarios | **5/5** expected outcomes |
| Automated unit tests | **23/23** passed |
| SHA-256 manifest checks | **15/15** passed |

These figures describe the **bounded synthetic experiment** and its reproduced execution, not the accuracy of a deployed system or a measure of real-world reliability.

## Technical review and external reproduction

The three contributions below have **different evidence histories**. They should not be conflated or counted as independent implementations.

| Contributor | Documented contribution | Evidence boundary |
| --- | --- | --- |
| **Nicolás Rocchia** | Reproduced the [original three-case public release](https://github.com/LaToucheai/prior-run-evidence-v01/tree/69819ec8501a3e9e56acacefd84dbede91d2948a) (3/3 cases, 7/7 tests, 14/14 hashes); critically reviewed the revisions, including report-binding and leaf-count issues; reproduced the private v0.4 package on Linux x86_64/Python 3.13.16 (5/5 cases, 23/23 tests, 15/15 hashes). See the [study method and revision history](https://github.com/LaToucheai/prior-run-evidence-v01/blob/main/README.md) and [changelog](https://github.com/LaToucheai/prior-run-evidence-v01/blob/main/CHANGELOG.md). | Reproduction and targeted technical criticism of the producer's code; not independent validation of its interpretation. |
| **Yasha Khandelwal** | Reported a separate rerun against the published pinned revision on 24 October 2026, reproducing five expected outcomes, 23 tests and 15 hashes. The report records its own exposure conditions. | Same published implementation; not a new independently written implementation or conformance determination. |
| **Guigui Wang (Correctover — AI Reliability)** | Completed a fresh-clone second-operator rerun on 20 October 2026 using Linux x86_64 and Python 3.13.12 (standard library only). Reported 5/5 cases, 23/23 tests, 15/15 SHA-256 checks. | Read [Guigui's approved attribution and exact scope](https://github.com/LaToucheai/prior-run-evidence-v01/blob/main/REPRODUCTION-RECORD.md). No wider endorsement, certification, audit or W3C approval is implied. |

The pinned experiment and source-file hashes are unchanged by these later supplementary records.

## Reproduce the published experiment

Use the [exact frozen revision](https://github.com/LaToucheai/prior-run-evidence-v01/tree/98366047dd322b9fe0ea3ef822cf0c410283fe9f). From a clean checkout, with Python 3.10 or later and no external dependencies, run:

```sh
python3 experiment.py
python3 -m unittest -v test_experiment.py
sha256sum -c SHA256SUMS
```

The main [study README](https://github.com/LaToucheai/prior-run-evidence-v01/blob/main/README.md) documents the cases, assumptions, technical revisions and limits in detail.

## R13 paper evidence

This study is associated with the R13 evidence row in the [separately maintained reporting-format paper appendix](https://github.com/probityai/agent-evidence-vectors/blob/main/interop/w3c-v01-appendix/README.md). La Touche's [R13 supporting evidence](https://github.com/LaToucheai/prior-run-evidence-v01/blob/main/R13-EVIDENCE.md) includes the exact citation Guigui approved for the paper evidence record. Whether or how the external maintainers incorporate later evidence remains their editorial decision.

**Research boundary:** Reproducing the study's outputs does not establish independent verification of the historical event, scientific peer review, W3C endorsement, Responsibility Infrastructure interoperability or conformance, regulatory approval, or validation of the L-SCAN commercial product.
