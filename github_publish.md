# 从零发布到 GitHub

本交付是本地项目包，尚未创建远程仓库。建议名称 `kpop-influencer-portfolio`。
简介可用：`An independent APT. creator-marketing study and playlist campaign proposal.`

## 路线 A：浏览器上传（无需 Git 命令）
1. 解压项目压缩包，进入 `kpop-influencer-portfolio` 文件夹。
2. 登录 GitHub，选择 New repository，填名称和简介。求职展示选 Public；不勾选自动创建 README、gitignore 或 license，因为项目已有相应文件。
3. 创建后选择 uploading an existing file；已有文件的仓库选择 Add file → Upload files。
4. 上传项目文件夹**里面的文件和子文件夹**，让 README.md 位于仓库根目录，不要只上传 ZIP，也不要把整个包嵌套一层。不要上传私人截图或访问令牌。浏览器上传不会应用 .gitignore，需人工排除。
5. 填提交说明 `Add research framework and campaign proposal`，按页面完成提交；若选择新分支，合并后再检查默认分支。
6. 打开 README，检查表格、图片及相对链接。About 可加 `marketing`、`influencer-marketing`、`kpop`、`portfolio`、`python` 标签。在个人主页置顶该仓库。

## 路线 B：本地 Git（可选）
先在 GitHub 创建同名空仓库，不初始化 README。在**解压后的项目文件夹**打开终端；把下面 YOUR_USERNAME 换成你的账号：

```sh
git init
git add .
git commit -m "Add research framework and campaign proposal"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/kpop-influencer-portfolio.git
git push -u origin main
```

若 Git 提示身份未设置，按提示配置你希望公开的姓名与提交邮箱；可选择 GitHub 提供的隐私邮箱。使用 GitHub 的登录流程，勿把令牌写进代码。已有 origin 时先查看 `git remote -v`，不要盲目覆盖。远程仓库已有文件时优先使用浏览器上传或先克隆，不做强制推送。

## 分阶段更新
- v0.1：现在就可发布，标题/摘要保留“data collection pending”。
- v0.2：填完实际样本，运行分析与测试，处理 quality_issues.csv，再提交 CSV 和生成的报告/图表。
- v1.0：补充 case_study 的证据链；将 README 状态改为真实完成情况。只有开展活动后才能增加实际营销结果。

## 发布检查
- [ ] README 在根目录，图片可见，工作簿能下载。
- [ ] 数字可追溯到 URL 和带时区的采集时间；没有隐藏的演示数据。
- [ ] 样本局限、提案状态、AI 协助与本人贡献说明准确。
- [ ] 没有私人资料、截图、视频文件、密钥或内部路径。
- [ ] 运行 `python scripts/analyze.py` 后没有未处理的质量错误。
- [ ] 读者知道“点击歌单”不等于“收听歌曲”。

参考：[创建仓库](https://docs.github.com/en/repositories/creating-and-managing-repositories/creating-a-new-repository) · [上传文件](https://docs.github.com/en/repositories/working-with-files/managing-files/adding-a-file-to-a-repository)。操作说明核对日 2026-11-07。
