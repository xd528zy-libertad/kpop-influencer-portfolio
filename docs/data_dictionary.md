# 数据字典

一行代表一个视频在一次采集窗口的公开快照；不把复查快照追加成新的独立视频。历史快照另存归档，主表保持一视频一行。

空白 ≠ 0。除 record_id/status 外的预留行为空，均不是真实观察。

| 列名 | 填写规则 |
|---|---|
| `record_id` | 固定记录编号 V01–V20；不可重复 |
| `status` | pending / verified / excluded；只有 verified 进入分析 |
| `platform` | YouTube Shorts / TikTok / Instagram Reels / Douyin / Bilibili；默认只用第一项 |
| `video_url` | 公开视频 HTTPS URL；YouTube 可用 shorts、watch 或 youtu.be 链接 |
| `creator_handle` | 公开账号名；纯文本；不是私人真实姓名 |
| `creator_url` | 账号页面 HTTPS URL；用于创作者去重 |
| `creator_type` | dancer / musician / lifestyle / comedy / fan_curator / other；看账号定位 |
| `followers` | 采集时粉丝/订阅数；非负整数，可空 |
| `content_format` | dance / cover / reaction / skit / lifestyle / tutorial / other；看本条内容 |
| `published_date` | YYYY-MM-DD；不可见留空，不凭相对日期猜精确日期 |
| `captured_at` | 真实采集时间 YYYY-MM-DDTHH:MM:SS+时区偏移；不要预填 |
| `views` | 公开播放次数，非负整数；缺失留空 |
| `likes` | 公开点赞次数，非负整数；缺失留空 |
| `comments` | 公开评论次数，非负整数；缺失留空 |
| `shares` | 公开分享次数，非负整数；缺失留空 |
| `saves` | 公开收藏次数，非负整数；缺失留空；不计入 L+C+S 指标 |
| `metric_precision` | exact / rounded / mixed / unknown；标记显示精度 |
| `raw_metrics` | 逐项保存页面原始显示与单位，注明来自视频页或账号页 |
| `missing_metrics_reason` | 逐项原因：not_public / hidden / not_visible / not_applicable / not_collected |
| `audio_match` | yes / no / uncertain；仅 yes 可进入 verified 分析 |
| `language` | 内容语言如 en / ko / zh / mixed / instrumental / unknown；不推断受众国籍 |
| `disclosure` | disclosed / not_observed / unknown；not_observed 不表示一定未合作 |
| `hook` | 开头的具体吸引点；用自己的话概括 |
| `cta` | 行动号召；没有填 none；区分评论/模仿/歌单点击 |
| `search_query` | 发现视频时使用的查询词 |
| `search_rank` | 页面展示顺序，从 1 开始；不可见可空并说明 |
| `evidence_ref` | 可选的本地截图文件名或核验笔记标识；不要填写机器绝对路径 |
| `notes` | 纳入/排除理由、分类依据、日期未知原因或复核说明 |

数值不填 K、万、逗号、百分号或公式；原始显示写 raw_metrics。CSV 为 UTF-8 BOM，便于 Excel 显示中文。编辑后保留列名与顺序。
