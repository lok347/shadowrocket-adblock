# Changelog

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
