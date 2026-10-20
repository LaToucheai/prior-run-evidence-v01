#!/usr/bin/env python3
"""Five synthetic comparisons for section 5.4 prior-run evidence (v0.4).

A bounded experimental profile, NOT an independent or normative W3C resolver.
The synthetic checker is executed to *produce* the fixture reports, but the
study assessor does not replay the checker while resolving historical evidence.
"""
import hashlib
import importlib.util
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / 'vendor'))
from agent_evidence_vectors import w3creport

CHECK_ID = 'synthetic.integer-ceiling'
DOMAIN = {'id': 'integer-example', 'description': 'one synthetic integer input'}


def canonical(value):
    """Deterministic local-envelope encoding; NOT RFC 8785."""
    return (json.dumps(value, sort_keys=True, indent=2, ensure_ascii=True) + '\n').encode('utf-8')


def sha256(blob):
    return hashlib.sha256(blob).hexdigest()


def checker(revision):
    source = ROOT / 'checkers' / revision
    spec = importlib.util.spec_from_file_location('toy_checker', source)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.check, 'sha256:' + sha256(source.read_bytes())


def make_observation(value, ceiling, revision):
    execute, rev = checker(revision)
    state = execute(value, ceiling)  # Actual execution to construct a synthetic prior/current fixture.
    check = {'check': CHECK_ID, 'state': state,
             'other-verdict': {'value': 'unknown'}, 'discrimination': {'value': 'unknown'}}
    counts = {s: int(state == s) for s in w3creport.STATES}
    counts.update({'declared': 1, 'exercised': 1, 'carried': 0, 'referenced': 0})
    counts['negative-capable'] = {'kind': 'shown-by-run' if state == 'fail' else 'nothing'}
    report = {
        'format': w3creport.FORMAT, 'domain': DOMAIN,
        'fixed': {'checker': rev, 'constraint-set': 'sha256:' + sha256(canonical({'ceiling': ceiling}))},
        'checks': [check], 'evidence': [], 'roll-up': counts,
        'check-set': {'sha256': w3creport.check_set_root([check], 'flat'),
                      'leaf-count': 1, 'tree-shape': 'flat'}
    }
    errors = w3creport.shape_errors(report)
    rejected = [] if errors else w3creport.rejections(report)
    if errors or rejected:
        raise AssertionError(f'pinned reader refused actual observation: {errors}; {rejected}')
    return {'input': value, 'configuration': {'ceiling': ceiling}, 'checker_source': revision,
            'report': report}


def result(reference_status, witness, reason):
    """Study-local result fields, not a W3C normative status vocabulary."""
    return {'reference_status': reference_status, 'witness': witness, 'reason': reason}


def attach_prior_claim(observation, reference):
    """Declare the prior witness in the current v0.1 report, not a side channel."""
    report = json.loads(json.dumps(observation['report']))
    report['roll-up']['negative-capable'] = {
        'kind': 'prior-discriminating-run',
        'reference': reference,
        'check-identity': [CHECK_ID],
    }
    return report


def assess(current_report, prior_bytes):
    """Study-local assessor, reading the current report's *declared* prior claim.

    No historical replay, normative resolution, or external-event attestation.
    A synthetic single-check report is the bounded scope of this study.
    """
    if not isinstance(current_report, dict):
        return result('not-evaluated', 'not-established', 'invalid-current-report')
    if (w3creport.shape_errors(current_report) or
            w3creport.rejections(current_report)):
        return result('not-evaluated', 'not-established', 'invalid-current-report')
    field = current_report['roll-up']['negative-capable']
    if field.get('kind') != 'prior-discriminating-run':
        return result('not-evaluated', 'not-established', 'not-a-prior-run-claim')
    # v0.1 permits a list of check identities; this experiment is deliberately
    # single-check, so never infer a positive witness for a multi-check report.
    check_ids = field.get('check-identity')
    if not isinstance(check_ids, list) or len(check_ids) != 1:
        return result('not-evaluated', 'not-established', 'unsupported-check-identity-scope')
    check_id = check_ids[0]
    reference = field['reference']
    expected_digest = reference['sha256']

    if prior_bytes is None:
        return result('unchecked', 'undetermined', 'unresolved-prior-reference')
    if sha256(prior_bytes) != expected_digest:
        return result('integrity-failure', 'not-established', 'digest-mismatch')
    try:
        prior = json.loads(prior_bytes)
        old = prior['report']
    except (ValueError, TypeError, KeyError):
        return result('matched', 'not-established', 'unreadable-prior-envelope')
    if w3creport.shape_errors(old) or w3creport.rejections(old):
        return result('matched', 'not-established', 'invalid-prior-report')

    # A matching envelope digest identifies bytes but does not prove that
    # the reference's declared tree parameters describe those resolved bytes.
    # This small experimental profile supports exactly ONE flat check, not a
    # general multi-leaf resolver. Compare the declared reference against the
    # resolved prior report before allowing a positive witness.
    if (reference.get('leaf-count') != 1 or len(old['checks']) != 1 or
            old['check-set']['leaf-count'] != 1):
        return result('matched', 'not-established', 'prior-reference-leaf-count-mismatch')
    if (reference.get('tree-shape') != 'flat' or
            old['check-set']['tree-shape'] != 'flat'):
        return result('matched', 'not-established', 'unsupported-prior-reference-tree-shape')

    # The compared check is the one identified in the *current report's*
    # negative-capable field, never a positional checks[0] assumption.
    cur_checks = {check['check']: check for check in current_report['checks']}
    old_checks = {check['check']: check for check in old['checks']}
    if check_id not in cur_checks or check_id not in old_checks:
        return result('matched', 'not-established', 'check-identity-mismatch')
    if current_report['fixed']['checker'] != old['fixed']['checker']:
        return result('matched', 'not-established', 'checker-revision-mismatch')
    if current_report['fixed']['constraint-set'] != old['fixed']['constraint-set']:
        return result('matched', 'not-established', 'configuration-mismatch')
    # The study-specific prior envelope contains its plain configuration;
    # establish that it agrees with the digest the prior report declares.
    # A malformed but digest-matched envelope must not crash or establish a witness.
    if not isinstance(prior.get('configuration'), dict):
        return result('matched', 'not-established', 'prior-configuration-binding-mismatch')
    if old['fixed']['constraint-set'] != 'sha256:' + sha256(canonical(prior['configuration'])):
        return result('matched', 'not-established', 'prior-configuration-binding-mismatch')
    if current_report['domain'] != old['domain']:
        return result('matched', 'not-established', 'domain-mismatch')
    if old_checks[check_id]['state'] != 'fail':
        return result('matched', 'not-established', 'no-declared-prior-fail')
    # This is only a reader-accepted recorded assertion, not authenticated
    # historical execution; deliberately no checker replay here.
    return result('matched', 'established', 'matching-binding-and-recorded-fail')

def build():
    specs = [
        # case, current ceiling, current checker, prior checker, resolution scenario, expected result
        ('A-valid', 10, 'v1.py', 'v1.py', 'resolved',
         result('matched', 'established', 'matching-binding-and-recorded-fail')),
        ('B-configuration-drift', 12, 'v1.py', 'v1.py', 'resolved',
         result('matched', 'not-established', 'configuration-mismatch')),
        ('C-revision-drift', 10, 'v1.py', 'v0.py', 'resolved',
         result('matched', 'not-established', 'checker-revision-mismatch')),
        ('D-integrity-mismatch', 10, 'v1.py', 'v1.py', 'altered-bytes',
         result('integrity-failure', 'not-established', 'digest-mismatch')),
        ('E-unresolved-reference', 10, 'v1.py', 'v1.py', 'unavailable',
         result('unchecked', 'undetermined', 'unresolved-prior-reference')),
    ]
    cases = []
    for ident, current_ceiling, current_source, prior_source, resolution, expected in specs:
        current = make_observation(5, current_ceiling, current_source)
        prior = make_observation(11, 10, prior_source)
        prior_blob = canonical(prior)
        reference = {'sha256': sha256(prior_blob), 'leaf-count': 1, 'tree-shape': 'flat'}
        current_report = attach_prior_claim(current, reference)
        errors = w3creport.shape_errors(current_report)
        rejected = [] if errors else w3creport.rejections(current_report)
        if errors or rejected:
            raise AssertionError(f'current report refused: {errors}; {rejected}')
        # Case D preserves parseable JSON but changes reference bytes.
        resolved_bytes = (prior_blob if resolution == 'resolved' else
                          prior_blob + b' ' if resolution == 'altered-bytes' else None)
        observed = assess(current_report, resolved_bytes)
        if observed != expected:
            raise AssertionError(f'{ident}: unexpected result {observed}')
        cases.append({
            'case': ident, 'current_input': 5, 'prior_input': 11,
            'current_ceiling': current_ceiling, 'prior_ceiling': 10,
            'current_checker_source': current_source, 'prior_checker_source': prior_source,
            'prior_report': prior, 'prior_reference': reference,
            'reference_resolution_scenario': resolution,
            'resolved_bytes_sha256': sha256(resolved_bytes) if resolved_bytes is not None else None,
            'current_v01_report': current_report,
            'reference_reader': {'shape_errors': errors, 'rejections': rejected},
            'observed': observed,
        })
    return {'experiment': 'prior-run-five-controlled-comparisons',
            'assessor_profile': 'synthetic-non-normative-no-replay', 'cases': cases}


def main():
    payload = canonical(build())
    expected = (ROOT / 'results.json').read_bytes()
    if payload != expected:
        raise SystemExit('MISMATCH: produced bytes do not match results.json')
    for case in json.loads(payload)['cases']:
        x = case['observed']
        print(f"{case['case']}: {x['reference_status']} / {x['witness']} ({x['reason']})")
    print('5/5 local expectations matched; reference reader accepted all five current report structures')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
