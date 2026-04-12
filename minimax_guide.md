# MiniMax M2.5 模型配置指南

## 概述

MiniMax M2.5 模型可以通过 OpenAI 兼容接口调用。TradingAgents 支持自定义 base_url，因此可以配置使用 MiniMax API。

## 配置步骤

### 1. 复制配置文件

```bash
cp .env.example .env
```

### 2. 编辑 .env 文件

添加以下内容：

```bash
# MiniMax 配置 (使用 OpenAI 兼容接口)
OPENAI_API_KEY=your_minimax_api_key_here
OPENAI_BASE_URL=https://api.minimax.chat/v1

# 可选: 指定模型
# OPENAI_MODEL=abab6.5s-chat
```

### 3. 编辑默认配置

编辑 `tradingagents/default_config.py`，修改以下配置：

```python
DEFAULT_CONFIG = {
    # ... 其他配置 ...
    
    # LLM settings
    "llm_provider": "openai",
    "deep_think_llm": "abab6.5s-chat",      # 改为 MiniMax 模型
    "quick_think_llm": "abab6.5s-chat",     # 改为 MiniMax 模型
    "backend_url": "https://api.minimax.chat/v1",  # MiniMax API 地址
    
    # ... 其他配置 ...
}
```

或者通过环境变量配置 (推荐):

```bash
# 在 .env 中添加
OPENAI_API_KEY=your_minimax_api_key
OPENAI_BASE_URL=https://api.minimax.chat/v1
OPENAI_MODEL=abab6.5s-chat
```

## 使用方式

配置完成后，运行：

```bash
python main.py
```

然后：
1. 输入股票代码: PDD
2. 选择市场: 美股
3. Agent 将使用您的 MiniMax M2.5 模型进行分析

## 验证配置

可以先测试 API 是否可用：

```bash
source venv/bin/activate
python -c "
import openai
client = openai.OpenAI(
    api_key='your_api_key',
    base_url='https://api.minimax.chat/v1'
)
response = client.chat.completions.create(
    model='abab6.5s-chat',
    messages=[{'role': 'user', 'content': 'Hello'}]
)
print('API 连接成功!')
print(response.choices[0].message.content)
"
```

## 注意事项

1. **API Key**: 从 MiniMax 开发者平台获取
2. **模型名称**: 确认使用的是 `abab6.5s-chat` 或其他可用模型
3. **计费**: 按 MiniMax 官方计费标准

---

如需进一步帮助，请查看 tradingagents/llm_clients/ 目录下的客户端代码。