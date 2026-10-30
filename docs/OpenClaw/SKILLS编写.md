# SKILLS 编写

> 本文整理自 OpenClaw 官方 [Skills](https://docs.openclaw.ai/tools/skills) 与 [Creating skills](https://docs.openclaw.ai/tools/creating-skills) 文档。

Skills（技能）是教智能体**如何与何时使用工具**的 Markdown 指令文件。每个技能是一个目录，内含带 YAML frontmatter 与 Markdown 正文的 `SKILL.md`。OpenClaw 加载内置技能及任何本地覆盖，并在加载时按环境、配置与二进制存在性过滤。

> OpenClaw 遵循 [AgentSkills](https://agentskills.io) 规范。frontmatter 先按 YAML 解析；失败则回退到单行解析器。嵌套 `metadata` 块会被扁平化为 JSON 字符串再按 JSON5 解析。

## 一、创建第一个技能

```bash
# 1. 建技能目录（放在工作区 skills/ 下）
mkdir -p ~/.openclaw/workspace/skills/hello-world

# 也可分子目录归组——技能名仍由 frontmatter 决定，不是目录路径
mkdir -p ~/.openclaw/workspace/skills/personal/hello-world   # 名字仍是 hello-world
```

````markdown
---
name: hello-world
description: A simple skill that prints a greeting.
---

# Hello World

When the user asks for a greeting, use the `exec` tool to run:

```bash
echo "Hello from your custom skill!"
```
````

命名规则：`name` 用小写字母、数字、连字符；保持目录名与 frontmatter `name` 一致；`description` 一行、≤160 字符（会展示给智能体与斜杠命令发现）。

```bash
# 2. 验证已加载
openclaw skills list

# 3. 测试
openclaw agent --message "give me a greeting"
# 或在聊天里直接问；用 /skill hello-world 按名显式调用
```

OpenClaw 默认监视 skills 根下的 `SKILL.md`。若监视被禁或要继续现有会话，用 `/new` 开新会话或 `openclaw gateway restart` 让智能体拿到刷新后的列表。

## 二、SKILL.md 格式参考

### 必填字段

| 字段 | 说明 |
| :--- | :--- |
| `name` | 唯一 slug，小写字母、数字、连字符 |
| `description` | 一行描述，展示给智能体与发现输出 |

### 可选 frontmatter

| 字段 | 默认 | 说明 |
| :--- | :--- | :--- |
| `user-invocable` | `true` | 是否作为用户斜杠命令暴露 |
| `disable-model-invocation` | `false` | 把技能排除出智能体系统提示（仍可经 `/skill` 运行） |
| `command-dispatch` | — | 设为 `tool` 时斜杠命令直接派发到工具，绕过模型 |
| `command-tool` | — | `command-dispatch: tool` 时要调用的工具名 |
| `command-arg-mode` | `raw` | 工具派发时把原始参数串原样转发 |
| `homepage` | — | macOS Skills UI 显示的"网站"URL |

### 用 `{baseDir}` 引用文件

不硬编码路径，让智能体把 `{baseDir}` 解析为技能自身目录：

```markdown
Run the helper script at `{baseDir}/scripts/run.sh`.
```

## 三、条件激活（Gating）

按依赖是否可用决定技能是否加载。通过 `metadata.openclaw`（frontmatter 里的 JSON5 对象）声明：

```markdown
---
name: gemini-search
description: Search using Gemini CLI.
metadata: { "openclaw": { "requires": { "bins": ["gemini"] }, "primaryEnv": "GEMINI_API_KEY" } }
---
```

| 键 | 说明 |
| :--- | :--- |
| `requires.bins` | 所有二进制都必须在 `PATH` 上 |
| `requires.anyBins` | 至少一个二进制在 `PATH` 上 |
| `requires.env` | 每个环境变量在进程或配置中存在 |
| `requires.config` | 每个 `openclaw.json` 路径为真 |
| `os` | 平台过滤：`["darwin"]`（或 `["macos"]`）、`["linux"]`、`["win32"]` |
| `always` | 在兼容 OS 上即使 `requires.*` 失败也包含（不覆盖 `os`） |
| `primaryEnv` | 与 `skills.entries.<name>.apiKey` 关联的环境变量名 |
| `install` | macOS Skills UI 用的安装器规格（brew/node/go/uv/download） |
| `emoji` / `homepage` | macOS Skills UI 显示的 emoji / URL |

> 三者关系：**Inventory**（是否在某根/内置源发现）→ **Readiness**（运行时能否满足声明的要求）→ **Visibility**（经智能体允许列表、调用标志、快照规则后是否暴露给所选智能体）。调试用 `openclaw skills check`。

## 四、加载顺序与优先级

文件型技能按以下来源加载，**最高优先级在前**，同名时最高源胜出：

| 优先级 | 来源 | 路径 |
| :--- | :--- | :--- |
| 1（最高） | 工作区技能 | `<workspace>/skills` |
| 2 | 项目 agent 技能 | `<workspace>/.agents/skills` |
| 3 | 个人 agent 技能 | `~/.agents/skills`（仅默认状态） |
| 4 | 托管/本地技能 | `<state-dir>/skills` |
| 5 | Workshop 技能 | `<state-dir>/agents/<agentId>/agent/workshop-skills` |
| 6 | 内置技能 | 随安装附带（含 Custodian 技能库，同层但仅系统/Custodian agent 可见） |
| 7（最低） | 额外目录 | `skills.load.extraDirs` + 插件技能 |

发现支持分组布局：`SKILL.md` 出现在配置根下任意位置（最深 6 层）即被发现；找到 `SKILL.md` 后不再向其下遍历。文件夹路径仅用于组织，技能名与斜杠命令来自 `name` frontmatter（缺失则用目录名）。

### 单 agent vs 共享

| 范围 | 路径 | 对谁可见 |
| :--- | :--- | :--- |
| 单智能体 | `<workspace>/skills` | 仅该智能体 |
| 项目-agent | `<workspace>/.agents/skills` | 仅该工作区的 agent |
| 个人-agent | `~/.agents/skills` | 用默认状态的 agent |
| 共享托管 | `<state-dir>/skills` | 该状态下所有 agent |
| Workshop | `<state-dir>/agents/<agentId>/agent/workshop-skills` | 仅该 agent |
| 额外目录 | `skills.load.extraDirs` | 该配置下所有 agent |

## 五、智能体允许列表 (Allowlist)

技能**位置**（优先级）与**可见性**（哪个智能体能用）是独立控制。用允许列表限制某智能体能看到哪些技能，与加载来源无关：

```json5
{
  agents: {
    ownership: "explicit",
    defaults: { skills: ["github", "weather"] },   // 共享基线
    entries: {
      writer: { workspace: "~/.openclaw/workspace" },      // 继承 github、weather
      docs: { skills: ["docs-search"] },                   // 整体替换 defaults
      "locked-down": { skills: [] },                       // 无技能
    },
  },
}
```

*   省略 `agents.defaults.skills` → 默认不限制。
*   省略 `agents.entries.*.skills` → 继承 `defaults`。
*   设 `agents.entries.*.skills: []` → 该 agent 无技能。
*   非空 `agents.entries.*.skills` 列表是**最终集合**，不与 defaults 合并。
*   这不是宿主 shell 授权边界；若该 agent 还能用 `exec`，需另行用沙箱、OS 用户隔离、exec 允许/拒绝列表、按资源凭据约束。

## 六、在提示中引用技能

在 Control UI 输入框输入 `$` 可搜索当前智能体可用的技能，选中会插入稳定命令名（如 `$release_notes`），不替换消息其余部分。一条消息可引用多个技能（最多 8 个）：

```text
Use $github and $release_notes to summarize this change for the release.
```

OpenClaw 对所有通道及通用网关/CLI/webhook agent 回合，从授权发送者的显式引用解析，并告知模型在行动前读取每个被引用的 `SKILL.md`。通道消息上 `/release_notes ...` 仍是独立命令形式。常见大写 shell 变量（`$HOME`/`$PATH`/`$EDITOR`）保持普通文本；用小写 `$home`/`$path`/`$editor` 引用同名技能；字面量用 `\$name` 转义。

## 七、配置覆盖与密钥注入

在 `~/.openclaw/openclaw.json` 的 `skills.entries` 下开关或配置内置/托管技能：

```json5
{
  skills: {
    entries: {
      "image-lab": {
        enabled: true,
        apiKey: { source: "env", provider: "default", id: "GEMINI_API_KEY" },
        env: { GEMINI_API_KEY: "GEMINI_KEY_HERE" },
        config: { endpoint: "https://example.invalid", model: "nano-pro" },
      },
      "coding-agent": { enabled: true },   // 内置但 opt-in
      sag: { enabled: false },
    },
  },
}
```

| 字段 | 说明 |
| :--- | :--- |
| `enabled` | `false` 即使内置/已安装也禁用。`coding-agent` 内置技能需显式 `enabled: true`，并装好 `claude`/`codex`/`opencode` 等之一且已认证 |
| `apiKey` | 便捷字段，配合 `metadata.openclaw.primaryEnv`；支持明文字符串或 SecretRef 对象 |
| `env` | agent 运行期间注入的环境变量（仅当进程未设置时） |
| `config` | 自定义每技能配置字段 |
| `allowBundled` | 仅对**内置**技能的允许列表 |

> 配置键默认匹配**技能名**；若技能声明了 `metadata.openclaw.skillKey`，则用该键。连字符名需加引号（JSON5 支持）。

⚠️ **密钥注入范围**：`env` 与 `apiKey` 注入到**宿主** agent 运行进程，**不进入沙箱**。沙箱内需另行处理（见 [sandboxed skills and env vars](https://docs.openclaw.ai/tools/skills-config#sandboxed-skills-and-env-vars)）。把密钥放技能内容之外，避免出现在提示与日志里。

## 八、Skill Workshop（智能体自学技能）

[Skill Workshop](https://docs.openclaw.ai/tools/skill-workshop) 让智能体自己保存并更新技能到 `<state-dir>/agents/<agentId>/agent/workshop-skills`。每次改动立即生效、会播报，并保存上一版以便撤销。学到的技能对其 agent 始终可见；归档可隐藏。

```bash
openclaw skills workshop list
openclaw skills workshop changes
openclaw skills workshop show hello-world
openclaw skills workshop archive hello-world --reason "Replaced by greeting"
openclaw skills workshop restore hello-world
```

也可让智能体创建/改进个人技能：其 `skill_workshop` 工具走网关授权库服务，不直接写托管修订目录。

## 九、从 ClawHub 安装与发布

[ClawHub](https://clawhub.ai) 是公共技能注册表。

### 安装 / 更新 / 校验

| 操作 | 命令 |
| :--- | :--- |
| 装到工作区 | `openclaw skills install @owner/<slug>` |
| 装外部 skills.sh 引用 | `openclaw skills install skills-sh:owner/repo/slug` |
| 从 Git 仓库装 | `openclaw skills install git:owner/repo@ref` |
| 装本地目录 | `openclaw skills install ./path/to/skill --as my-tool` |
| 为所有本地 agent 装 | `openclaw skills install @owner/<slug> --global` |
| 更新所有工作区技能 | `openclaw skills update --all` |
| 更新共享托管技能 | `openclaw skills update @owner/<slug> --global` |
| 校验信任封套 | `openclaw skills verify @owner/<slug>` |
| 打印 Skill Card | `openclaw skills verify @owner/<slug> --card` |

默认装到当前工作区 `skills/`；`--global` 装到共享 `~/.openclaw/skills`。Git/本地安装需在源根有 `SKILL.md`，slug 取自 frontmatter `name`（合法时）否则回退目录/仓库名，可用 `--as <slug>` 覆盖。`openclaw skills update` 只跟踪 ClawHub 安装；Git/本地源需重装刷新。跟踪元数据在 `.clawhub/`（旧的 `.clawdhub` 不再读取）。

### 发布

owner 是 ClawHub 发布者句柄（如 `@alice` 或 `@your-org`）：

```bash
npm i -g clawhub
clawhub login
clawhub skill publish ./path/to/hello-world     # 可加 --version / --owner
```

详见 [ClawHub Publishing](https://docs.openclaw.ai/clawhub/publishing) 与 [ClawHub CLI](https://docs.openclaw.ai/clawhub/cli)（含 `clawhub sync`、`clawhub skill rename` 等）。

## 十、快照与刷新

OpenClaw 在**会话开始时**快照可用技能并复用直到触发刷新。触发刷新的动作：安装/更新/卸载/编辑技能、影响技能的配置变更、启动或重启网关、新连上的远程节点。被动刷新靠文件系统事件（`skills.load.watch` 默认开）+ 每 30 分钟安全重扫兜底。现有会话在下一个 agent 回合拾取变更的文件型技能。

```json5
{
  skills: {
    load: {
      extraDirs: ["~/path/to/agent-scripts/skills"],
      allowSymlinkTargets: ["~/path/to/skills"],   // 信任指向根外的符号链接目标
      watch: true,                                  // 默认
    },
  },
}
```

## 十一、安全

⚠️ 把第三方技能视为**不可信代码**，启用前先读；对不可信输入与高风险工具优先沙箱运行。

*   **路径约束**：工作区/项目-agent/额外目录的技能发现只接受 realpath 在配置根内的技能，除非 `skills.load.allowSymlinkTargets` 显式信任某目标根。`skill-card.md` 须是该目录内 ≤256 KiB 的常规文件。
*   **安装策略**：`security.installPolicy` 可在技能安装继续前跑一个可信本地策略命令，覆盖 ClawHub/上传/Git/本地/更新/依赖安装器路径。
*   **密钥注入范围**：仅注入宿主进程、仅该 agent 回合，不进沙箱。

完整威胁模型与清单见 [Security](https://docs.openclaw.ai/gateway/security)。

## 十二、Token 影响

技能可用时，OpenClaw 向系统提示注入紧凑 XML 块，成本线性：基础开销（1+ 技能时固定块）+ 每技能约 97 字符 + 你的 `name`/`description`/`location` 长度（XML 转义会略增）。若超出预算 `skills.limits.maxSkillsPromptChars`，先尽量保留技能身份（name+location），再放缩短的描述。**保持 description 简短**以降低开销。

## 最佳实践

*   **简洁**：指导模型做*什么*，别教它如何当 AI。
*   **安全优先**：用 `exec` 时写不允许不可信输入任意命令注入的提示。
*   **先本地测试**：分享前用 `openclaw agent --message "..."` 验证。
*   **先逛 ClawHub**：从 [clawhub.ai](https://clawhub.ai) 找现成技能，再考虑从零写。
