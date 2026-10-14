"""Network-free end-to-end selection and removal reporting tests."""
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import biweekly_review as r


class ReviewIntegrationTests(unittest.TestCase):
    def test_candidate_report_is_only_an_audit_not_a_release(self):
        old = '||old-ads.example^\n||gone.example^\n'
        latest = '||old-ads.example^\n||guard.example^\n||newad.example^\n||already.example^\n||awa.example^\n||safe.example^\n@@||safe.example^\n'
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            (root / 'Shadowrocket-AdBlock.sgmodule').write_text('DOMAIN-SUFFIX,guard.example,DIRECT\nDOMAIN-SUFFIX,already.example,REJECT\nDOMAIN,gone.example,REJECT\n', encoding='utf-8')
            old_review = {'sources': {'easylist_china': {'head_commit': 'older123'}, 'awa': {}}}
            fresh = {
                'easylist_china': {'repository': 'easylist/easylistchina', 'path': 'easylistchina.txt', 'commit': 'new123', 'blob_sha': 'abc123', 'text': latest},
                'awa': {'repository': 'TG-Twilight/AWAvenue-Ads-Rule', 'path': 'Filters/AWAvenue-Ads-Rule-Surge-RULE-SET.list', 'commit': 'new456', 'blob_sha': 'def456', 'text': 'DOMAIN,awa.example\n'},
                'easylist': {'repository': 'easylist/easylist', 'path': 'easylist/easylist_adservers.txt', 'commit': 'new789', 'blob_sha': 'ghi789', 'text': '||newad.example^\n'},
            }
            with patch.object(r, 'source_at_commit', return_value=old):
                record, rule_text, report = r.summarize(root, '2026-10-14', fresh, Path('2026-10-07.json'), old_review)
            self.assertEqual(record['counts']['upstream_added'], 5)
            self.assertEqual(record['counts']['ready_for_review'], 1)
            self.assertEqual(record['counts']['guard_conflicts'], 1)
            self.assertEqual(record['counts']['source_exception_conflicts'], 1)
            self.assertEqual(record['counts']['already_covered_locally'], 1)
            self.assertEqual(record['counts']['covered_by_awa'], 1)
            self.assertEqual(record['removed_still_rejected_locally'], ['gone.example'])
            self.assertEqual(record['status'], 'review_only_unpublished')
            self.assertIn('DOMAIN-SUFFIX,newad.example', rule_text)
            self.assertNotIn('DOMAIN-SUFFIX,guard.example', rule_text)
            self.assertIn('未发布稳定版', report)

if __name__ == '__main__':
    unittest.main()
