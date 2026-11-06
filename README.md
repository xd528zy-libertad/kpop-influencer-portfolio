# From Dance Challenge to Playlist Discovery
## 《APT.》TikTok 内容观察与歌单推广策略

**Independent marketing portfolio · Screenshot-based exploratory study**

已完成20条用户提供截图的互动数据转录、内容初步分类与描述性分析。链接与截图按序对应已由用户确认；完整视频、账号主页和短链接尚未独立核验。推广提案未执行。

### 项目回答什么问题？
围绕 ROSÉ & Bruno Mars《APT.》，哪些可观察的内容特点值得转化成下一轮歌单推广测试？本案例展示研究整理、指标判断、内容策略与测量设计，而不是宣称实际投放增长。

### 关键发现
- 20张TikTok截图有可读的点赞、评论、收藏与分享；没有可读的播放量或账号粉丝量，因此不计算播放互动率、触达率或ROI。
- 3条明确教学提示内容的收藏/点赞中位比值约28.0%；其余16条创作者候选的舞蹈相关内容约9.3%。另1条媒体背景记录不参加分组。
- 该差异只用于提出“教程方便回看”的创意假设。样本量、发布时间、粉丝基础与选择偏差未被控制，不能当作因果关系或收听转化证据。

![数据覆盖](reports/figures/screenshot_counts.svg)

### 从证据到策略
| 阅读入口 | 内容 | 展示能力 |
|---|---|---|
| [案例报告](reports/case_study.md) | 发现、替代解释及行动 | Insight / storytelling |
| [自动分析与图表](reports/tiktok_findings.md) | 有效样本与指标口径 | Marketing analytics |
| [20条原始转录 CSV](data/raw/tiktok_observations.csv) | 原始显示、数值、链接、截图标识 | Evidence management |
| [推广提案](strategy/tiktok_campaign.md) | 三个创意、达人筛选与KPI | Influencer strategy |
| [研究方法](docs/tiktok_methodology.md) | 便利取样、修订和限制 | Research design |
| [GitHub发布指南](docs/github_publish.md) | 项目更新方法 | Communication |

### English brief
An exploratory screenshot-based study of 20 TikTok posts associated with “APT.” Publicly displayed interaction counts were transcribed and used to develop playlist-promotion hypotheses. Three tutorial-labelled posts showed a higher median saves-to-likes ratio than 16 other creator candidates. One apparent media-account post was retained as context only. Views, follower counts and conversion data were unavailable; no causal effect, campaign uplift or ROI is claimed. Link-to-image mapping was confirmed by the contributor, while independent video and profile verification remains pending.

### 复现分析
Python 3.10+，无需第三方库。在项目文件夹运行：
```sh
python scripts/analyze_screenshots.py
python -m unittest discover -s tests -v
```
输入：`data/raw/tiktok_observations.csv`；输出：`reports/tiktok_findings.md`、`data/processed/screenshot_*.csv` 和 `reports/figures/screenshot_*.svg`。

`videos.csv` 已填入截图可见字段，但保留 pending，避免冒充完整验证记录；原 `scripts/analyze.py` 用于未来完成视频与账号核验后的分析。它的空样本报告不代表截图没有数据。
原 `collection_template.xlsx` 是空白采集模板；本次数据以链接的 CSV 为准，用 Excel 可以打开，不需要用户重复填写。

### 状态与限制
截图日期由用户确认为2026-11-07；用户报告批次时间01:37，截图状态栏约01:22–01:29；时区未知。数据不是实时统计。
初始YouTube研究计划已调整为用户提供的TikTok便利样本，没有实际执行预设搜索配额。完整修订说明见研究方法。旧计划与模板作为设计记录保留。
本项目与艺人、唱片公司及平台无官方关联。AI协助转录、代码与初稿；用户提供素材及顺序确认。未发布截图副本，未进行达人联系或真实投放。
