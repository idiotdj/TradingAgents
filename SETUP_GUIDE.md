# TradingAgents 开发环境快速操作手册

> 创建时间: 2026-04-12

---

## 一、虚拟环境操作

### 1.1 进入虚拟环境

```bash
cd /home/idiotdj/work/code/myrepo/TradingAgents
source venv/bin/activate
```

激活成功后，命令行会显示 `(venv)` 前缀：
```
(venv) user@hostname:~/work/code/myrepo/TradingAgents$
```

### 1.2 退出虚拟环境

```bash
deactivate
```

或直接关闭终端也可以退出。

### 1.3 验证环境是否激活

```bash
# 检查 Python 路径
which python
# 应该显示: .../TradingAgents/venv/bin/python

# 检查 pip 路径
which pip
# 应该显示: .../TradingAgents/venv/bin/pip
```

---

## 二、运行 TradingAgents

### 2.1 方式一: 使用 CLI 命令（推荐）

```bash
# 确保在虚拟环境中
source venv/bin/activate

# 运行 tradingagents
tradingagents
```

### 2.2 方式二: 直接运行 Python 模块

```bash
# 确保在虚拟环境中
source venv/bin/activate

# 运行 CLI 模块
python -m cli.main
```

### 2.3 方式三: 运行示例代码

```bash
# 确保在虚拟环境中
source venv/bin/activate

# 运行 main.py 示例
python main.py
```

---

## 三、快速验证命令

### 3.1 验证安装成功

```bash
source venv/bin/activate
tradingagents --help
```

应该显示帮助信息。

### 3.2 验证 Python 环境

```bash
source venv/bin/activate
python --version
# 输出: Python 3.12.3

python -c "import tradingagents; print('TradingAgents imported successfully!')"
```

### 3.3 检查已安装的包

```bash
source venv/bin/activate
pip list | grep -E "tradingagents|yfinance|langchain|openai"
```

---

## 四、环境信息

### 4.1 项目路径
```
/home/idiotdj/work/code/myrepo/TradingAgents
```

### 4.2 虚拟环境路径
```
/home/idiotdj/work/code/myrepo/TradingAgents/venv
```

### 4.3 Python 版本
```
Python 3.12.3
```

### 4.4 主要依赖
- tradingagents: 0.2.3
- yfinance: 1.2.1
- langchain: 多个版本
- pandas: 3.0.2
- openai: 2.31.0
- anthropic: 0.94.0

---

## 五、配置 API 密钥

### 5.1 复制环境变量模板

```bash
cp .env.example .env
```

### 5.2 编辑 .env 文件

根据需要使用的 LLM 提供商，在 `.env` 文件中填入对应的 API 密钥：

```bash
# OpenAI
OPENAI_API_KEY=your_openai_key

# Google (Gemini)
GOOGLE_API_KEY=your_google_key

# Anthropic (Claude)
ANTHROPIC_API_KEY=your_anthropic_key

# xAI (Grok)
XAI_API_KEY=your_xai_key

# Alpha Vantage (股票数据)
ALPHA_VANTAGE_API_KEY=your_alpha_vantage_key
```

### 5.3 环境变量生效

```bash
source venv/bin/activate
export $(cat .env | grep -v '^#' | xargs)  # 加载 .env 中的变量
```

或者直接在终端设置（临时生效）：
```bash
export OPENAI_API_KEY=your_key_here
```

---

## 六、常用操作汇总

```bash
# === 进入项目目录 ===
cd /home/idiotdj/work/code/myrepo/TradingAgents

# === 激活虚拟环境 ===
source venv/bin/activate

# === 验证环境 ===
python --version
tradingagents --help

# === 运行 CLI ===
tradingagents

# === 运行示例 ===
python main.py

# === 安装额外依赖 ===
pip install akshare

# === 退出虚拟环境 ===
deactivate
```

---

## 七、故障排查

### 问题1: 命令找不到

```bash
# 确保在虚拟环境中
source venv/bin/activate

# 重新安装
pip install -e .
```

### 问题2: API 密钥错误

```bash
# 检查环境变量
echo $OPENAI_API_KEY

# 或在 .env 中检查
cat .env
```

### 问题3: 依赖冲突

```bash
# 重新创建虚拟环境
rm -rf venv
python3 -m venv venv
source venv/bin/activate
pip install -e .
```

---

*文档版本: v1.0*  
*最后更新: 2026-04-12*