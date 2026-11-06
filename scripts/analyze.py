"""Reproducible public-snapshot analysis. No scraping, no invented observations."""
from __future__ import annotations

import argparse
import csv
import html
import re
import sys
from collections import defaultdict, Counter
from datetime import datetime, date, timezone
from pathlib import Path
from statistics import median
from urllib.parse import urlparse, parse_qs

ROOT = Path(__file__).resolve().parents[1]
NUMBERS = ('followers', 'views', 'likes', 'comments', 'shares', 'saves')
RATES = ('like_view_rate', 'comment_view_rate', 'lcs_view_rate', 'views_followers_ratio')
ENUMS = {
    'platform': {'YouTube Shorts', 'TikTok', 'Instagram Reels', 'Douyin', 'Bilibili'},
    'creator_type': {'dancer', 'musician', 'lifestyle', 'comedy', 'fan_curator', 'other'},
    'content_format': {'dance', 'cover', 'reaction', 'skit', 'lifestyle', 'tutorial', 'other'},
    'metric_precision': {'exact', 'rounded', 'mixed', 'unknown'},
    'disclosure': {'disclosed', 'not_observed', 'unknown'},
}
REQUIRED = ('record_id', 'status', 'platform', 'video_url', 'creator_handle', 'creator_url',
            'creator_type', 'content_format', 'captured_at', 'audio_match',
            'metric_precision', 'disclosure', 'search_query', 'hook', 'cta', 'language')
HEADERS = set(REQUIRED) | set(NUMBERS) | {'published_date', 'raw_metrics',
            'missing_metrics_reason', 'search_rank', 'notes', 'evidence_ref'}


def canonical_url(value):
    p = urlparse(value.strip())
    host = (p.hostname or '').lower().removeprefix('www.').removeprefix('m.')
    path = p.path.rstrip('/')
    if host in ('youtube.com', 'youtu.be'):
        if host == 'youtu.be':
            video_id = path.lstrip('/')
        elif path.startswith(('/shorts/', '/embed/')):
            video_id = path.split('/')[-1]
        else:
            video_id = parse_qs(p.query).get('v', [''])[0]
        if video_id:
            return f'youtube:{video_id}'
    return host + path


def valid_url(value):
    p = urlparse(value)
    return p.scheme == 'https' and bool(p.hostname) and not p.username


def count_value(value):
    value = value.strip()
    if not value:
        return None
    if not re.fullmatch(r'[0-9]+', value):
        raise ValueError('use a nonnegative integer, or leave blank')
    return int(value)


def ratio(numerator, denominator):
    if numerator is None or denominator is None or denominator <= 0:
        return None
    return numerator / denominator


def validate(rows, now=None):
    now = now or datetime.now(timezone.utc)
    valid, issues = [], []
    seen_ids, seen_videos, seen_creators = set(), set(), set()
    for line, source in enumerate(rows, 2):
        row = {k: (v or '').strip() for k, v in source.items()}
        rid = row.get('record_id') or f'line_{line}'
        errors = []

        def issue(message, severity='error'):
            issues.append(dict(record_id=rid, line=line, severity=severity, message=message))
            if severity == 'error':
                errors.append(message)

        if not row.get('record_id'):
            issue('Missing record_id')
        elif rid in seen_ids:
            issue('Duplicate record_id; fix before publishing')
        seen_ids.add(rid)
        status = row.get('status', '')
        if status not in ('pending', 'verified', 'excluded'):
            issue('status must be pending, verified or excluded')
        if status != 'verified':
            if status == 'excluded' and not row.get('notes'):
                issue('Excluded row needs a reason in notes')
            continue
        for field in REQUIRED:
            if not row.get(field):
                issue(f'Missing {field}')
        for field, options in ENUMS.items():
            if row.get(field) not in options:
                issue(f'Invalid {field}: {row.get(field, "")}')
        for field in ('video_url', 'creator_url'):
            if not valid_url(row.get(field, '')):
                issue(f'{field} must be a public HTTPS URL')
        if row.get('audio_match') != 'yes':
            issue('Verified rows require audio_match=yes after human review')
        capture = None
        try:
            capture = datetime.fromisoformat(row.get('captured_at', '').replace('Z', '+00:00'))
            if capture.utcoffset() is None:
                raise ValueError()
            if capture > now:
                issue('captured_at is in the future')
        except ValueError:
            issue('captured_at needs an ISO timestamp including timezone offset')
        age = None
        if row.get('published_date'):
            try:
                published = date.fromisoformat(row['published_date'])
                if capture is not None:
                    age = (capture.date() - published).days
                    if age < 0:
                        issue('published_date is after capture date')
            except ValueError:
                issue('published_date must be YYYY-MM-DD')
        else:
            issue('Missing published_date; post age cannot be compared', 'warning')
        for field in NUMBERS:
            try:
                row[field] = count_value(row.get(field, ''))
            except ValueError as e:
                issue(f'{field}: {e}')
                row[field] = None
        if any(row[f] is None for f in NUMBERS) and not row.get('missing_metrics_reason'):
            issue('Explain missing metrics in missing_metrics_reason')
        if any(row[f] is not None for f in NUMBERS) and not row.get('raw_metrics'):
            issue('Record original metric display text in raw_metrics')
        if row.get('search_rank'):
            try:
                if count_value(row['search_rank']) < 1:
                    raise ValueError()
            except ValueError:
                issue('search_rank must be a positive integer')
        video_key = canonical_url(row.get('video_url', ''))
        creator_key = (row.get('platform'), canonical_url(row.get('creator_url', '')).casefold())
        if video_key in seen_videos:
            issue('Duplicate video URL; later row excluded')
        if creator_key in seen_creators:
            issue('Repeated creator within platform; later row excluded by sampling protocol')
        if errors:
            continue
        seen_videos.add(video_key)
        seen_creators.add(creator_key)
        row['post_age_days'] = age
        row['like_view_rate'] = ratio(row['likes'], row['views'])
        row['comment_view_rate'] = ratio(row['comments'], row['views'])
        interactions = None if any(row[f] is None for f in ('likes','comments','shares')) else sum(row[f] for f in ('likes','comments','shares'))
        row['lcs_view_rate'] = ratio(interactions, row['views'])
        row['views_followers_ratio'] = ratio(row['views'], row['followers'])
        if row['views'] == 0:
            issue('Zero views: view-based ratios unavailable', 'warning')
        if row['likes'] is not None and row['views'] is not None and row['likes'] > row['views']:
            issue('Likes exceed views; recheck display precision and snapshot timing', 'warning')
        valid.append(row)
    return valid, issues


def summarize(rows, dimension):
    groups = defaultdict(list)
    for row in rows:
        groups[(row['platform'], row[dimension])].append(row)
    output = []
    for (platform, category), members in sorted(groups.items()):
        result = dict(platform=platform, dimension=dimension, category=category, n_videos=len(members))
        for metric in ('views', *RATES):
            values = [r[metric] for r in members if r[metric] is not None]
            result[f'n_{metric}'] = len(values)
            result[f'median_{metric}'] = median(values) if len(values) >= 3 else None
        output.append(result)
    return output


def safe_cell(value):
    # Prevent copied public text from becoming a spreadsheet formula on export.
    if isinstance(value, str) and value.startswith(('=', '+', '-', '@', '\t', '\r')):
        return "'" + value
    return value


def write_csv(path, fields, rows):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('w', encoding='utf-8-sig', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fields, extrasaction='ignore')
        writer.writeheader()
        writer.writerows({k: safe_cell(v) for k, v in row.items()} for row in rows)


def chart(path, title, subtitle, entries, percent=False):
    height = max(270, 150 + 46 * len(entries))
    parts = [f'<svg xmlns="http://www.w3.org/2000/svg" width="1100" height="{height}" viewBox="0 0 1100 {height}" role="img" aria-label="{html.escape(title)}">',
             '<rect width="100%" height="100%" fill="#faf9f6"/>',
             '<g font-family="Arial, sans-serif" fill="#222b39">',
             f'<text x="30" y="42" font-size="23" font-weight="bold">{html.escape(title)}</text>',
             f'<text x="30" y="72" font-size="13">{html.escape(subtitle)}</text>']
    if not entries:
        parts += ['<text x="30" y="150" font-size="20">No eligible observations yet.</text>',
                  '<text x="30" y="180" font-size="15">Collect and verify public videos before interpreting performance.</text>']
    else:
        maximum = max([value for _, value, _ in entries if value is not None] + [0]) or 1
        for i, (label, value, n) in enumerate(entries):
            y = 115 + 46 * i
            parts.append(f'<text x="30" y="{y+17}" font-size="13">{html.escape(label)}</text>')
            if value is None:
                parts.append(f'<text x="430" y="{y+17}" font-size="13">Unavailable (valid n={n}; need 3)</text>')
            else:
                width = value / maximum * 470
                display = f'{value:.2%}' if percent else f'{value:g}'
                parts += [f'<rect x="430" y="{y}" width="{width:.2f}" height="24" rx="3" fill="#7465a8"/>',
                          f'<text x="{440+width:.2f}" y="{y+17}" font-size="13">{display} | n={n}</text>']
    parts.append('</g></svg>')
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text('\n'.join(parts), encoding='utf-8')


def run(input_path, output_root, now=None):
    with input_path.open(encoding='utf-8-sig', newline='') as f:
        reader = csv.DictReader(f)
        absent = HEADERS - set(reader.fieldnames or [])
        if absent:
            raise ValueError('Missing CSV columns: ' + ', '.join(sorted(absent)))
        rows = list(reader)
    if any(None in row for row in rows):
        raise ValueError('CSV row has too many columns; check quoting and commas')
    valid, issues = validate(rows, now=now)
    grouped = summarize(valid, 'content_format') + summarize(valid, 'creator_type')
    processed = output_root / 'data/processed'
    metrics_fields = ['record_id','platform','video_url','creator_type','content_format','captured_at','post_age_days',*NUMBERS,*RATES]
    group_fields = ['platform','dimension','category','n_videos'] + [f'{prefix}_{metric}' for metric in ('views', *RATES) for prefix in ('n','median')]
    write_csv(processed/'video_metrics.csv', metrics_fields, valid)
    write_csv(processed/'group_summary.csv', group_fields, grouped)
    write_csv(processed/'quality_issues.csv', ['record_id','line','severity','message'], issues)
    figures = output_root/'reports/figures'
    counts = Counter(r.get('status','') for r in rows)
    errors = sum(i['severity']=='error' for i in issues)
    chart(figures/'collection_progress.svg', 'APT. | Collection progress',
          'Rows in the current input file; verified status does not replace human source review.',
          [('Pending', counts['pending'], counts['pending']),
           ('Excluded by researcher', counts['excluded'], counts['excluded']),
           ('Verified and structurally valid', len(valid), len(valid)),
           ('Verified but invalid', counts['verified']-len(valid), counts['verified']-len(valid))])
    for dimension, filename in [('content_format','format_like_view.svg'),('creator_type','creator_like_view.svg')]:
        chart(figures/filename, 'Median like/view rate by '+dimension.replace('_',' '),
              'Within-platform descriptive comparisons only. Medians suppressed when valid n < 3.',
              [(f'{g["platform"]} / {g["category"]}', g['median_like_view_rate'], g['n_like_view_rate']) for g in grouped if g['dimension']==dimension], True)
    report = ['# 自动描述性分析', '', f'- 模板/输入行数：{len(rows)}；目标样本数：20。',
              f'- pending：{counts["pending"]}；人工 excluded：{counts["excluded"]}；verified：{counts["verified"]}。',
              f'- 通过结构校验并纳入：{len(valid)}；质量错误：{errors}；警告：{len(issues)-errors}。',
              '- 此报告只读取 CSV，不联网核验。错误行不进入统计；警告需要人工复核。', '',
              '[质量问题](../data/processed/quality_issues.csv) · [逐条指标](../data/processed/video_metrics.csv) · [分组统计](../data/processed/group_summary.csv)', '']
    if valid:
        captures = [datetime.fromisoformat(r['captured_at'].replace('Z','+00:00')) for r in valid]
        start, end = min(captures), max(captures)
        report += [f'采集窗口：{start.isoformat()} 至 {end.isoformat()}。',
                   f'窗口跨度：{(end-start).total_seconds()/3600:.1f} 小时；方法建议不超过 48 小时。',
                   '', '| 平台 | 分组维度 | 类别 | 视频 n | Like/view 有效 n | 中位数 |', '|---|---|---|---:|---:|---:|']
        for g in grouped:
            value = g['median_like_view_rate']
            display = '样本不足' if value is None else f'{value:.2%}'
            report.append(f'| {g["platform"]} | {g["dimension"]} | {g["category"]} | {g["n_videos"]} | {g["n_like_view_rate"]} | {display} |')
        report += ['', '分组比较为描述性结果。先检查视频年龄、计数精度、达人量级和缺失情况，再形成待测试假设。不能据此推断增量收听或因果效果。']
    else:
        report += ['**暂无合格观察，不能判断哪种内容或达人表现更好。**', '采集、核验后重新运行脚本；缺失值不会被补成零。']
    report += ['', '![采集进度](figures/collection_progress.svg)', '', '![内容形式](figures/format_like_view.svg)', '', '![达人类型](figures/creator_like_view.svg)', '',
               '所有比率以小数保存在 CSV；例如 0.025 表示 2.5%。L+C+S/view 仅在点赞、评论、分享均可见时计算；每项指标都报告自己的有效 n。']
    (output_root/'reports/analysis_summary.md').write_text('\n'.join(report)+'\n', encoding='utf-8')
    return len(valid), errors


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--input', type=Path, default=ROOT/'data/raw/videos.csv')
    parser.add_argument('--output-root', type=Path, default=ROOT)
    args = parser.parse_args()
    try:
        n, errors = run(args.input, args.output_root)
    except (ValueError, OSError) as exc:
        print(f'Analysis stopped: {exc}', file=sys.stderr)
        return 2
    print(f'Eligible observations: {n}; validation errors: {errors}. See reports/analysis_summary.md.')
    return 1 if errors else 0


if __name__ == '__main__':
    sys.exit(main())
