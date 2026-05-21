# Introduction

**Bubblewrap（`bwrap`）** 是一个基于 Linux 命名空间（namespaces）实现的轻量级、非特权沙盒工具，主要用于安全隔离应用程序。它被广泛用于 Flatpak 等项目中，以提供应用级别的容器化和权限限制。

---

### 一、基本介绍

- **项目名称**：Bubblewrap（命令行工具名为 `bwrap`）
- **开发语言**：C
- **依赖机制**：Linux 内核特性（如 user namespace、mount namespace、pid namespace 等）
- **主要用途**：
    - 创建受限的运行环境（类似 chroot，但更安全灵活）
    - 隔离半信任程序（如网页浏览器组件、图像/视频缩略图生成器等）
    - 在不同库环境中运行程序（例如 Flatpak 运行时）

---

### 二、核心特性

1. **无需 root 权限**  
   利用 Linux 的用户命名空间（user namespaces），普通用户即可创建沙盒环境。

2. **最小化攻击面**  
   默认情况下，沙盒内几乎没有任何文件系统挂载，只有显式指定的内容才可访问。

3. **高度可控**  
   可通过命令行参数精细控制：
    - 挂载点（`--bind`, `--ro-bind`, `--dev`, `--proc` 等）
    - 用户/组映射（`--uid`, `--gid`）
    - 网络、IPC、PID 隔离（`--unshare-net`, `--unshare-ipc`, `--unshare-pid`）
    - 文件系统只读/写保护

4. **与 Flatpak 深度集成**  
   Flatpak 使用 `bwrap` 作为其底层沙盒引擎，确保应用在隔离环境中运行。

---

### 三、典型使用示例

```bash
# 创建一个只包含 /bin 和 /lib 的最小环境，并运行 bash
bwrap \
  --ro-bind /bin /bin \
  --ro-bind /lib /lib \
  --ro-bind /lib64 /lib64 \
  --dev /dev \
  --proc /proc \
  --unshare-pid \
  --unshare-ipc \
  --unshare-net \
  bash
```

此命令会启动一个隔离的 shell，无法访问主系统的 `/home`、`/etc` 等目录，也无法与外部网络通信。

---

### 四、安装方式

大多数 Linux 发行版已包含 `bubblewrap`：

- **Debian/Ubuntu**：
  ```bash
  sudo apt install bubblewrap
  ```
- **Fedora/RHEL**：
  ```bash
  sudo dnf install bubblewrap
  ```
- **Arch Linux**：
  ```bash
  sudo pacman -S bubblewrap
  ```

> 注意：内核需启用 **user namespaces**（现代发行版默认开启）。

---

### 五、安全与限制

- **优势**：轻量、快速启动、无需守护进程、符合 POSIX 标准。
- **局限**：
    - 不提供完整的容器功能（如 cgroups 资源限制需配合其他工具）
    - 依赖内核支持，老旧系统可能无法使用
    - 若配置不当（如挂载了敏感目录），仍可能存在逃逸风险

---

### 六、项目资源

- **官方仓库**（GitHub 镜像）：  
  https://github.com/containers/bubblewrap  
  （搜索结果中提到的 GitCode 镜像：https://gitcode.com/gh_mirrors/bub/bubblewrap）

- **文档与手册**：可通过 `man bwrap` 查看本地帮助。

---

### 总结

`bubblewrap` 是一个强大而简洁的沙盒工具，适合需要轻量级隔离的场景。它不是 Docker 那样的完整容器方案，但在安全性、性能和易用性之间取得了良好平衡，特别适合作为桌面应用（如 Flatpak）或自动化脚本的安全运行环境。

