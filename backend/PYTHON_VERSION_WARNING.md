# Python版本要求说明

## ⚠️ 重要提示

**本项目需要 Python 3.10 或更高版本**

当前检测到您的系统使用的是 **Python 3.9.6**，这会导致以下问题：

1. **pydantic 2.x 无法安装** - 需要 Python 3.10+
2. **某些LangChain依赖可能不兼容** - 推荐使用 Python 3.10+

## 解决方案

### 方案1：升级Python版本（推荐）

#### macOS (使用Homebrew)
```bash
# 安装Python 3.10或更高版本
brew install python@3.11

# 或者使用pyenv管理多个Python版本
brew install pyenv
pyenv install 3.11.0
pyenv global 3.11.0
```

#### 验证安装
```bash
python3 --version  # 应该显示 3.10.x 或更高
```

### 方案2：使用虚拟环境（如果已安装Python 3.10+）

```bash
# 创建虚拟环境（使用Python 3.10+）
python3.10 -m venv venv
# 或
python3.11 -m venv venv

# 激活虚拟环境
source venv/bin/activate

# 验证版本
python --version

# 安装依赖
pip install -r requirements.txt
```

### 方案3：降级依赖（不推荐，可能影响功能）

如果必须使用Python 3.9，可以尝试：

```bash
# 使用pydantic 1.x（不推荐，可能不兼容）
pip install "pydantic<2.0.0"
```

但这种方式可能导致其他依赖不兼容，**强烈建议升级到Python 3.10+**。

## 检查Python版本

```bash
python3 --version
```

## 推荐配置

- **Python版本**: 3.10 或 3.11（推荐）
- **包管理器**: pip 或 uv（如果已安装）

## 相关文档

- Python官方下载: https://www.python.org/downloads/
- pyenv文档: https://github.com/pyenv/pyenv
