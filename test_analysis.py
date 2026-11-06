"""Synthetic software checks only. These are NOT observed public videos."""
import importlib.util
from pathlib import Path
import tempfile
import unittest
from datetime import datetime, timezone

spec = importlib.util.spec_from_file_location('analysis', Path(__file__).resolve().parents[1]/'scripts/analyze.py')
a = importlib.util.module_from_spec(spec)
spec.loader.exec_module(a)
NOW = datetime(2026, 11, 7, 0, 0, tzinfo=timezone.utc)


def synthetic(**changes):
    row = dict.fromkeys(a.HEADERS, '')
    row.update(record_id='TEST_ONLY_1', status='verified', platform='YouTube Shorts',
               video_url='https://example.invalid/video/1', creator_url='https://example.invalid/creator/1',
               creator_handle='fictional_test_creator', creator_type='dancer', content_format='dance',
               captured_at='2026-11-06T12:00:00+11:00', published_date='2026-11-01',
               audio_match='yes', metric_precision='exact', disclosure='unknown', language='en',
               search_query='SYNTHETIC TEST', hook='TEST', cta='none', views='100', likes='10',
               comments='0', shares='', saves='', followers='50', raw_metrics='TEST ONLY',
               missing_metrics_reason='shares:not_public; saves:not_public')
    row.update(changes)
    return row


class AnalysisTests(unittest.TestCase):
    def test_missing_share_does_not_become_zero(self):
        rows, _ = a.validate([synthetic()], NOW)
        self.assertEqual(rows[0]['like_view_rate'], .1)
        self.assertEqual(rows[0]['comment_view_rate'], 0)
        self.assertIsNone(rows[0]['lcs_view_rate'])

    def test_true_zero_and_zero_denominator(self):
        rows, _ = a.validate([synthetic(shares='0', views='0', likes='0')], NOW)
        self.assertIsNone(rows[0]['like_view_rate'])
        self.assertIsNone(rows[0]['lcs_view_rate'])

    def test_complete_numerator(self):
        rows, _ = a.validate([synthetic(shares='2', comments='3')], NOW)
        self.assertEqual(rows[0]['lcs_view_rate'], .15)

    def test_negative_abbreviated_and_future_are_rejected(self):
        for change in [dict(likes='-1'), dict(views='1.2K'), dict(captured_at='2099-01-01T00:00:00+00:00'),dict(captured_at='2026-11-01')]:
            with self.subTest(change=change):
                rows, issues = a.validate([synthetic(**change)], NOW)
                self.assertFalse(rows)
                self.assertTrue(any(i['severity']=='error' for i in issues))

    def test_url_deduplication(self):
        self.assertEqual(a.canonical_url('https://www.youtube.com/shorts/TESTID?si=abc'), a.canonical_url('https://youtu.be/TESTID'))
        self.assertEqual(a.canonical_url('https://youtube.com/watch?v=TESTID&t=3'), 'youtube:TESTID')
        rows, issues = a.validate([synthetic(), synthetic(record_id='TEST_ONLY_2')], NOW)
        self.assertEqual(len(rows), 1)
        self.assertTrue(any('Duplicate video' in i['message'] for i in issues))

    def test_metric_specific_sample_size_and_platform_separation(self):
        inputs = [synthetic(record_id=str(i), video_url=f'https://example.invalid/video/{i}',creator_url=f'https://example.invalid/creator/{i}',likes=str(v)) for i,v in enumerate([0,10,20])]
        rows, _ = a.validate(inputs, NOW)
        group = a.summarize(rows, 'content_format')[0]
        self.assertEqual(group['median_like_view_rate'], .1)
        self.assertEqual(group['n_lcs_view_rate'], 0)
        self.assertIsNone(group['median_lcs_view_rate'])
        self.assertIsNone(a.summarize(rows[:2], 'content_format')[0]['median_like_view_rate'])
        rows[0]['platform'] = 'TikTok'
        self.assertEqual(len(a.summarize(rows, 'content_format')), 2)

    def test_empty_template_integration(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            path = root/'input.csv'
            a.write_csv(path, sorted(a.HEADERS), [dict(record_id=f'V{i:02}',status='pending') for i in range(1,21)])
            self.assertEqual(a.run(path,root,NOW), (0,0))
            report = (root/'reports/analysis_summary.md').read_text(encoding='utf-8')
            self.assertIn('暂无合格观察',report)
            self.assertIn('No eligible observations', (root/'reports/figures/format_like_view.svg').read_text())

    def test_csv_formula_guard(self):
        self.assertEqual(a.safe_cell('=1+1'), "'=1+1")

    def test_nonempty_report_integration(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            inputs = [synthetic(record_id=f'TEST_{i}', video_url=f'https://example.invalid/video/{i}', creator_url=f'https://example.invalid/creator/{i}', likes=str(v)) for i,v in enumerate([0,10,20])]
            a.write_csv(root/'input.csv', sorted(a.HEADERS), inputs)
            self.assertEqual(a.run(root/'input.csv', root, NOW), (3,0))
            self.assertIn('10.00%', (root/'reports/analysis_summary.md').read_text(encoding='utf-8'))
            self.assertIn('10.00%', (root/'reports/figures/format_like_view.svg').read_text())


if __name__ == '__main__':
    unittest.main()
