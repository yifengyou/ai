# OpenClaw (个人 AI 智能体)

* 官网: <https://openclaw.ai/>
* 文档: <https://docs.openclaw.ai/>
* 源码: <https://github.com/openclaw/openclaw>
* GitHub 组织: <https://github.com/openclaw>
* 技能市场 ClawHub: <https://clawhub.ai/>
* 社区 Discord: <https://discord.gg/clawd>

OpenClaw 是一款**自托管、本地优先**的开源个人 AI 智能体（AI Agent），slogan 是 "The AI that actually does things"（真正能干活的 AI）。它由 [OpenClaw Foundation](https://openclaw.org/)（独立 501(c)(3) 基金会）维护，MIT 许可证，无付费层、无托管服务、无代币。

它本质上是一个**网关（Gateway）**：在自己机器上运行一个常驻进程，把常用的聊天应用（Discord、Slack、Telegram、WhatsApp、iMessage、Signal、Microsoft Teams、Matrix、Google Chat、Zalo、微信等，通过通道插件扩展）连接到 AI 编码/任务智能体。你从任何聊天界面发消息，网关就把请求交给智能体执行，再把结果回传。

### 🤔 核心定位

OpenClaw 不是 IDE 替代品，而是一个**助手与协调层**。快速直接的编码循环仍用 Claude Code / Codex CLI / OpenCode；OpenClaw 负责持久记忆、跨设备访问与工具编排——你可以在手机上发消息让它改服务器上的代码、查日历、跑脚本。

它是一套"即开即用的完整智能体运行时"，与 AutoGen、CrewAI 等开发者库不同：内置 20+ 消息平台接入、子智能体编排、主动行为调度与数千社区技能生态。

### ✨ 主要特性

*   **自托管 (Self-hosted)**
    跑在你自己的硬件上，数据留在自己手里。同一套网关既能当个人助手跑在笔记本上，也能作为[团队共享部署](https://docs.openclaw.ai/start/teams)跑在服务器上，区别仅在配置。

*   **多通道 (Multi-channel)**
    一个网关进程同时服务所有已配置的通道插件。官方插件按需安装，社区还覆盖 Matrix、Nostr、Twitch、Zalo 等。

*   **智能体原生 (Agent-native)**
    为编码智能体设计，内置工具使用、会话、记忆与多智能体路由。可以把 Claude Code、Codex CLI、OpenCode 等作为 agent harness 插件来驱动。

*   **多智能体路由 (Multi-agent routing)**
    按通道、账号、发送者把入站消息路由到隔离的智能体，各自有独立工作区与每智能体会话。

*   **多形态 (Multi-form)**
    除 CLI 与 Web Control UI（`openclaw dashboard`）外，还有 macOS 菜单栏应用、Windows Hub 应用、iOS/Android 节点应用。注意：官方推荐用内置 Control UI，第三方 WebClaw 仅支持旧协议 v3，无法连接当前网关（需 v4）。

*   **本地模型可选 (Local-only)**
    可配置本地模型，让所有数据都不出设备。

### 🏗️ 架构概览

```
聊天应用 (WhatsApp/Telegram/Slack/...)
        │  消息
        ▼
   OpenClaw Gateway  ←── 单一长驻进程，默认监听 127.0.0.1:18789
   │  ├─ 通道插件 (Baileys/grammY/...)
   │  ├─ 智能体运行时 (Pi，工具流 + 块流)
   │  ├─ 会话 / 记忆 / 队列 / 调度
   │  └─ WebSocket API (控制面)
        ▲            ▲            ▲
        │            │            │
   CLI / Web UI   macOS 应用   iOS/Android/headless 节点 (role: node)
```

* **Gateway（守护进程）**：唯一持有所有消息会话的进程；维护提供者连接，暴露类型化 WebSocket API，校验入站帧，发出 `agent`/`chat`/`presence`/`health`/`heartbeat`/`cron` 等事件。一台主机一个网关。
* **控制面客户端**：macOS 应用、CLI、Web UI、自动化各持一条 WS 连接，发送 `health`/`status`/`send`/`agent` 等请求并订阅事件。
* **节点（Nodes）**：macOS/iOS/Android/无头设备以 `role: node` 连接到同一个 WS 服务，提供设备能力（`camera.*`、`screen.record`、`location.get` 等）。配对基于设备，审批记录在设备配对库。
* **协议**：WebSocket 文本帧 + JSON。首帧必须是 `connect`；之后请求 `{type:"req",id,method,params}` → 响应 `{type:"res",id,ok,payload|error}`，事件 `{type:"event",event,payload,...}`。带副作用的 `send`/`agent` 需幂等键。
* **远程访问**：首选 Tailscale/VPN，或 SSH 隧道 `ssh -N -L 18789:127.0.0.1:18789 user@gateway-host`；可对 WS 启用 TLS + 可选 pinning。

### 🛠️ 核心能力

1.  **工具与技能 (Tools & Skills)**
    工具是智能体能调用的能力（浏览器、exec、网页搜索等）；技能是教智能体"如何与何时使用工具"的 Markdown 指令文件（`SKILL.md`）。技能可从 ClawHub 安装，也能由智能体自己通过 Skill Workshop 学习并保存（带版本与撤销）。

2.  **插件 (Plugins)**
    插件可随附自己的技能与工具（在 `openclaw.plugin.json` 列 `skills` 目录）。浏览器插件就随附 `browser-automation` 技能。

3.  **记忆与会话 (Memory & Sessions)**
    持久记忆与跨会话工作区。DM 默认共享智能体主会话，每个群聊各自一个会话。会话快照在会话开始时生成并在刷新触发时更新。

4.  **主动行为 (Proactive Behavior)**
    智能体不只能被动等指令：通过心跳（Heartbeat）与定时任务（cron）机制自主发起行动；七层权限策略栈（全局→智能体→群聊→子智能体）确保自主行为不越界。

5.  **子智能体 (Sub-agents)**
    隔离、非阻塞、可配置深度的并行任务执行能力。

### 📊 与同类工具对比

| 工具 | 定位 | 运行位置 | 界面 | 开源 |
| :--- | :--- | :--- | :--- | :--- |
| **OpenClaw** | 通用个人智能体/协调层 | 你的硬件 | Control UI、应用、20+ 聊天通道 | ✅ MIT |
| Claude Code / Codex CLI | 编码智能体 | 你的终端 | 终端、IDE | Codex CLI 是 |
| Cursor / GitHub Copilot | IDE 助手 | 厂商云 + IDE | IDE | ❌ |
| Open Interpreter | CLI 智能体 | 你的机器 | 终端 | ✅ |
| CrewAI / AutoGen | 多智能体框架（库） | 你的代码里 | 你的应用 | ✅ |

> OpenClaw 也能把 Claude Code 与 Codex 当作 agent harness 来驱动，二者互补而非互斥。

### ⚠️ 安全须知

*   **把入站消息当不可信输入**。可发 DM 的通道默认会配对未知发送者；用 `openclaw pairing approve <channel> <code>` 审批配对请求。
*   工具默认在主会话的**宿主机**上运行，除非配置沙箱。使用前务必阅读[安全指南](https://docs.openclaw.ai/gateway/security)。
*   第三方技能视为**不可信代码**，启用前先阅读；对不可信输入与高风险工具优先用沙箱运行。
*   把凭据放在技能内容之外，用 `skills.entries.<name>.apiKey` / `env` 注入。

---

> 📖 进一步阅读：[部署](部署.md) · [SKILLS编写](SKILLS编写.md)
>
> 本文以官方文档 <https://docs.openclaw.ai/> 为准。
