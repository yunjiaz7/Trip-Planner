# 安装 uv 工具说明

## 问题

测试时发现 `uvx` 命令未找到，这是因为系统没有安装 `uv` 工具。

`uv` 是一个快速的 Python 包管理器和项目管理工具，由 Astral 开发。

## 安装方法

### macOS / Linux

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

安装后，需要重新加载shell配置：
```bash
source ~/.bashrc  # 或 source ~/.zshrc
```

### 验证安装

```bash
uvx --version
```

应该看到类似输出：
```
uvx 0.x.x
```

## 为什么需要 uv？

MCP (Model Context Protocol) 服务器 `amap-mcp-server` 需要通过 `uvx` 命令运行。

`uvx` 是 `uv` 工具的一部分，用于运行 Python 包而不需要安装到系统中。

## 替代方案（如果无法安装 uv）

如果无法安装 `uv`，可以考虑：

1. **使用 MCP Python SDK**（如果存在）
2. **直接调用高德地图API**（绕过MCP服务器）
3. **使用其他MCP客户端实现**

但目前最简单的方案是安装 `uv`。

## 参考链接

- uv 官网: https://github.com/astral-sh/uv
- 安装文档: https://github.com/astral-sh/uv#installation
