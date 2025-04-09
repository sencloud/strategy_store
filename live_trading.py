import schedule
import time
import pandas as pd
import numpy as np
from datetime import datetime
import os
import signal
import sys
from get_futures_data import get_5min_data, get_all_futures_symbols
from calculate_signals import calculate_ema_signals
from ctpbee import CtpbeeApi, CtpBee, helper
from ctpbee.constant import Exchange, Direction, Offset, OrderType, Event

class LiveTradingApi(CtpbeeApi):
    def __init__(self, name):
        super().__init__(name)
        self.positions = {}  # 记录持仓状态
        self.take_profit_points = {
            'M2505': 1,  # 豆粕1个点=10元
            'RU2505': 5,  # 橡胶1个点=50元，对应5元价格变化
            'MA2505': 1  # 甲醇1个点=10元
        }
        self.inited = False
        self.symbols = get_all_futures_symbols()
        print(f"初始化API，监控的合约列表: {self.symbols}")
        
    def on_init(self, init: bool):
        """初始化完成回调"""
        print(f"[{datetime.now()}] 交易接口初始化完成: {init}")
        self.inited = True
        
        # 订阅合约行情
        print(f"[{datetime.now()}] 开始订阅合约行情...")
        for symbol in self.symbols:
            try:
                req = helper.generate_market_request(
                    symbol=symbol,
                    exchange=Exchange.SHFE  # 这里需要根据实际合约设置正确的交易所
                )
                self.app.subscribe(req)
                print(f"[{datetime.now()}] 订阅合约 {symbol} 成功")
            except Exception as e:
                print(f"[{datetime.now()}] 订阅合约 {symbol} 失败: {e}")
    
    def on_tick(self, tick):
        """行情数据回调"""
        print(f"[{datetime.now()}] 收到行情: {tick.symbol} 最新价: {tick.last_price} 买一: {tick.bid_price_1} 卖一: {tick.ask_price_1}")
        
    def on_bar(self, bar):
        """K线数据回调"""
        print(f"[{datetime.now()}] 收到K线: {bar.symbol} 开:{bar.open_price} 高:{bar.high_price} 低:{bar.low_price} 收:{bar.close_price}")
        
    def on_trade(self, trade):
        """交易回报回调"""
        print(f"[{datetime.now()}] 收到成交回报: 合约:{trade.symbol} 方向:{trade.direction} 开平:{trade.offset} 价格:{trade.price} 手数:{trade.volume}")
        if trade.offset == Offset.OPEN:
            # 开仓成功后，立即下止盈单
            symbol = trade.symbol
            if symbol in self.take_profit_points:
                take_profit_point = self.take_profit_points[symbol]
                
                if trade.direction == Direction.LONG:
                    take_profit_price = trade.price + take_profit_point
                    direction = Direction.SHORT
                else:
                    take_profit_price = trade.price - take_profit_point
                    direction = Direction.LONG
                
                print(f"[{datetime.now()}] 开始设置止盈单: 合约:{symbol} 方向:{direction} 止盈价:{take_profit_price}")
                # 下止盈单
                req = helper.generate_order_req_by_var(
                    symbol=symbol,
                    exchange=trade.exchange,
                    direction=direction,
                    offset=Offset.CLOSE,
                    type=OrderType.LIMIT,
                    price=take_profit_price,
                    volume=trade.volume
                )
                self.send_order(req)
                print(f"[{datetime.now()}] 止盈单已发送")
    
    def on_order(self, order):
        """订单状态回调"""
        print(f"[{datetime.now()}] 收到订单状态更新: 合约:{order.symbol} 方向:{order.direction} 开平:{order.offset} "
              f"价格:{order.price} 手数:{order.volume} 状态:{order.status}")
    
    def on_position(self, position):
        """持仓更新回调"""
        print(f"[{datetime.now()}] 收到持仓更新: 合约:{position.symbol} 方向:{position.direction} "
              f"总仓:{position.volume} 可用:{position.available} 冻结:{position.frozen}")
    
    def on_account(self, account):
        """账户资金更新回调"""
        print(f"[{datetime.now()}] 收到账户更新: 余额:{account.balance} 可用:{account.available} "
              f"冻结:{account.frozen} 持仓盈亏:{account.position_profit}")
        
    def process_signals(self, df, symbol):
        """处理交易信号"""
        if not self.inited:
            print(f"[{datetime.now()}] 交易接口未初始化完成，跳过信号处理")
            return
            
        print(f"[{datetime.now()}] 开始处理 {symbol} 的交易信号...")
        golden_cross, death_cross = calculate_ema_signals(df)
        
        # 检查是否有新的金叉信号
        if not golden_cross.empty:
            latest_golden = golden_cross.iloc[-1]
            print(f"[{datetime.now()}] 发现金叉信号: {symbol} 时间:{latest_golden['datetime']} 价格:{latest_golden['close']}")
            if symbol not in self.positions:
                print(f"[{datetime.now()}] 准备开多仓...")
                # 开多仓
                req = helper.generate_order_req_by_var(
                    symbol=symbol,
                    exchange=Exchange.SHFE,  # 根据实际交易所设置
                    direction=Direction.LONG,
                    offset=Offset.OPEN,
                    type=OrderType.LIMIT,
                    price=latest_golden['close'],
                    volume=1
                )
                self.send_order(req)
                print(f"[{datetime.now()}] 多仓开仓委托已发送")
                self.positions[symbol] = {
                    'direction': '多',
                    'entry_price': latest_golden['close']
                }
        
        # 检查是否有新的死叉信号
        if not death_cross.empty:
            latest_death = death_cross.iloc[-1]
            print(f"[{datetime.now()}] 发现死叉信号: {symbol} 时间:{latest_death['datetime']} 价格:{latest_death['close']}")
            if symbol not in self.positions:
                print(f"[{datetime.now()}] 准备开空仓...")
                # 开空仓
                req = helper.generate_order_req_by_var(
                    symbol=symbol,
                    exchange=Exchange.SHFE,  # 根据实际交易所设置
                    direction=Direction.SHORT,
                    offset=Offset.OPEN,
                    type=OrderType.LIMIT,
                    price=latest_death['close'],
                    volume=1
                )
                self.send_order(req)
                print(f"[{datetime.now()}] 空仓开仓委托已发送")
                self.positions[symbol] = {
                    'direction': '空',
                    'entry_price': latest_death['close']
                }

class LiveTrading:
    def __init__(self):
        self.running = True
        print(f"[{datetime.now()}] 开始初始化交易系统...")
        
        # 初始化CTP接口
        self.app = CtpBee("live_trading", __name__)
        self.app.config.from_mapping({
            "CONNECT_INFO": {
                "userid": "231121",
                "password": "sc1q2w#E4r",
                "brokerid": "9999",
                "md_address": "tcp://180.168.146.187:10211",
                "td_address": "tcp://180.168.146.187:10201",
                "appid": "simnow_client_test",
                "auth_code": "0000000000000000"
            },
            "INTERFACE": "ctp",  # 使用CTP接口
            "TD_FUNC": True,     # 开启交易功能
            "MD_FUNC": True,     # 开启行情功能
            "XMIN": [5],         # 订阅5分钟K线
            "LOOPER_METHOD": "thread"
        })
        print(f"[{datetime.now()}] CTP接口配置完成")
        
        # 创建API并添加到app
        self.api = LiveTradingApi("live_trading_api")
        self.app.add_extension(self.api)
        print(f"[{datetime.now()}] API实例创建完成")
        
        # 注册信号处理
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)
        
        # 启动连接
        self.app.start()
        print(f"[{datetime.now()}] CTP连接已启动")
        
        # 等待初始化完成
        print(f"[{datetime.now()}] 等待交易接口初始化...")
        while not self.api.inited and self.running:
            time.sleep(1)
            
        if self.running:
            print(f"[{datetime.now()}] 交易接口初始化完成")
        else:
            print(f"[{datetime.now()}] 初始化过程被中断")
    
    def signal_handler(self, signum, frame):
        """信号处理函数"""
        print(f"\n[{datetime.now()}] 收到退出信号，开始安全退出...")
        self.running = False
    
    def check_market(self):
        """每分钟检查市场"""
        print(f"\n[{datetime.now()}] 开始检查市场...")
        
        for symbol in self.api.symbols:
            if not self.running:
                print(f"[{datetime.now()}] 市场检查被中断")
                break
                
            try:
                # 获取5分钟数据
                print(f"[{datetime.now()}] 获取 {symbol} 的5分钟数据...")
                df = get_5min_data(symbol)
                if df is not None and not df.empty:
                    # 处理交易信号
                    self.api.process_signals(df, symbol)
            except Exception as e:
                print(f"[{datetime.now()}] 处理{symbol}时出错: {e}")
    
    def run(self):
        """运行交易系统"""
        print(f"[{datetime.now()}] 启动自动交易系统...")
        
        # 等待交易接口完全连接
        time.sleep(5)
        
        # 设置定时任务，每分钟执行一次
        schedule.every(1).minutes.do(self.check_market)
        print(f"[{datetime.now()}] 定时任务设置完成")
        
        # 运行定时任务
        while self.running:
            schedule.run_pending()
            time.sleep(1)
            
        # 安全退出
        print(f"[{datetime.now()}] 开始清理资源...")
        self.app.release()
        print(f"[{datetime.now()}] 交易系统已安全退出")

if __name__ == "__main__":
    trader = LiveTrading()
    trader.run()
