这个代码仓库是一个想法试验库。

包含数据获取、信号计算、回测和实盘功能。

## 项目结构
```
strategy_store/
├── data/                    # 存储期货行情数据
├── signals/                 # 存储交易信号数据
├── live_data/              # 实盘数据存储
├── logs/                   # 日志文件
├── ui/                     # React前端代码
├── archives/               # 历史数据归档
└── scripts/
    ├── get_futures_data.py     # 获取期货数据
    ├── calculate_signals.py     # 计算交易信号
    ├── trend_strategy.py       # 顺大顺小策略实现
    ├── backtest.py            # 回测系统
    ├── live_trading.py        # 实盘交易系统
    ├── live_monitor.py        # 实盘监控
    ├── run_minute_tasks.py    # 定时任务
    └── app.py                 # Streamlit应用
```

## 安装说明

1. 克隆仓库
```bash
git clone https://github.com/sencloud/strategy_store.git
cd strategy_store
```

2. 安装依赖
```bash
pip install -r requirements.txt
npm install  # 前端依赖
npm start    # 启动前端
```

## 功能列表

### 1. 数据获取
- 使用akshare获取指定品种主力合约的5分钟行情数据
- 按合约分别存储为CSV文件

### 2. 技术指标计算
- 计算EMA8和EMA21指标（使用talib）
- 生成金叉死叉信号CSV文件
- 记录信号时间和价格

### 3. 回测系统
- 初始资金：10万
- 基于金叉死叉信号开仓
- 在1分钟K线数据中定位对应时间
- 下一K线收盘时平仓
- 计算收益情况

### 4. 可视化界面
- Streamlit实现回测界面
- 分品种Tab展示回测结果

### 5. 实盘交易
- 实时获取期货数据
- 计算5分钟EMA指标
- 金叉开多，死叉开空

### 6. 实时监控
- Streamlit界面展示
- 每分钟更新数据和信号
- 按日期分Tab展示结果

### 7. 数据大屏
- React + Antd实现
- 品种信号网格展示
- 显示历史和当前信号

### 8. 自动化脚本
- 每分钟执行数据获取
- 每分钟计算交易信号

### 9. 顺大顺小策略
- 30分钟趋势判断
- 5分钟信号确认
- 顺势开仓逻辑

## 开发说明

### 数据格式
- 5分钟K线数据格式：datetime, open, high, low, close, volume
- 信号数据格式：datetime, price, signal_type(golden_cross/death_cross)

### API文档
- `get_futures_data()`: 获取期货数据
- `calculate_signals()`: 计算交易信号

## 许可证

本项目采用 MIT 许可证。

## 核心脚本说明

### 数据获取与信号计算
- `get_futures_data.py`: 使用akshare获取期货数据，支持主力合约5分钟K线
- `calculate_signals.py`: 计算EMA指标和金叉死叉信号
- `trend_strategy.py`: 实现30分钟+5分钟的顺大顺小策略

### 回测与实盘
- `backtest.py`: 回测引擎，支持多品种信号回测
- `live_trading.py`: 实盘交易系统，支持实时信号生成和下单
- `live_monitor.py`: 实时监控交易信号和持仓状态

### 自动化任务
- `run_minute_tasks.py`: 定时执行数据获取和信号计算
- `app.py`: Streamlit可视化界面，展示回测和实盘结果
