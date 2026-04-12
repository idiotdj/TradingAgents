# TradingAgents 使用指南

> 本项目是基于 [TradingAgents](https://github.com/TauricResearch/TradingAgents) 的多市场交易 Agent 扩展，支持美股、港股、A股、加密货币。

---

## 一、项目概述

TradingAgents 是一个基于 LLM (大语言模型) 的多 Agent 金融交易框架。本项目在原版基础上扩展了以下功能：

- **多市场支持**: 美股、港股、A股、加密货币
- **真实数据源**: yfinance, AkShare (真实市场数据，非模拟)
- **交互式界面**: Shell 菜单、Python CLI、REST API
- **测试框架**: 一键运行所有测试

---

## 二、功能特性

### 2.1 市场数据查询

| 市场 | 示例代码 | 数据源 |
|------|----------|--------|
| 美股 | AAPL, MSFT, NVDA, PDD | yfinance |
| 港股 | 00700.HK, 09988.HK | AkShare |
| A股 (上海) | 600519.SS, 688111.SS | AkShare |
| A股 (深圳) | 000001.SZ, 300750.SZ | AkShare |
| 加密货币 | BTC-USD, ETH-USD | yfinance |

### 2.2 核心模块

- **市场类型检测** (`market_enums.py`): 自动识别股票代码所属市场
- **数据获取** (`market_tools.py`): 获取实时/历史行情数据
- **交易模拟器** (`trading_simulator.py`): 模拟下单/持仓/盈亏
- **回测引擎** (`backtest_engine.py`): 基于历史数据回测策略

### 2.3 用户界面

- **Shell 交互** (`tradingagents.sh`): 菜单式操作
- **Python CLI** (`run_cli.py`): 交互式菜单
- **REST API** (`api/app.py`): FastAPI 服务

---

## 三、快速开始

### 3.1 环境要求

- Python 3.10+
- 虚拟环境 (推荐)

### 3.2 安装

```bash
# 1. 克隆项目
git clone https://github.com/idiotdj/TradingAgents.git
cd TradingAgents

# 2. 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate   # Windows

# 3. 安装依赖
pip install -e .

# 4. 安装额外依赖 (API 需要)
pip install fastapi uvicorn
```

### 3.3 启动方式

#### 方式1: Shell 交互界面 (推荐)

```bash
bash tradingagents.sh
```

菜单操作:
```
📊 TradingAgents 交互式菜单
------------------------------------------------------------
  [1] 市场数据查询 - 查询实时行情
  [2] 多市场切换 - 查看各市场说明
  [3] 策略回测 - 回测功能说明
  [4] 交易模拟 - 模拟交易说明
  [5] Agent 分析 - LLM 分析说明
  [6] 运行测试 - 一键测试
  [7] 安装依赖 - 安装 Python 包
  [0] 退出
------------------------------------------------------------
```

#### 方式2: Python 交互界面

```bash
python run_cli.py
```

#### 方式3: 一键测试

```bash
python run_tests.py
```

测试内容:
- 市场类型检测 (17个用例)
- 交易模拟器
- 回测引擎
- 多市场工具

#### 方式4: API 服务

```bash
python api/app.py
# 访问 http://localhost:8000
```

API 端点:
- `GET /` - 根路径
- `GET /health` - 健康检查
- `GET /api/markets` - 支持的市场列表
- `POST /api/market/query` - 市场数据查询
- `POST /api/backtest` - 回测接口
- `POST /api/trade/order` - 交易下单

---

## 四、使用示例

### 4.1 查询美股数据 (Shell)

```bash
$ bash tradingagents.sh

# 选择 [1] 市场数据查询
# 选择 [1] 美股
# 输入股票代码: PDD

# 输出示例:
✅ 数据获取成功!
  股票代码: PDD
  市场类型: 美股
  当前价格: $100.17
  最新日期: 2026-04-10
  开盘: $101.30
  收盘: $100.17
  成交量: 5,000,400

最近5个交易日:
  2026-04-10: O:101.30 H:103.86 L:99.91 C:100.17
  2026-04-09: O:102.88 H:103.87 L:99.05 C:102.34
  2026-04-08: O:102.51 H:104.80 L:102.51 C:103.96
```

### 4.2 查询加密货币

```bash
# 选择 [4] 加密货币
# 输入: BTC-USD
```

### 4.3 一键测试

```bash
$ python run_tests.py

🎉 所有测试通过!
  ✅ 通过  市场类型检测
  ✅ 通过  交易模拟器
  ✅ 通过  回测引擎
  ✅ 通过  多市场工具
```

---

## 五、配置说明

### 5.1 API 密钥 (可选 - 用于 Agent 分析)

```bash
# 复制配置文件
cp .env.example .env

# 编辑 .env，填入您的 API 密钥
OPENAI_API_KEY=sk-xxx      # OpenAI
ANTHROPIC_API_KEY=xxx      # Anthropic
GOOGLE_API_KEY=xxx         # Google
```

### 5.2 数据源配置

项目使用真实数据源:
- **美股/加密货币**: yfinance (Yahoo Finance)
- **港股/A股**: AkShare (免费开源)

无需额外配置，数据自动获取。

---

## 六、项目结构

```
TradingAgents/
├── tradingagents.sh          # Shell 交互入口
├── run_cli.py                # Python 交互界面
├── run_tests.py              # 一键测试脚本
├── api/
│   └── app.py                # FastAPI REST API
├── tradingagents/
│   ├── dataflows/            # 数据层
│   │   ├── market_enums.py   # 市场类型枚举
│   │   ├── akshare_data.py   # A股/港股数据
│   │   └── y_finance.py      # 美股/加密货币数据
│   ├── agents/utils/         # Agent 工具
│   │   └── market_tools.py   # 多市场数据工具
│   ├── simulator/            # 交易模拟
│   │   └── trading_simulator.py
│   └── backtest/             # 回测引擎
│       └── backtest_engine.py
├── tests/                    # 测试用例
│   └── test_market_enums.py
└── docs/                    # 文档
    └── MARKET_RESEARCH.md
```

---

## 七、常见问题

### Q1: 为什么查询不到数据?

1. 检查股票代码是否正确 (如 PDD, AAPL)
2. 检查网络连接 (yfinance 需要联网)
3. 检查虚拟环境是否激活

### Q2: 交易被拒绝怎么办?

模拟交易在工作日交易时间可下单:
- 美股: 9:30-16:00 EST
- 港股: 9:30-16:00 HKT
- A股: 9:30-15:00 CST
- 加密货币: 7x24 小时

### Q3: 如何使用 Agent 分析?

1. 配置 API 密钥 (见 5.1)
2. 运行 `python main.py`
3. 按照 CLI 提示操作

---

## 八、免责声明

本项目仅供学习和研究使用，不构成投资建议。使用本项目进行交易造成的任何损失，由用户自行承担。

---

## 九、LLM 模型配置

如需使用 MiniMax、Moonshot 等第三方模型，请参考 [minimax_guide.md](./minimax_guide.md)。

## 十、参考资源

- [TradingAgents 官方](https://github.com/TauricResearch/TradingAgents)
- [yfinance](https://pypi.org/project/yfinance/)
- [AkShare](https://akshare.akfamily.com.cn/)

---

*文档版本: 1.0.1*  
*最后更新: 2026-04-12*
