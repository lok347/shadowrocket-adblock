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

- upstream 原始版本：例如 `v6.2`
- 本仓库稳定版本：例如 `v6.2-lok.1`
- 同一 upstream 基线上，每次本地稳定修订递增末位：
  - `v6.2-lok.2`
  - `v6.2-lok.3`
- upstream 升级后重新起基线：
  - `v6.3-lok.1`

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
