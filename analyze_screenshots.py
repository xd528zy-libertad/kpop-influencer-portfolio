"""Analyze screenshot evidence separately from fully verified video observations."""
import csv
from pathlib import Path
from statistics import median
from analyze import chart, write_csv

ROOT=Path(__file__).resolve().parents[1]

def main():
    with (ROOT/'data/raw/tiktok_observations.csv').open(encoding='utf-8-sig',newline='') as f:
        rows=list(csv.DictReader(f))
    ids=set()
    for r in rows:
        assert r['record_id'] not in ids
        ids.add(r['record_id'])
        for field in ('likes','comments','saves','shares'):
            r[field]=int(r[field]); assert r[field]>=0
        r['saves_per_like']=r['saves']/r['likes'] if r['likes'] else None
        r['shares_per_like']=r['shares']/r['likes'] if r['likes'] else None
    write_csv(ROOT/'data/processed/screenshot_metrics.csv',list(rows[0]),rows)
    summary=[]
    for key in ('tutorial','dance_related'):
        group=[r for r in rows if r['content_format']==key and r['sample_role']=='creator_candidate']
        summary.append(dict(group=key,n=len(group),median_likes=median(r['likes'] for r in group),median_saves_per_like=median(r['saves_per_like'] for r in group),median_shares_per_like=median(r['shares_per_like'] for r in group)))
    write_csv(ROOT/'data/processed/screenshot_groups.csv',list(summary[0]),summary)
    chart(ROOT/'reports/figures/screenshot_saves_per_like.svg','APT. | Saves per like by visible content format','Screenshot counts, rounded inputs. Creator candidates only; these are NOT view-based engagement rates.',[(f"TikTok / {g['group']}",g['median_saves_per_like'],g['n']) for g in summary],True)
    chart(ROOT/'reports/figures/screenshot_counts.svg','APT. | Evidence coverage','20 screenshots transcribed. Link mapping confirmed by user; full video/profile checks remain pending.', [('Screenshots transcribed',len(rows),len(rows)),('Creator candidates',19,19),('Media context record',1,1),('Visible view counts',0,0),('Visible follower counts',0,0)])
    lines=['# TikTok 截图观察：自动分析','',f'已转录 {len(rows)} 张截图。链接与截图顺序由用户确认；未完成网页、音频和账号主页核验。','',
    '采集日期：用户确认 2026-11-07；用户提供批次时间 01:37，截图状态栏约 01:22–01:29；时区未知，不能计算精确视频年龄。','',
    '## 可观察数据','',f"全体 20 张截图显示的点赞折算合计约 {sum(r['likes'] for r in rows):,}；评论约 {sum(r['comments'] for r in rows):,}；收藏约 {sum(r['saves'] for r in rows):,}；分享约 {sum(r['shares'] for r in rows):,}。",
    '以上是各视频累计计数的算术合计，不是独立用户人数、当前实时数据或活动新增结果。简写数字按万折算，保留原始显示精度。所有截图均未显示视频播放量或账号粉丝量。','',
    '## 内容分组（探索性）','', '| 暂定内容形式 | 创作者候选 n | 点赞中位数（约） | 收藏/点赞中位比值（约） | 分享/点赞中位比值（约） |','|---|---:|---:|---:|---:|']
    for g in summary:
        lines.append(f"| {g['group']} | {g['n']} | {g['median_likes']:,.0f} | {g['median_saves_per_like']:.1%} | {g['median_shares_per_like']:.1%} |")
    lines += ['', 'V07 的显示名提示媒体账号，留作背景观察，不进入创作者分组；其余19条是候选记录，不代表已确认的19个独立创作者。',
    'tutorial = V12、V18、V20，画面或文案明确显示教学提示；dance_related = 其他舞蹈相关画面，不能仅靠静帧确认完整叙事。账号类型保持未核验。',
    '收藏/点赞和分享/点赞是两种累计行为计数的比值，不是用户转化概率或按播放量计算的互动率。同一人可能产生多个行为；分母不同，不可用来宣布推广效率。','',
    '![样本覆盖](figures/screenshot_counts.svg)','', '![收藏相对点赞](figures/screenshot_saves_per_like.svg)','',
    '## 对策略的启示','',
    '三条带明确教学提示的候选内容，在本批样本中呈现较高的收藏/点赞中位比值。这支持把“分步教学、方便回看”作为优先测试假设；不能据此证明教程带来更多歌单收听。',
    '双人、群体、居家和造型演绎提供不同创意场景；样本未包含足够翻唱、音乐评论等类型，不能得出舞蹈优于其他形式的结论。',
    'V05 可见文案有二选一提问；这是可复用的互动设计线索，但没有评论内容分析，不能判断评论是否由提问引起。','',
    '## 审核边界','',
    '便利样本、非随机检索、热门视频选择偏差、发布时间不同、四舍五入及未知付费推广都会影响比较。截图无法证明视频开头、全程CTA、声音和合作披露；没有把搜索建议当实际搜索词，也没有把播放列表“+1M views”当本视频播放数。',
    'V12 发布时间被叠字遮挡而留空；V07/V16 显示名被截断；所有账号主页、粉丝量、播放量缺失。来源是用户提供的20张截图，见原始表 evidence_ref。',
    '', '[原始转录表](../data/raw/tiktok_observations.csv) · [逐条计算](../data/processed/screenshot_metrics.csv) · [分组统计](../data/processed/screenshot_groups.csv)']
    (ROOT/'reports/tiktok_findings.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')
    print(summary)

if __name__=='__main__':
    main()
