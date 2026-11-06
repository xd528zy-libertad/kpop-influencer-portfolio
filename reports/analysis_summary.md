# 自动描述性分析

- 模板/输入行数：20；目标样本数：20。
- pending：20；人工 excluded：0；verified：0。
- 通过结构校验并纳入：0；质量错误：0；警告：0。
- 此报告只读取 CSV，不联网核验。错误行不进入统计；警告需要人工复核。

[质量问题](../data/processed/quality_issues.csv) · [逐条指标](../data/processed/video_metrics.csv) · [分组统计](../data/processed/group_summary.csv)

**暂无合格观察，不能判断哪种内容或达人表现更好。**
采集、核验后重新运行脚本；缺失值不会被补成零。

![采集进度](figures/collection_progress.svg)

![内容形式](figures/format_like_view.svg)

![达人类型](figures/creator_like_view.svg)

所有比率以小数保存在 CSV；例如 0.025 表示 2.5%。L+C+S/view 仅在点赞、评论、分享均可见时计算；每项指标都报告自己的有效 n。
