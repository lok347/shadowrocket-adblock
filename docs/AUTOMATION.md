# 双周审查自动化（MVP）

此工作流仅做**审查和候选收集**，不会直接改变 Shadowrocket 生效规则。现有固定订阅链接、iOS 捷径和日期归档保持不变。

## 工作原理

- `.github/workflows/adblock-review.yml` 每周三北京时间 09:17 触发，但仅在相对 **2026-10-21** 的 14 天整周期执行。
- `workflow_dispatch` 支持手动 Dry-run（默认开启）。2026-10-14 可手动执行 Dry-run，不改变下一周期基准。
- 从最近的 `docs/reviews/*.json` 获取固定来源 SHA，读取该 Commit 下的 EasyList China 基线；获取新的 EasyList China、AWAvenue、EasyList 的固定 Commit 与文件 Blob SHA。校验下载内容的 Git blob SHA，失败则停止。
- 仅采纳字面形式为 `||domain^`、没有 path、modifier、资源类型及域名限制的条目作为来源新增域名；其他过滤语法不自动转换。
- 对比本地静态 REJECT 和 DIRECT、最新 AWAvenue、来源例外；记录上游移除、AWAvenue 移除、来源例外变更。冲突项不能列入待发布清单。
- 写出 `docs/reviews/YYYY-MM-DD.{json,md}` 和 `rules/candidates/YYYY-MM-DD.list`（**候选文件不会被稳定模块引用**）。
- 当非 Dry-run 且当日无现存同名分支时，创建独立的 `automation/adblock-review-YYYY-MM-DD` 分支及 Draft PR，等待人工审阅；不会自动修改 `main`。

## 启用要求

1. 仅在仓库所有者审核并合并本自动化 PR 后，定时工作流才会在默认分支运行。
2. 仓库设置中需要允许 GitHub Actions 创建 Pull Requests，且 `GITHUB_TOKEN` 具有本工作流声明的 `contents: write` / `pull-requests: write` 作用域；否则报告脚本仍可运行，但 PR 创建将失败并在 Actions 日志中提示。
3. 首次合并后建议手动触发 `dry_run=true` 查看报告；请勿把 GitHub Token 写入源码或提交到仓库。
4. GitHub 定时工作流可能延迟；若长期不活跃可能被停用，请通过 Actions 页面核查。

## 发布仍需人工批准

通过 Draft PR 并不意味着发布。正式发布应另行验证待发布候选，随后**同时**更新日期 `.sgmodule`、固定 `Shadowrocket-AdBlock.sgmodule`、README、CHANGELOG；两份模块须逐字节一致。未更新固定订阅入口时，iPhone 不会因为报告或 PR 而获取新规则。带日期的旧订阅始终指向旧文件。

## 当前局限与后续改进

- 不做 iOS / App 实机测试，不保证候选域名只承载广告流量。
- 来源列表收录并不构成独立核实；EasyList 和 EasyList China 不视为两家独立来源。
- 现有稳定模块仍动态引用 AWAvenue `main` 和 Cleaner `main`；建议单独审核 Commit 版本锁定，避免静默变更，但**本 MVP 不修改运行期依赖**。
- 目前只自动采集 EasyList China 的无条件域名增量，AWAvenue/EasyList 用于覆盖、例外和撤回辅助；对 GY AdBlock / 其他上游的差异分析尚待扩展。
- 不自动清理被上游移除的域名；请在人工审查时考虑误杀撤回。
- GitHub Actions 以 `GITHUB_TOKEN` 创建的 PR 通常不会自动触发新的 `pull_request` 工作流；生成 PR 的 job 事先跑本地测试，审核者仍应显式检查测试情况。
