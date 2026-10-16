#!/usr/bin/env python3
"""Three synthetic comparisons of the existing section 5.4 prior-run rule.

This is an experimental one-check profile, NOT an independent W3C validator.
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
    """Local deterministic envelope encoding, not RFC 8785."""
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
    state = execute(value, ceiling)  # Actual checker execution, not a stated expected outcome.
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


def assess(current, prior_bytes, expected_digest):
    if sha256(prior_bytes) != expected_digest:
        return {'witness': 'not-established', 'reason': 'digest-mismatch'}
    prior = json.loads(prior_bytes)
    cur, old = current['report'], prior['report']
    if w3creport.shape_errors(old) or w3creport.rejections(old):
        return {'witness': 'not-established', 'reason': 'invalid-prior-report'}
    if cur['checks'][0]['check'] != old['checks'][0]['check']:
        return {'witness': 'not-established', 'reason': 'check-identity-mismatch'}
    if cur['fixed']['checker'] != old['fixed']['checker']:
        return {'witness': 'not-established', 'reason': 'checker-revision-mismatch'}
    if current['configuration'] != prior['configuration'] or cur['fixed']['constraint-set'] != old['fixed']['constraint-set']:
        return {'witness': 'not-established', 'reason': 'configuration-mismatch'}
    if cur['domain'] != old['domain']:
        return {'witness': 'not-established', 'reason': 'domain-mismatch'}
    if old['checks'][0]['state'] != 'fail':
        return {'witness': 'not-established', 'reason': 'no-observed-prior-fail'}
    execute, revision = checker(prior['checker_source'])
    if revision != old['fixed']['checker'] or execute(prior['input'], prior['configuration']['ceiling']) != 'fail':
        return {'witness': 'not-established', 'reason': 'prior-replay-failed'}
    return {'witness': 'established', 'reason': 'matching-binding-and-observed-fail'}


def build():
    specs = [
        # ID, current ceiling, current source, prior source, expected witness, reason
        ('A-valid', 10, 'v1.py', 'v1.py', 'established', 'matching-binding-and-observed-fail'),
        ('B-configuration-drift', 12, 'v1.py', 'v1.py', 'not-established', 'configuration-mismatch'),
        ('C-revision-drift', 10, 'v1.py', 'v0.py', 'not-established', 'checker-revision-mismatch'),
    ]
    cases = []
    for ident, current_ceiling, current_source, prior_source, expected, expected_reason in specs:
        current = make_observation(5, current_ceiling, current_source)
        prior = make_observation(11, 10, prior_source)
        prior_blob = canonical(prior)
        reference = {'sha256': sha256(prior_blob), 'leaf-count': 1, 'tree-shape': 'flat'}
        # The report is a v0.1 declaration, but resolution/replay is separately checked by study.
        current_report = json.loads(json.dumps(current['report']))
        current_report['roll-up']['negative-capable'] = {
            'kind': 'prior-discriminating-run', 'reference': reference, 'check-identity': [CHECK_ID]}
        errors = w3creport.shape_errors(current_report)
        rejected = [] if errors else w3creport.rejections(current_report)
        if errors or rejected:
            raise AssertionError(f'current report refused: {errors}; {rejected}')
        observed = assess(current, prior_blob, reference['sha256'])
        if observed != {'witness': expected, 'reason': expected_reason}:
            raise AssertionError(f'{ident}: unexpected outcome {observed}')
        cases.append({
            'case': ident, 'current_input': 5, 'prior_input': 11,
            'current_ceiling': current_ceiling, 'prior_ceiling': 10,
            'current_checker_source': current_source, 'prior_checker_source': prior_source,
            'prior_report': prior, 'prior_reference': reference,
            'current_v01_report': current_report,
            'reference_reader': {'shape_errors': errors, 'rejections': rejected},
            'observed': observed,
        })
    return {'experiment': 'prior-run-three-controlled-comparisons', 'cases': cases}


def main():
    result = canonical(build())
    expected = (ROOT / 'results.json').read_bytes()
    if result != expected:
        raise SystemExit('MISMATCH: produced bytes do not match results.json')
    for case in json.loads(result)['cases']:
        print(case['case'] + ': ' + case['observed']['witness'] + ' (' + case['observed']['reason'] + ')')
    print('3/3 local expectations matched; reference reader accepted all three current report structures')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
