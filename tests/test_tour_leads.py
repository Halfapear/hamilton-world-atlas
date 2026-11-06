"""v1.2 source-confidence and canonical data contract."""
import json
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]

class TourLeadTests(unittest.TestCase):
    def setUp(self):
        self.data = json.loads((ROOT / 'data/hamilton-world.json').read_text(encoding='utf-8'))

    def test_leads_are_separate_not_bookable(self):
        leads = self.data.get('tourLeads', [])
        self.assertEqual(len(leads), 7, '7 unconfirmed leads required')
        self.assertEqual(len(self.data['stops']), 22)
        official = {s['id'] for s in self.data['stops']}
        self.assertEqual(len({s['id'] for s in leads}), 7)
        for lead in leads:
            self.assertNotIn(lead['id'], official)
            self.assertEqual(lead['evidenceLevel'], '用户提供摘要')
            self.assertIsNone(lead['verifiedAt'])
            self.assertEqual(lead['coordinateKind'], '城市中心')
            self.assertTrue(lead['sources'])
            self.assertTrue(lead['verificationStatus'])
            self.assertTrue(lead['dateText'])
            for forbidden in ('bookingUrl','prices','ticketOpen','startDate','endDate'):
                self.assertNotIn(forbidden, lead)
            for source in lead['sources']:
                self.assertIsNone(source['publicationDate'])
                self.assertIn(source['accessStatus'], ('访问失败', '仅收到摘要，无独立原站链接'))

    def test_korea_freshness_does_not_replace_old_baseline(self):
        self.assertEqual(self.data['meta']['version'], '1.2')
        self.assertEqual(self.data['meta']['lastVerified'], '2026-10-28')
        for stop in self.data['stops']:
            if stop['id'] in ('busan','seoul'):
                self.assertTrue(stop.get('verifiedAt','').startswith('2026-11-06'))
                self.assertIn('2026-11-06', stop['dateVerification']['checkedAt'])
                self.assertIn('用户摘要', stop['dateConflict'])
            else:
                self.assertFalse(stop.get('verifiedAt','').startswith('2026-11-06'))
        korea = {s['id']: s for s in self.data['stops']}
        self.assertEqual(len(korea['busan']['presales']), 2)
        self.assertIn('一楼 VIP', korea['seoul']['ticketScope'])
        self.assertIn('01-21', korea['seoul']['ticketScope'])

if __name__ == '__main__':
    unittest.main()
