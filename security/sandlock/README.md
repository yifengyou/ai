# sandlock

* 源码仓库：<https://github.com/multikernel/sandlock>

Sandlock 是一个为 AI Agent 量身定制的、策略优先的轻量级安全沙箱。它旨在解决当前 AI Agent 安全领域普遍存在的过度设计问题，摒弃了容器、微虚拟机等重量级隔离方案，转而采用基于策略的细粒度访问控制，以更高效、更低成本的方式保障 Agent 的运行安全。

### 🤖 Sandlock 是什么？

Sandlock 是一个用 Rust 编写的开源安全沙箱工具，专为 AI Agent 场景设计。它并非一个通用的虚拟化平台，而是一个聚焦于解决 Agent 特定威胁模型的运行时环境。

与动辄需要数百毫秒启动的容器或微虚拟机不同，Sandlock 利用 Linux 内核的 Landlock、seccomp-bpf 等非特权特性，在毫秒级（约 5ms）内即可为 Agent 或其调用的每个工具创建一个受约束的运行环境。它不依赖任何外部守护进程，也不需要 root 权限，是一个单一的可执行文件，极大地简化了部署和运维。

### 🛡️ Sandlock 有什么作用？

Sandlock 的核心作用是通过实施最小权限原则，保护系统资源免受 AI Agent 可能带来的风险，包括由提示词注入攻击引发的恶意操作和 Agent 自身的误操作。它通过以下几个层面实现这一目标：

1.  **基于策略的细粒度访问控制**
    Sandlock 认为隔离不等于安全，真正的安全来自于精确的策略。它默认拒绝所有对文件系统、网络和系统调用的访问，开发者必须显式地通过白名单授权。例如，你可以精确指定 Agent 只能读取 `/src` 目录，只能向 `api.openai.com` 发送 POST 请求，而无需将整个项目目录挂载给它。

2.  **按需隔离，而非一刀切**
    Sandlock 颠覆了“一个沙箱装所有工具”的模式。它支持在每次工具调用时创建独立的沙箱。这意味着，一个用于浏览网页的工具可以拥有网络权限但被禁止写入磁盘，而一个用于操作文件的工具则可以被禁止联网。这种按调用隔离的粒度，有效限制了单个工具被攻破后可能造成的损失。

3.  **消除提示词注入风险**
    Sandlock 支持一种“仅执行 Agent”（Execute-Only Agent, XOA）的架构模式。在这种模式下，LLM 仅负责生成代码，而生成的代码在独立的沙箱阶段执行，其输出直接返回给用户，不会回流到 LLM 的上下文中。从架构上彻底切断了攻击者通过注入恶意指令来控制 Agent 的路径。

4.  **极简且安全的架构**
    Sandlock 完全在用户空间运行，不需要 Docker 守护进程、kubelet 或任何需要 root 权限的组件。这不仅消除了这些特权组件本身可能带来的攻击面，也意味着 Sandlock 可以在任何普通用户权限下运行，大大降低了部署门槛和安全风险。

### 🚀 快速上手

Sandlock 提供了简洁的命令行接口和多种语言的 SDK，可以轻松集成到现有工作流中。

#### 命令行使用示例

以下是一些常见的命令行用法：

*   **基础运行**：限制 Agent 只能读取系统库，写入 `/tmp` 目录，并仅允许连接指定的 API 主机。
    ```bash
    sandlock run -r /usr -r /lib -r /etc -w /tmp \
      --net-allow-host api.anthropic.com -- python3 agent.py
    ```

*   **HTTP 级 ACL**：配置精确到 HTTP 方法和路径的访问控制规则。
    ```bash
    sandlock run \
      --http-allow "POST api.openai.com/v1/chat/completmos" \
      --http-deny "* */admin/*" \
      -r /usr -r /lib -r /etc -- python3 agent.py
    ```

*   **资源限制**：限制内存、CPU 和执行时间。
    ```bash
    sandlock run -m 512M -P 20 -t 30 -- ./compute.sh
    ```

*   **写时复制 (COW) 文件系统**：所有写操作都会被拦截，仅在任务成功完成后统一提交，非常适合需要保证原子性的任务。
    ```bash
    sandlock run --workdir /opt/project -r /usr -r /lib -- python3 task.py
    ```

*   **Dry-run 模式**：预览所有文件变更，但不实际执行。
    ```bash
    sandlock run --dry-run --workdir . -w . -r /usr -r /lib -- make build
    ```

#### Python API 使用示例

Sandlock 也提供了 Python API，方便在代码中直接调用：

```python
from sandlock import Sandbox, Policy

policy = Policy(
    fs_readable=["/usr", "/lib", "/etc"],
    fs_writable=["/tmp/sandbox"],
    net_allow_hosts=["api.anthropic.com"],
)

result = Sandbox(policy).run(["python3", "agent.py"])
```

通过上述方式，开发者可以快速为 AI Agent 构建一个安全、高效且低成本的运行环境。

