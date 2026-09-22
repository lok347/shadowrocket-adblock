# Shadowrocket AdBlock

Lok 自用的 Shadowrocket 去广告规则维护仓库。

当前稳定基线：**GY AdBlock v6.2-lok.1**

## 来源与维护关系

- 上游作者：Y123456-hzy
- 上游 Gist：https://gist.github.com/Y123456-hzy/dd342a1a61daf8c250b112faa1381918
- 本仓库维护者：lok347
- 本仓库以稳定、自用、低误杀为优先，不保证与上游逐次同步。

> 本仓库不会机械合并上游更新。任何上游变化应先分析误杀、App 启动依赖、MITM 范围和脚本行为，再进入稳定版。

## Shadowrocket 导入

稳定模块：

https://raw.githubusercontent.com/lok347/shadowrocket-adblock/main/Shadowrocket-AdBlock.sgmodule

模块引用的响应清理脚本：

https://raw.githubusercontent.com/lok347/shadowrocket-adblock/main/scripts/gy-startup-ads-clean.js

## 维护原则

规则按风险从低到高分层：

1. **DIRECT guards**：保护 SDK 握手、配置和 App 启动依赖，必须位于 REJECT 规则之前。
2. **社区 RULE-SET**：继续引用 AWAvenue 作为大范围广告/追踪域名基础库。
3. **静态 fallback**：上游规则集下载失败时仍可屏蔽高置信广告域名。
4. **URL Rewrite**：只针对已经确认的广告接口，不直接封锁整个 SDK 域名。
5. **Response Cleaner**：仅处理 allowlist 路由和强广告特征；未知接口、非 JSON 或未修改响应保持原样。

## 分支策略

- `main`：稳定版，Shadowrocket 只订阅这里。
- `dev`：新规则、兼容修复与上游同步测试。

正常维护流程：

`问题/上游更新 -> dev 修改 -> Diff/验证 -> main`

## 反馈一个广告问题时需要什么

最好提供：

- App 名称与版本
- 广告出现位置（开屏 / 信息流 / 弹窗等）
- Shadowrocket PacketTunnel / HTTP 日志
- 相关请求域名、URL 或响应片段
- 加规则后是否出现启动慢、页面空白、功能失效

不要只因为域名名称看起来像广告就直接 REJECT。

## 文件

- `Shadowrocket-AdBlock.sgmodule`：稳定模块
- `scripts/gy-startup-ads-clean.js`：响应清理脚本
- `CHANGELOG.md`：本仓库变更记录
- `docs/MAINTENANCE.md`：维护 SOP

## 安全说明

使用 MITM 前需要在 iOS 中安装并完全信任 Shadowrocket CA。MITM 会解密匹配域名的 HTTPS 流量，因此应严格控制 hostname 范围，只添加确实需要 Rewrite / Script 的域名。

## Attribution

本仓库基线规则与响应清理逻辑源自 Y123456-hzy 的 GY AdBlock v6.2。本仓库保留上游来源并在此基础上做自用维护。
