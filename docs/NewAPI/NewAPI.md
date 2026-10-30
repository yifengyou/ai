# New API (大模型网关)

* 官网: <https://www.newapi.ai/>（亦见 <https://www.newapi.pro/>）
* 文档: <https://docs.newapi.ai/zh/docs>
* 源码: <https://github.com/QuantumNous/new-api>
* Docker: <https://hub.docker.com/r/calciumion/new-api>
* DeepWiki: <https://deepwiki.com/QuantumNous/new-api>

New API 是一款**面向应用、Agent 和团队的自托管 AI 网关**。它把不同厂商的模型服务接入统一入口，在同一套 Web 控制台中管理渠道（上游提供者）、访问权限、用量与成本。slogan 是"新一代大模型网关与 AI 资产管理系统"。

它由 **锟腾科技（QuantumNous）** 开发，对 OpenAI、Anthropic Messages、Google Gemini 三类 API **完全兼容**，支持 30+ AI 服务商、100+ 模型。

### 🤔 核心定位

New API 解决的是"**多模型、多账号、多团队的统一接入与治理**"问题：

*   **统一入口**：你的应用/客户端只需对接 New API 一个地址，由它转发到上游各厂商。客户端永远看不到上游真实密钥，只用 New API 签发的令牌。
*   **用量与成本**：对每次调用计费、配额、分组权限，把"个人/团队/企业"的 AI 资产管起来。
*   **自用/团队内部/企业私有化**：默认面向自托管部署，而非公开 SaaS。

### 🔗 与 One API 的关系

New API 是基于 **One API**（<https://github.com/songquanpeng/one-api>，MIT 许可）的**二次开发（fork）**，在其基础上新增了全新 UI、Midjourney/Suno 支持、Rerank、Realtime API、插件系统、数据看板、成本核算等大量能力。

| 项目 | 许可证 | 备注 |
| :--- | :--- | :--- |
| One API | MIT | 上游原版 |
| New API | **AGPL-3.0** | 衍生版，功能更丰富 |

> ⚠️ AGPL-3.0 比 MIT 严格：修改后的网络服务也需开源。AGPLv3 第 7 条附加条款要求保留作者署名 "Frontend design and development by New API contributors." 及指向 <https://github.com/QuantumNous/new-api> 的可见链接。无法使用 AGPLv3 的组织可联系 support@quantumnous.com 获取商业授权。

### ✨ 主要特性

| 领域 | 能力 |
| :--- | :--- |
| **模型接入** | OpenAI Chat Completions / Responses、Anthropic Messages、Gemini API；流式、工具调用、推理、多模态输入 |
| **渠道调度** | 模型映射、渠道优先级与权重、重试、渠道亲和、多上游密钥 |
| **用量与成本** | 配额、订阅、用量日志、缓存计费、按表达式分档计价 |
| **访问控制** | 用户、分组、细粒度权限、API Key 限制；OAuth/OIDC、Passkey、2FA、会话管理 |
| **异步任务** | 用于图片/视频/任务的 JavaScript 插件；任务状态与输出获取 |
| **Web 控制台** | 配置渠道/模型、查看用量与审计日志、模型 Playground；多语言（简中/繁中/英/法/日/俄/越） |

相对 One API 的主要增强：全新 UI、多语言、Midjourney-Proxy(Plus)、Suno、Rerank（兼容 Cohere/Jina，可对接 Dify）、OpenAI Realtime API（含 Azure）、SQLite 开箱即用、渠道加权随机、数据看板、令牌级模型范围控制、Telegram OAuth、按模型名后缀设推理强度（如 `o3-mini-high`、`claude-...-thinking`）、`thinking_to_content`（把 `reasoning_content` 转 `</think> `<think>` 标签）、模型限速、缓存计费等。

### 🌐 兼容的协议与端点

New API 对外暴露这些端点，客户端可按对应协议直接对接：

| 接口 | 端点 |
| :--- | :--- |
| OpenAI Chat / Responses | `POST /v1/chat/completions`、`POST /v1/responses` |
| Anthropic Messages | `POST /v1/messages` |
| Gemini | `POST /v1beta/models/{model}:generateContent`、`POST /v1beta/models/{model}:streamGenerateContent` |
| Realtime / Responses（WebSocket） | `GET /v1/realtime`、`GET /v1/responses`（WebSocket 升级） |
| 图片 / 音频 | `/v1/images/generations`、`/v1/images/edits`、`/v1/audio/speech`、`/v1/audio/transcriptions`、`/v1/audio/translations` |
| Embeddings / Rerank | `POST /v1/embeddings`、`POST /v1/rerank` |
| 任务插件 | `POST /v1/tasks/{pluginKey}`、`GET /v1/tasks/{taskId}` |

内部 `relaykit/` 模块负责 OpenAI Chat、Responses、Anthropic Messages、Gemini 四种文本协议之间的请求/响应/流式转换。

### 🏗️ 上游与下游的概念

```
                          New API 网关
客户端 ──(New API 令牌)──►  ├─ 渠道(OpenAI)   ──(上游真实Key)──► OpenAI
                          ├─ 渠道(Anthropic) ──(上游真实Key)──► Claude
                          ├─ 渠道(Gemini)    ──(上游真实Key)──► Google
                          └─ 渠道(国产模型)   ──(上游真实Key)──► 通义/DeepSeek/…
```

*   **上游 = 渠道（Channels）**：你拥有真实 API Key 的 LLM 提供者。在控制台把它们配成"渠道"。
*   **下游 = 令牌/客户端（Tokens）**：New API 签发给应用的 `sk-...` 密钥。客户端只使用令牌，不接触上游密钥。
*   **分组（Groups）**：链接机制——令牌所在分组只能使用同分组的渠道，实现多租户访问控制。
*   **模型映射**：可重映射模型名（如客户端请求 `gpt-4`，路由到另一个上游模型）。
*   **调度流程**：`客户端(带令牌) → New API → 按 分组+模型+优先级+权重 选渠道 → 上游提供者`。

### 📦 支持的提供者与模型

按源码 `relay/channel/` 适配器目录统计：

**国际提供者**：OpenAI、Anthropic(Claude)、Google Gemini、Google Vertex AI、Google PaLM(旧)、AWS Bedrock、Azure OpenAI、Cloudflare Workers AI、Cohere、Mistral AI、Perplexity、xAI(Grok)、OpenRouter、Replicate、Jina AI、Ollama(本地)、Xinference(本地)、OpenAI Codex。

**国产大模型**：

| 适配器 | 提供者 | 中文名 |
| :--- | :--- | :--- |
| `ali` | Alibaba Qwen | 通义千问（阿里云百炼） |
| `deepseek` | DeepSeek | 深度求索 |
| `zhipu` / `zhipu_4v` | Zhipu AI (GLM) | 智谱 AI（ChatGLM） |
| `baidu` / `baidu_v2` | Baidu ERNIE | 百度文心一言 |
| `xunfei` | iFlytek Spark | 讯飞星火 |
| `tencent` | Tencent Hunyuan | 腾讯混元 |
| `moonshot` | Moonshot (Kimi) | 月之暗面 |
| `minimax` | MiniMax | — |
| `lingyiwanwu` | Yi | 零一万物 |
| `volcengine` | Volcengine (Doubao) | 火山引擎（字节跳动豆包） |
| `jimeng` | Jimeng | 即梦（字节跳动，图片生成） |
| `siliconflow` | SiliconFlow | 硅基流动 |
| `ai360` | 360 AI | 360 智脑 |
| `coze` | Coze | 扣子（字节跳动） |
| `dify` | Dify | Dify 工作流 |

**其他**：`advancedcustom`（高级自定义）、`newapi`（New API 链式转发）、`task`（异步任务，如 Midjourney/Suno）等。

### 🧩 已验证对接的客户端

Cherry Studio、DeepChat、AionUi、AstrBot、LangBot、LunaTranslator、OpenClaw、**Claude Code**、**OpenAI Codex CLI**、Factory Droid CLI 等。对接方式：把客户端的 Base URL 指向 New API，用 New API 令牌作为 API Key。

### 🛠️ 技术栈

*   **后端**：Go + Gin
*   **前端**：React 19、TypeScript、Rsbuild、TanStack、Tailwind CSS 4（用 Bun 构建）
*   **桌面壳**：Electron
*   架构：`router/` → `middleware/` → `controller/`(HTTP) → `relay/`(上游适配器) → `service/`/`model/`(业务) → `relaykit/`(协议转换) → `plugins/tasks/`(JS 任务插件)

### 📊 与同类对比

| 项目 | 定位 | 许可证 | 特色 |
| :--- | :--- | :--- | :--- |
| **New API** | 自托管 AI 网关 + 资产管理 | AGPL-3.0 | 多协议兼容、计费/配额、UI 完善、国产模型丰富 |
| One API | LLM API 代理/分发 | MIT | 上游原版，功能精简 |
| LiteLLM | Proxy + SDK | MIT | Python 生态，SDK 导向 |

---

> 📖 进一步阅读：[部署](部署.md)
>
> 本文以官方文档 <https://docs.newapi.ai/zh/docs> 为准。
