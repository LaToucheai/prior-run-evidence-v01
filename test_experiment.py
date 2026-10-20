"""Local regression tests for the study-specific v0.4 prior-run assessor."""
import json
from unittest import TestCase, main
from unittest.mock import patch
from experiment import (
    assess, attach_prior_claim, build, canonical, checker,
    make_observation, result, sha256, w3creport,
)


def current_report(current, prior_blob):
    """Build the *current report* carrying its own reference and identity."""
    return attach_prior_claim(current, {
        'sha256': sha256(prior_blob), 'leaf-count': 1, 'tree-shape': 'flat'})


class StudyTests(TestCase):
    def test_all_five_comparisons(self):
        self.assertEqual(len(build()['cases']), 5)

    def test_first_three_original_boundaries(self):
        self.assertEqual([x['observed']['witness'] for x in build()['cases'][:3]],
                         ['established', 'not-established', 'not-established'])

    def test_prior_fail_is_executed_to_construct_data(self):
        for revision in ['v1.py', 'v0.py']:
            obs = make_observation(11, 10, revision)
            self.assertEqual(obs['report']['checks'][0]['state'], 'fail')
            self.assertEqual(checker(revision)[0](11, 10), 'fail')

    def test_current_pass_is_executed_to_construct_data(self):
        for ceiling in [10, 12]:
            self.assertEqual(make_observation(5, ceiling, 'v1.py')['report']['checks'][0]['state'], 'pass')

    def test_revisions_are_distinct_real_files(self):
        self.assertNotEqual(checker('v1.py')[1], checker('v0.py')[1])

    def test_reference_reader_accepts_all_current_reports(self):
        for case in build()['cases']:
            self.assertEqual(case['reference_reader'], {'shape_errors': [], 'rejections': []})

    def test_matching_reference_is_distinct_from_witness(self):
        cases = build()['cases']
        self.assertEqual([x['observed']['reference_status'] for x in cases[:3]], ['matched'] * 3)
        self.assertNotEqual(cases[1]['observed']['witness'], cases[0]['observed']['witness'])

    def test_mismatched_digest_is_integrity_failure(self):
        old = make_observation(11, 10, 'v1.py')
        current = make_observation(5, 10, 'v1.py')
        blob = canonical(old)
        self.assertEqual(assess(current_report(current, blob), blob + b' '),
                         result('integrity-failure', 'not-established', 'digest-mismatch'))

    def test_missing_reference_is_unchecked_not_integrity_failure(self):
        old = make_observation(11, 10, 'v1.py')
        current = make_observation(5, 10, 'v1.py')
        self.assertEqual(assess(current_report(current, canonical(old)), None),
                         result('unchecked', 'undetermined', 'unresolved-prior-reference'))

    def test_resolved_mismatch_vs_unresolved_are_separate_cases(self):
        d, e = build()['cases'][3:]
        self.assertNotEqual(d['observed']['reference_status'], e['observed']['reference_status'])
        self.assertIsNotNone(d['resolved_bytes_sha256'])
        self.assertIsNone(e['resolved_bytes_sha256'])

    def test_assessor_does_not_replay_checker(self):
        old = make_observation(11, 10, 'v1.py')
        current = make_observation(5, 10, 'v1.py')
        blob = canonical(old)
        with patch('experiment.checker', side_effect=AssertionError('replay called')):
            x = assess(current_report(current, blob), blob)
        self.assertEqual(x, result('matched', 'established', 'matching-binding-and-recorded-fail'))

    def test_tampered_report_state_with_stale_check_root_is_rejected(self):
        old = make_observation(7, 10, 'v1.py')
        current = make_observation(5, 10, 'v1.py')
        old['report']['checks'][0]['state'] = 'fail'
        blob = canonical(old)
        self.assertNotEqual(assess(current_report(current, blob), blob)['witness'], 'established')

    def test_other_prior_check_without_fail_is_not_witness(self):
        old = make_observation(5, 10, 'v1.py')
        current = make_observation(5, 10, 'v1.py')
        blob = canonical(old)
        self.assertEqual(assess(current_report(current, blob), blob)['reason'], 'no-declared-prior-fail')

    def test_configuration_difference_is_nonqualifying(self):
        old = make_observation(11, 10, 'v1.py')
        current = make_observation(5, 12, 'v1.py')
        blob = canonical(old)
        self.assertEqual(assess(current_report(current, blob), blob)['reason'], 'configuration-mismatch')

    def test_revision_difference_is_nonqualifying(self):
        old = make_observation(11, 10, 'v0.py')
        current = make_observation(5, 10, 'v1.py')
        blob = canonical(old)
        self.assertEqual(assess(current_report(current, blob), blob)['reason'], 'checker-revision-mismatch')

    def test_wrong_declared_check_identity_never_establishes_witness(self):
        """Nicolás's precise regression: report rejects under W3C-R-014."""
        old = make_observation(11, 10, 'v1.py')
        current = make_observation(5, 10, 'v1.py')
        blob = canonical(old)
        report = current_report(current, blob)
        report['roll-up']['negative-capable']['check-identity'] = ['other.check']
        self.assertIn('W3C-R-014', w3creport.rejections(report))
        self.assertEqual(assess(report, blob),
                         result('not-evaluated', 'not-established', 'invalid-current-report'))

    def test_reference_digest_is_read_from_current_report(self):
        old = make_observation(11, 10, 'v1.py')
        current = make_observation(5, 10, 'v1.py')
        blob = canonical(old)
        report = current_report(current, blob)
        report['roll-up']['negative-capable']['reference']['sha256'] = '0' * 64
        self.assertEqual(assess(report, blob),
                         result('integrity-failure', 'not-established', 'digest-mismatch'))

    def test_reference_missing_from_current_report_is_not_inferred(self):
        old = make_observation(11, 10, 'v1.py')
        current = make_observation(5, 10, 'v1.py')
        blob = canonical(old)
        report = current_report(current, blob)
        del report['roll-up']['negative-capable']['reference']
        self.assertEqual(assess(report, blob),
                         result('not-evaluated', 'not-established', 'invalid-current-report'))

    def test_missing_prior_run_claim_not_inferred_from_observation(self):
        current = make_observation(5, 10, 'v1.py')
        old = make_observation(11, 10, 'v1.py')
        self.assertEqual(assess(current['report'], canonical(old)),
                         result('not-evaluated', 'not-established', 'not-a-prior-run-claim'))

    def test_nicolas_leaf_count_five_is_not_a_witness_even_if_reader_accepts(self):
        """A digest match cannot override an inaccurate declared leaf count."""
        old = make_observation(11, 10, 'v1.py')
        current = make_observation(5, 10, 'v1.py')
        blob = canonical(old)
        report = current_report(current, blob)
        report['roll-up']['negative-capable']['reference']['leaf-count'] = 5
        # Precisely the v0.3 hole: the pinned reader accepts this report.
        self.assertEqual(w3creport.shape_errors(report), [])
        self.assertEqual(w3creport.rejections(report), [])
        self.assertEqual(assess(report, blob), result(
            'matched', 'not-established', 'prior-reference-leaf-count-mismatch'))

    def test_reference_leaf_count_zero_is_not_a_witness(self):
        old = make_observation(11, 10, 'v1.py')
        current = make_observation(5, 10, 'v1.py')
        blob = canonical(old)
        report = current_report(current, blob)
        report['roll-up']['negative-capable']['reference']['leaf-count'] = 0
        self.assertNotEqual(assess(report, blob)['witness'], 'established')

    def test_matching_single_flat_reference_is_still_established(self):
        old = make_observation(11, 10, 'v1.py')
        current = make_observation(5, 10, 'v1.py')
        blob = canonical(old)
        self.assertEqual(assess(current_report(current, blob), blob),
                         result('matched', 'established', 'matching-binding-and-recorded-fail'))

    def test_prior_envelope_configuration_must_bind_to_report(self):
        old = make_observation(11, 10, 'v1.py')
        current = make_observation(5, 10, 'v1.py')
        old['configuration']['ceiling'] = 12  # Report still declares digest of 10.
        blob = canonical(old)
        self.assertEqual(assess(current_report(current, blob), blob),
                         result('matched', 'not-established', 'prior-configuration-binding-mismatch'))


if __name__ == '__main__':
    main()
