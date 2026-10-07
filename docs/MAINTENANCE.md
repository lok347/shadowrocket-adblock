# Maintenance SOP

本仓库的目标不是追求“规则最多”，而是维持 **高命中、低误杀、可回滚** 的 Shadowrocket 去广告配置。

## 1. 上游检查

主要观察：

1. GY AdBlock upstream  
   https://gist.github.com/Y123456-hzy/dd342a1a61daf8c250b112faa1381918
2. AWAvenue Ads Rule  
   https://github.com/TG-Twilight/AWAvenue-Ads-Rule

发现 upstream 变化后，不直接覆盖 `main`。先记录：

- 修改了哪些 DIRECT guard
- 新增/删除了哪些域名 REJECT
- URL Rewrite 是否扩大匹配范围
- MITM hostname 是否扩大
- Response Cleaner 是否增加新 route / marker
- 修改是否针对某个特定 App 的兼容性问题

## 2. 分层判断

遇到新广告时按以下顺序判断。

### A. DOMAIN / DOMAIN-SUFFIX REJECT

只用于高置信、纯广告/追踪域名。

不适合：
- SDK 基础服务
- 同域同时承载业务 API
- App 启动、配置、鉴权依赖

### B. DIRECT guard

当社区域名库误杀 SDK 握手、配置、遥测或启动依赖时使用。

DIRECT guard 必须位于对应社区 RULE-SET / REJECT 之前，因为 Shadowrocket 按先匹配原则处理。

### C. URL Rewrite

适合：
- 开屏广告接口
- 独立广告物料接口
- 明确的 view/click/ad payload endpoint

优先精确匹配 path，避免只按域名拦截。

### D. Response Cleaner

只有以下情况才考虑：
- 广告和正常内容混合在同一个 JSON 响应
- 直接 reject 会导致页面报错/空白
- 可以可靠识别广告对象

保持现有安全模型：
- route allowlist
- strong ad markers
- known ad containers
- 非 JSON / 未知路由 / 未发生修改 -> pass-through

## 3. 一个新问题的处理流程

`复现 -> 抓日志 -> 确认 URL/响应 -> 判断层级 -> dev 修改 -> 测试 App 核心功能 -> 检查副作用 -> 合并 main`

至少检查：

- App 冷启动和热启动
- 首页是否正常加载
- 登录/鉴权
- 图片和视频加载
- 搜索
- 支付/下单等关键业务（如适用）
- 是否出现持续重试、耗电或流量异常

## 4. 风险信号

出现以下现象应优先怀疑误杀：

- App 卡在启动页
- 首屏长时间白屏
- PacketTunnel 日志同一域名高频重试
- 图片全部加载失败
- 登录状态丢失
- 某功能在关闭模块后立即恢复

此时优先撤销最近规则，或把 SDK 基础域名加入 DIRECT guard，再用精确 Rewrite 处理广告接口。

## 5. 版本规则

- upstream 版本与本仓库版本分开记录，不混用版本号。
- upstream 原始版本：例如 `GY AdBlock v6.2`，仅作为来源基线记录。
- 本仓库稳定版本采用独立序列：
  - `AdBlock_lok.1`
  - `AdBlock_lok.2`
  - `AdBlock_lok.3`
- upstream 升级不会自动重置本仓库版本号；只有实际发布本仓库新稳定版时才递增 `lok.x`。

## 6. 回滚

Shadowrocket 稳定订阅只指向 `main`。

如果新版本出现兼容问题：
1. 找到上一个稳定 commit。
2. 在 `dev` 撤销有问题的规则。
3. 验证后再更新 `main`。
4. CHANGELOG 记录原因和受影响 App。

不要在没有日志或复现证据时连续叠加“修复规则”，否则很难定位副作用。

## 7. 提交信息建议

- `fix: restore Coolapk startup dependency`
- `feat: block <app> splash endpoint`
- `fix: narrow <domain> rewrite pattern`
- `chore: sync reviewed upstream changes`
- `docs: document compatibility issue`

## 8. 提交问题时建议提供

- App 名称/版本
- iOS 版本
- Shadowrocket 版本
- 广告类型与出现位置
- 相关 URL / hostname
- HTTP 状态码
- 响应 JSON 中可识别的广告字段（敏感值需脱敏）
- 开启/关闭模块后的差异

## 9. 双周新增域名搜集

自 2026-10-07 起，每两周做一次增量搜集，下一次计划为 2026-10-21。默认通过 ChatGPT 双周任务执行，交付到本仓库 `dev` 与草稿 PR。

1. 先读 main/dev 和最近 `docs/reviews/` 记录，固定当前本地模块与来源 commit/blob SHA。
2. 查看 AWAvenue、EasyList China、EasyList、AdGuard 官方来源的新增规则和误封撤回。使用上一期源快照作基线，不根据名字猜测广告用途，不要求凑满新增数量。
3. 对照本地 REJECT、AWAvenue 与 DIRECT guards 去重，按 DOMAIN / DOMAIN-SUFFIX / DOMAIN-KEYWORD 的实际语义核对；检查来源例外规则。
4. 只把无路径、无条件的 `||domain^` 作为域名级候选。带 `$third-party`、`$domain`、资源类型或 path 的规则，必须保留原始限制，不能改成整个域名封锁。
5. 保存 `docs/reviews/YYYY-MM-DD.md` 研究报告、同名 `.json` 逐域记录，以及 `rules/candidates/YYYY-MM-DD.list` 待测规则。记录来源、时间范围、覆蓋/冲突、用途证据、核验状态与不确定项。
6. 执行格式、重复、来源新增、覆盖、DIRECT/例外冲突和订阅隔离检查。候选文件不应被稳定模块自动引用。
7. DNS 查询失败不等于域名失效；来源名单收录也不等于已证明纯广告用途。缺少用途证据、接口核验或实机测试时保留待测，不合并稳定模块、不扩大 MITM、不修改 response cleaner。
8. 按本 SOP 第 3 节完成相应 App 的核心功能测试后，才提出稳定版规则修改。只提交报告或候选文件时，不递增 `AdBlock_lok.x`。

本期任务只在对话回报报告 / PR 链接，不发送邮件。没有适合新增时也应保存检查结果和重要来源修正，不能为了定期更新而叠加无依据的规则。
