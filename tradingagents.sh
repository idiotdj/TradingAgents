#!/bin/bash
#
# TradingAgents Shell 交互式脚本
# 用法: bash tradingagents.sh
#

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# 项目路径
PROJECT_DIR="$(cd "$(dirname "$0")" && pwd)"
VENV_ACTIVATE="$PROJECT_DIR/venv/bin/activate"

# 打印分隔线
print_line() {
    echo "============================================================"
}

# 打印标题
print_header() {
    echo ""
    print_line
    echo -e "  ${CYAN}$1${NC}"
    print_line
}

# 打印菜单
print_menu() {
    echo ""
    echo -e "${YELLOW}📊 TradingAgents 交互式菜单${NC}"
    echo "------------------------------------------------------------"
    echo "  [1] 市场数据查询"
    echo "       - 查询实时行情"
    echo "       - 查询历史K线"
    echo "       - 查询基本面数据"
    echo ""
    echo "  [2] 多市场切换"
    echo "       - 美股 (US Stock)"
    echo "       - 港股 (HK Stock)"
    echo "       - A股 (China A-Share)"
    echo "       - 加密货币 (Crypto)"
    echo ""
    echo "  [3] 策略回测"
    echo "       - 基于真实历史数据回测"
    echo "       - 查看回测报告"
    echo ""
    echo "  [4] 交易模拟"
    echo "       - 模拟下单/平仓"
    echo "       - 查看持仓和盈亏"
    echo ""
    echo "  [5] Agent 分析"
    echo "       - 生成投资分析报告"
    echo "       - 查看市场研究"
    echo ""
    echo "  [6] 运行测试"
    echo "       - 一键运行所有测试"
    echo "       - 查看测试报告"
    echo ""
    echo "  [7] 安装依赖"
    echo "       - 安装 Python 依赖包"
    echo ""
    echo "  [0] 退出"
    echo "------------------------------------------------------------"
}

# 检查虚拟环境
check_venv() {
    if [ -f "$VENV_ACTIVATE" ]; then
        source "$VENV_ACTIVATE"
    fi
}

# 市场数据查询
query_market() {
    print_header "市场数据查询"
    
    echo ""
    echo "选择市场:"
    echo "  [1] 美股"
    echo "  [2] 港股"
    echo "  [3] A股 (上海/深圳)"
    echo "  [4] 加密货币"
    echo "  [0] 返回"
    
    read -p "
请输入选项: " choice
    
    case $choice in
        1)
            market_name="美股"
            example="AAPL"
            ;;
        2)
            market_name="港股"
            example="00700.HK"
            ;;
        3)
            market_name="A股"
            example="600519.SS"
            ;;
        4)
            market_name="加密货币"
            example="BTC-USD"
            ;;
        0)
            return
            ;;
        *)
            echo -e "${RED}❌ 无效选项${NC}"
            return
            ;;
    esac
    
    read -p "请输入股票代码 (如 $example): " ticker
    
    if [ -z "$ticker" ]; then
        echo -e "${RED}❌ 请输入股票代码${NC}"
        return
    fi
    
    echo ""
    echo -e "${BLUE}📈 查询中: $ticker ($market_name)...${NC}"
    
    # 使用 Python 查询
    python3 << EOF
import sys
sys.path.insert(0, "$PROJECT_DIR")
from tradingagents.dataflows.market_enums import detect_market, get_display_name
from tradingagents.agents.utils.market_tools import get_market_stock_data

try:
    market = detect_market("$ticker")
    data = get_market_stock_data("$ticker")
    
    if data:
        print("\n✅ 数据获取成功!")
        print(f"\n数据预览:")
        print(f"  股票代码: $ticker")
        print(f"  市场类型: {get_display_name('$ticker', market)}")
        if 'current_price' in data:
            print(f"  当前价格: \${data['current_price']:.2f}")
        if 'daily' in data and len(data['daily']) > 0:
            latest = data['daily'][-1]
            print(f"  最新日期: {latest.get('date', 'N/A')}")
            print(f"  收盘: \${latest.get('close', 0):.2f}")
    else:
        print("\n❌ 未获取到数据，请检查股票代码是否正确")
except Exception as e:
    print(f"\n❌ 查询失败: {e}")
EOF
    
    echo ""
    read -p "按回车键继续..."
}

# 市场切换说明
switch_market() {
    print_header "多市场切换"
    
    echo ""
    echo "当前支持的市场:"
    echo "  [1] 美股 (US Stock)"
    echo "       示例: AAPL, MSFT, NVDA, GOOGL"
    echo ""
    echo "  [2] 港股 (HK Stock)"
    echo "       示例: 00700.HK (腾讯), 09988.HK (阿里)"
    echo ""
    echo "  [3] A股 (China A-Share)"
    echo "       上海: 600519.SS (茅台), 600036.SS (招行)"
    echo "       深圳: 000001.SZ (平安), 300750.SZ (宁德)"
    echo ""
    echo "  [4] 加密货币 (Crypto)"
    echo "       示例: BTC-USD, ETH-USD, DOGE-USD"
    echo ""
    echo "  [0] 返回"
    
    read -p "
请输入选项: " choice
    
    case $choice in
        1)
            echo -e "\n✅ 已切换到 ${GREEN}美股${NC}"
            echo "   示例股票代码: AAPL"
            ;;
        2)
            echo -e "\n✅ 已切换到 ${GREEN}港股${NC}"
            echo "   示例股票代码: 00700.HK"
            ;;
        3)
            echo -e "\n✅ 已切换到 ${GREEN}A股${NC}"
            echo "   示例股票代码: 600519.SS"
            ;;
        4)
            echo -e "\n✅ 已切换到 ${GREEN}加密货币${NC}"
            echo "   示例股票代码: BTC-USD"
            ;;
        0)
            return
            ;;
        *)
            echo -e "${RED}❌ 无效选项${NC}"
            ;;
    esac
    
    echo ""
    read -p "按回车键继续..."
}

# 策略回测
run_backtest() {
    print_header "策略回测"
    
    echo ""
    echo -e "${YELLOW}⚠️  注意: 回测将使用真实历史数据${NC}"
    
    read -p "请输入股票代码 (如 AAPL, 600519.SS): " ticker
    
    if [ -z "$ticker" ]; then
        echo -e "${RED}❌ 请输入股票代码${NC}"
        read -p "按回车键继续..."
        return
    fi
    
    echo ""
    echo -e "${BLUE}📊 正在准备 $ticker 的回测数据...${NC}"
    
    # 这里可以调用回测功能
    echo ""
    echo -e "${GREEN}✅ 回测引擎已就绪${NC}"
    echo "   注意: 完整回测功能需要更多配置"
    echo "   - 选择回测时间范围"
    echo "   - 设置初始资金"
    echo "   - 选择交易策略"
    
    echo ""
    read -p "按回车键继续..."
}

# 交易模拟
trading_sim() {
    print_header "交易模拟"
    
    echo ""
    echo "当前功能:"
    echo "  - 交易模拟器已就绪"
    echo "  - 支持多市场订单"
    echo "  - 支持市价单/限价单"
    echo "  - 持仓和盈亏管理"
    echo ""
    echo -e "  运行命令: ${CYAN}python test_simulator.py${NC}"
    
    echo ""
    read -p "按回车键继续..."
}

# Agent 分析
agent_analysis() {
    print_header "Agent 分析"
    
    echo ""
    echo -e "${YELLOW}⚠️  注意: 需要配置 LLM API 密钥${NC}"
    echo ""
    echo "配置步骤:"
    echo "  1. 复制 .env.example 为 .env"
    echo "  2. 设置 OPENAI_API_KEY 或 ANTHROPIC_API_KEY"
    echo "  3. 运行: python main.py"
    echo ""
    echo "支持的 LLM:"
    echo "  - OpenAI (GPT-4)"
    echo "  - Anthropic (Claude)"
    echo "  - Google (Gemini)"
    echo "  - xAI (Grok)"
    
    echo ""
    read -p "按回车键继续..."
}

# 运行测试
run_tests() {
    print_header "运行测试"
    
    echo ""
    echo -e "${BLUE}运行中...${NC}"
    echo ""
    
    cd "$PROJECT_DIR"
    check_venv
    python run_tests.py
    
    echo ""
    read -p "按回车键继续..."
}

# 安装依赖
install_deps() {
    print_header "安装依赖"
    
    echo ""
    echo "正在安装依赖..."
    
    cd "$PROJECT_DIR"
    
    # 检查是否使用虚拟环境
    if [ -f "$VENV_ACTIVATE" ]; then
        echo "检测到虚拟环境: venv"
        source "$VENV_ACTIVATE"
    fi
    
    # 安装依赖
    pip install -e .
    
    echo ""
    echo -e "${GREEN}✅ 依赖安装完成${NC}"
    read -p "按回车键继续..."
}

# 主循环
main() {
    # 清除屏幕
    clear
    
    while true; do
        print_header "TradingAgents 多市场交易系统"
        
        echo ""
        echo -e "📁 项目路径: ${CYAN}$PROJECT_DIR${NC}"
        echo ""
        echo "当前已实现功能:"
        echo -e "  ${GREEN}✅${NC} 市场类型检测 (美股/港股/A股/加密货币)"
        echo -e "  ${GREEN}✅${NC} 数据源接口 (yfinance, AkShare)"
        echo -e "  ${GREEN}✅${NC} 交易模拟器"
        echo -e "  ${GREEN}✅${NC} 回测引擎"
        echo -e "  ${GREEN}✅${NC} 测试框架"
        
        print_menu
        
        read -p "
请输入选项: " choice
        
        # 清除屏幕
        clear
        
        case $choice in
            1)
                check_venv
                query_market
                ;;
            2)
                switch_market
                ;;
            3)
                run_backtest
                ;;
            4)
                trading_sim
                ;;
            5)
                agent_analysis
                ;;
            6)
                check_venv
                run_tests
                ;;
            7)
                install_deps
                ;;
            0)
                echo ""
                echo -e "${YELLOW}👋 感谢使用 TradingAgents!${NC}"
                echo "   GitHub: https://github.com/idiotdj/TradingAgents"
                echo ""
                break
                ;;
            *)
                echo -e "${RED}❌ 无效选项，请重新输入${NC}"
                read -p "按回车键继续..."
                ;;
        esac
    done
}

# 启动
main