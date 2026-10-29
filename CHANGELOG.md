# Changelog

## AdBlock_lok.20261029 — 2026-10-29

### Added
- 已归档 2026-10-28 GitHub Actions 候选审查（PR #10）；稳定版新增 74 条 EasyList China 无条件 `||domain^` 规则，并转换为 `DOMAIN-SUFFIX,REJECT`。
- 来源锁定：`easylist/easylistchina` commit `ef624b775f18035510632920d7910094b282ce83`；见 `docs/reviews/2026-10-28.{md,json}` 与 `rules/candidates/2026-10-28.list`。
- 75 条候选均通过来源增量、去重、AWAvenue 覆盖、原有 DIRECT guard、来源例外检查；保留 `jieshengsz.com` 待进一步识别，防止可能的业务网站被整个域名误拦截。实发 74 条。

### Preserved and risks
- 完全保留原 DIRECT guards、AWAvenue RULE-SET、URL Rewrite、MITM、`scripts/adblock-clean.js`、iOS 捷径；稳定入口和日期归档必须逐字节相同。
- 仅完成规则层校验，**未做 iPhone / Shadowrocket 实机回归**；不保证具体 App 的广告被全部清除，也不保证零误杀。如出现 App 启动/登录/业务页面异常，按 `docs/MAINTENANCE.md` 通过 Git 历史回退至 `AdBlock_lok.20261023`。
- 本次稳定版发布来自 2026-10-29 用户明确指令；每周自动扫描仍只创建待审查 PR，后续不自动发布未经审核的规则。


## AdBlock_lok.20261023 — 2026-10-23

### Added
- 基于 2026-10-21 自动审查 Draft PR #8 和人工核验，向稳定模块新增 62 条 EasyList China 无条件 `||domain^` 规则，以 `DOMAIN-SUFFIX,REJECT` 实现。
- 来源锁定：`easylist/easylistchina` commit `5917795aae3d190292c6b02a5bacbbb46feb4052`；对应审查记录 `docs/reviews/2026-10-21.{md,json}`、`rules/candidates/2026-10-21.list`。
- 核验范围：逐条确认新增条目存在于固定来源而不在上一基线；无重复；无本地 DIRECT guard、AWAvenue 覆盖或来源例外冲突。同期来源撤回 6 条，均非本地静态 REJECT，本期无需删除。

### Preserved and risks
- 保留原有 DIRECT、社区 RULE-SET、URL Rewrite、MITM、Response Cleaner 及 iOS 捷径；固定订阅入口与 `Shadowrocket-AdBlock-lok.20261023.sgmodule` 内容必须一致。
- 仅通过规则和来源校验，未做 iPhone / App 实机回归测试；上游收录不代表已独立验证纯广告用途。出现启动或业务功能异常时应按 `docs/MAINTENANCE.md` 回滚。
- 发布获得仓库所有者 2026-10-23 的明确授权；候选审查不代表以后自动发布的长期授权。


## AdBlock_lok.20261015 — 2026-10-15

### Added
- 根据 EasyList China 最新固定 Commit `dcc067a21ac9628d117349303933efd0ddefa08e`，相对 2026-10-07 基线新增 88 条无路径、无修饰条件的 `||domain^`，转为 `DOMAIN-SUFFIX,REJECT`。
- 同期来源移除 414 条无条件域名规则；2026-10-07 发布的 162 条均仍在来源中，无需因本次撤回删除。
- 保存本期来源 SHA、撤回列表、逐域审查和候选规则文件。

### Maintenance cadence
- 从双周审查调整为每周审查，计划每周三北京时间约 09:17 运行；仅自动创建候选和 Draft PR，稳定版仍需人工授权发布。

### Preserved and risks
- 现有 DIRECT guards、社区 RULE-SET、URL Rewrite、MITM、`scripts/adblock-clean.js`、iOS 捷径均不修改；固定订阅入口与当期日期文件内容保持完全一致。
- 本期未进行 iPhone 或 App 实机验证。无条件域名增量不保证修复具体 App 的开屏广告；混合业务 API 需独立抓日志分析。
- 依据 2026-10-07 对无条件域名增量的已有发布授权及本次 2026-10-15 立即更新要求发布，保留回滚历史。


## AdBlock_lok.20261007 — 2026-10-07

### Naming

- 本次发布名称由 `AdBlock_lok.2` 改为 `AdBlock_lok.20261007`，以后以实际更新日期 `YYYYMMDD` 标识。
- GitHub 与下载副本统一使用 `Shadowrocket-AdBlock-lok.20261007.sgmodule`；固定订阅入口 `Shadowrocket-AdBlock.sgmodule` 与日期文件保持相同内容。
- 本次仅同步名称、文件名和文档，过滤规则未改变。

### Added

- 加入 EasyList China 最近约两周新增的 162 条无条件域名过滤规则，以 DOMAIN-SUFFIX / REJECT 写入稳定模块。
- 保存固定来源 SHA、逐域记录、Shadowrocket 规则清单及本期报告。

### Preserved

- 原有全部 REJECT、DIRECT guards、社区 RULE-SET、URL Rewrite、MITM hostname 与响应清理脚本保持不变。
- 稳定订阅地址保持不变。

### Validation

- 格式、去重、来源增量、域名覆盖和白名单/源例外冲突检查通过。
- 用户明确授权直接更新，未执行 iOS / App 实测。DNS 活跃性未完成核验；不将规则层检查描述为实机兼容保证。


## AdBlock_lok.1 — 2026-09-22

命名清理版本，不改变广告过滤逻辑。

### Changed

- 模块显示名称改为独立维护版本 `AdBlock_lok.1`。
- Response Cleaner 文件由 `scripts/gy-startup-ads-clean.js` 更名为 `scripts/adblock-clean.js`。
- Script 标识与调试前缀去除 `GY` 品牌前缀。
- 稳定模块的所有 `script-path` 已切换到新文件名。

本文件只记录 `lok347/shadowrocket-adblock` 自用维护版本的变化。

## Migration baseline — 2026-09-22

首次建立可维护仓库基线。

### Added

- 将 GY AdBlock v6.2 迁入普通 GitHub Repository。
- 新增本地托管的 `scripts/gy-startup-ads-clean.js`。
- 新增 README、维护 SOP 与变更记录。
- 建立 `main` 稳定版 / `dev` 开发版工作流。

### Changed

- 模块版本标记为 `v6.2-lok.1`。
- Response Cleaner 的 `script-path` 从原作者 Gist 改为本仓库 `main` Raw 地址。
- 保留原作者与 upstream 链接，不改变 v6.2 的广告识别与清理逻辑。

### Review

- 2026-09-22 检查 upstream：仍为 GY AdBlock v6.2，最后活动 2026-09-16。
- 本次没有发现需要新增或删除的广告规则，因此不对过滤逻辑做额外修改。
