# Shadowrocket AdBlock

Lok 自用的 Shadowrocket 去广告规则维护仓库。

当前稳定版本：**AdBlock_lok.20261007**

当前 upstream 基线：**GY AdBlock v6.2**

## 来源与维护关系

- 上游作者：Y123456-hzy
- 上游 Gist：https://gist.github.com/Y123456-hzy/dd342a1a61daf8c250b112faa1381918
- 本仓库维护者：lok347
- 本仓库以稳定、自用、低误杀为优先，不保证与上游逐次同步。

> 本仓库不会机械合并上游更新。任何上游变化应先分析误杀、App 启动依赖、MITM 范围和脚本行为，再进入稳定版。

## Shadowrocket 导入

本期日期文件：

https://raw.githubusercontent.com/lok347/shadowrocket-adblock/main/Shadowrocket-AdBlock-lok.20261007.sgmodule

固定订阅入口（每次与最新日期文件同步）：

https://raw.githubusercontent.com/lok347/shadowrocket-adblock/main/Shadowrocket-AdBlock.sgmodule

模块引用的响应清理脚本：

https://raw.githubusercontent.com/lok347/shadowrocket-adblock/main/scripts/adblock-clean.js

## iOS 捷径与自动更新

**可以自动跟随本仓库更新。** 使用固定链接添加远程模块，再开启 Shadowrocket 的模块自动更新；本仓库每两周维护一次，手机按设定间隔检查新版。

### 添加现成 iOS 捷径

**[下载 AdBlock_lok 更新入口捷径](https://github.com/lok347/shadowrocket-adblock/raw/refs/heads/main/shortcuts/AdBlock-lok-update.shortcut)**

<a href="https://github.com/lok347/shadowrocket-adblock/raw/refs/heads/main/shortcuts/AdBlock-lok-update.shortcut"><img src="docs/assets/adblock-shortcut-download-qr.svg" width="240" alt="下载完整 AdBlock_lok 捷径的二维码"></a>

用 Safari 点链接或扫码下载，打开下载的 `.shortcut` 文件，然后在「快捷指令」中按 **添加快捷指令**。动作和本仓库的固定模块链接均已预填，**无需自行创建动作或修改地址**。如果浏览器只保存文件，到「文件 → 下载」中点开它即可。

运行捷径会打开 Shadowrocket 的模块安装/导入入口，可能仍需确认。自动后台更新按下方设置开启一次。此处提供完整的已签名捷径文件；目前未提供 iCloud 分享链接，尚未进行 iPhone 实机导入测试。

### 链接与 QR Code

- [固定模块订阅链接](https://raw.githubusercontent.com/lok347/shadowrocket-adblock/main/Shadowrocket-AdBlock.sgmodule)：始终指向最新稳定版，适合自动更新。
- [iOS 捷径安装与自动更新说明](docs/IOS-AUTO-UPDATE.md)：安装现成捷径及开启后台自动更新。

| 固定订阅链接 | Shadowrocket 模块导入入口 |
| --- | --- |
| <img src="docs/assets/adblock-subscription-qr.svg" width="240" alt="固定模块订阅链接二维码"> | <img src="docs/assets/adblock-shortcut-qr.svg" width="240" alt="Shadowrocket 模块导入入口二维码"> |
| 扫码获取 HTTPS 链接，再添加为远程模块。 | 支持自定义 URL Scheme 的扫码工具可打开 Shadowrocket；不识别时按捷径说明复制 URL。 |

### 开启自动更新

1. 在 Shadowrocket 中进入 **配置 → 模块 → ＋**，粘贴固定订阅链接，下载并启用模块。
2. 进入 **设置 → 更新 → 模块**，开启 **自动后台更新**，建议更新间隔设为 **1 天**。若找不到此项，先升级 Shadowrocket。
3. 在 iOS **设置 → 通用 → 后台 App 刷新** 中允许 Shadowrocket 后台刷新。

使用带日期的链接会一直读取该期文件；要跟随以后更新，请使用固定链接。后台更新由 iOS 调度，不保证在某个整点执行；重启手机或手动结束应用后，请重新打开一次 Shadowrocket。

### 手动创建捷径（备用）

在「快捷指令」中新建 **AdBlock_lok 更新入口**，依次添加 **URL** 和 **打开 URL** 两个动作。URL 内容如下，可复制使用：

```text
shadowrocket://install?module=https%3A%2F%2Fraw.githubusercontent.com%2Flok347%2Fshadowrocket-adblock%2Fmain%2FShadowrocket-AdBlock.sgmodule
```

该捷径用于打开远程模块安装/导入入口，可能需要在 Shadowrocket 中确认；**扫码或运行此捷径本身不等于开启后台自动更新**。无人值守更新请使用上面的「模块自动后台更新」设置。

参考：[Shadowrocket 开发者更新频道](https://t.me/s/ShadowrocketNews?after=1267) · [社区使用手册：自动更新](https://github.com/LOWERTOP/Shadowrocket#自动更新) · [社区使用手册：URL Schemes](https://github.com/LOWERTOP/Shadowrocket#url-schemes)。

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

无条件域名增量完成来源、覆盖和冲突检查后可发布，并记录未实机测试状态；涉及混合业务接口、脚本或 MITM 的改动仍按维护 SOP 做兼容性验证。

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

- `Shadowrocket-AdBlock-lok.20261007.sgmodule`：本期稳定模块，日期格式 `YYYYMMDD`
- `Shadowrocket-AdBlock.sgmodule`：固定订阅入口，与最新日期文件内容一致
- `scripts/adblock-clean.js`：响应清理脚本
- `CHANGELOG.md`：本仓库变更记录
- `docs/MAINTENANCE.md`：维护 SOP
- `docs/IOS-AUTO-UPDATE.md`：iOS 自动更新与捷径设置说明
- `shortcuts/AdBlock-lok-update.shortcut`：预填固定模块链接的已签名 iOS 捷径
- `shortcuts/AdBlock-lok-update.plist`：捷径动作源文件，供维护检查

## 安全说明

使用 MITM 前需要在 iOS 中安装并完全信任 Shadowrocket CA。MITM 会解密匹配域名的 HTTPS 流量，因此应严格控制 hostname 范围，只添加确实需要 Rewrite / Script 的域名。

## Attribution

本仓库基线规则与响应清理逻辑源自 Y123456-hzy 的 GY AdBlock v6.2。本仓库保留上游来源并在此基础上做自用维护。
