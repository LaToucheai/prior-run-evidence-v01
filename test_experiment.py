import unittest
from experiment import assess, build, canonical, checker, make_observation, sha256

class StudyTests(unittest.TestCase):
    def test_three_comparisons(self):
        self.assertEqual([x['observed']['witness'] for x in build()['cases']],
                         ['established', 'not-established', 'not-established'])

    def test_prior_fail_is_executed(self):
        for rev in ['v1.py', 'v0.py']:
            run = make_observation(11, 10, rev)
            self.assertEqual(run['report']['checks'][0]['state'], 'fail')
            self.assertEqual(checker(rev)[0](11, 10), 'fail')

    def test_current_pass_is_executed(self):
        for ceiling in [10, 12]:
            self.assertEqual(make_observation(5, ceiling, 'v1.py')['report']['checks'][0]['state'], 'pass')

    def test_revisions_are_actual_distinct_files(self):
        self.assertNotEqual(checker('v1.py')[1], checker('v0.py')[1])

    def test_both_reader_checks_are_clean(self):
        for x in build()['cases']:
            self.assertEqual(x['reference_reader'], {'shape_errors': [], 'rejections': []})

    def test_wrong_artifact_digest_is_not_witness(self):
        old = make_observation(11, 10, 'v1.py')
        cur = make_observation(5, 10, 'v1.py')
        self.assertEqual(assess(cur, canonical(old), '0'*64)['reason'], 'digest-mismatch')

    def test_incorrect_fail_claim_is_caught_by_replay(self):
        cur = make_observation(5, 10, 'v1.py')
        old = make_observation(7, 10, 'v1.py')
        old['report']['checks'][0]['state'] = 'fail'
        # Shape/check-set binding left stale: either reader rejection or replay prevents acceptance.
        blob = canonical(old)
        self.assertNotEqual(assess(cur, blob, sha256(blob))['witness'], 'established')

if __name__ == '__main__':
    unittest.main()
