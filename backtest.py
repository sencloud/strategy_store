import pandas as pd
import os
from datetime import datetime
import glob

class Backtest:
    def __init__(self, initial_capital=100000):
        self.initial_capital = initial_capital
        self.current_capital = initial_capital
        self.positions = {}  # {symbol: {'size': 1, 'entry_price': price, 'entry_time': time, 'take_profit': price}}
        self.trades = []
        
        # 设置每个品种的止盈点数和合约乘数
        self.take_profit_points = {
            'M2505': 1,  # 豆粕1个点=10元
            'RU2505': 5,  # 橡胶1个点=50元，对应5元价格变化
            'MA2505': 1  # 甲醇1个点=10元
        }
        self.contract_multiplier = 10  # 合约乘数
        
    def load_signals(self, symbol):
        golden_cross = pd.read_csv(f'signals/{symbol}_golden_cross.csv')
        death_cross = pd.read_csv(f'signals/{symbol}_death_cross.csv')
        golden_cross['signal'] = 1  # 1 for buy
        death_cross['signal'] = -1  # -1 for sell
        
        # 合并信号并按时间排序
        all_signals = pd.concat([golden_cross, death_cross])
        # 对每个时间点只保留第一个信号
        all_signals = all_signals.drop_duplicates(subset=['datetime'], keep='first')
        return all_signals.sort_values('datetime')
    
    def load_1min_data(self, symbol):
        # Get the most recent 1min data file
        files = glob.glob(f'data/1min/{symbol}_*.csv')
        latest_file = max(files, key=os.path.getctime)
        return pd.read_csv(latest_file)
    
    def find_exit_price(self, symbol, entry_price, entry_time, signal_type):
        # 获取入场后的所有K线
        future_candles = self.min_data[self.min_data['datetime'] > entry_time]
        take_profit_point = self.take_profit_points[symbol]
        
        for _, candle in future_candles.iterrows():
            if signal_type == 1:  # 买入
                if candle['high'] >= entry_price + take_profit_point:
                    return candle['datetime'], entry_price + take_profit_point
            else:  # 卖出
                if candle['low'] <= entry_price - take_profit_point:
                    return candle['datetime'], entry_price - take_profit_point
        
        # 如果没找到止盈点，使用最后一个K线
        last_candle = future_candles.iloc[-1]
        return last_candle['datetime'], last_candle['close']
    
    def execute_trade(self, symbol, signal_time, signal_price, signal_type):
        # Find the next 1min candle after the signal
        next_candle = self.min_data[self.min_data['datetime'] > signal_time].iloc[0]
        
        if signal_type == 1:  # Golden cross - Buy
            if symbol not in self.positions:
                # Calculate position size (1 contract)
                self.positions[symbol] = {
                    'size': 1,
                    'entry_price': next_candle['close'],
                    'entry_time': next_candle['datetime']
                }
                self.trades.append({
                    'symbol': symbol,
                    'type': '买入',
                    'entry_time': next_candle['datetime'],
                    'entry_price': next_candle['close']
                })
                
                # 寻找止盈点
                exit_time, exit_price = self.find_exit_price(symbol, next_candle['close'], next_candle['datetime'], signal_type)
                position = self.positions[symbol]
                profit = (exit_price - position['entry_price']) * position['size'] * self.contract_multiplier
                self.current_capital += profit
                
                self.trades.append({
                    'symbol': symbol,
                    'type': '卖出',
                    'exit_time': exit_time,
                    'exit_price': exit_price,
                    'profit': profit
                })
                del self.positions[symbol]
        else:  # Death cross - Sell
            if symbol not in self.positions:
                # Calculate position size (1 contract)
                self.positions[symbol] = {
                    'size': 1,
                    'entry_price': next_candle['close'],
                    'entry_time': next_candle['datetime']
                }
                self.trades.append({
                    'symbol': symbol,
                    'type': '卖出',
                    'entry_time': next_candle['datetime'],
                    'entry_price': next_candle['close']
                })
                
                # 寻找止盈点
                exit_time, exit_price = self.find_exit_price(symbol, next_candle['close'], next_candle['datetime'], signal_type)
                position = self.positions[symbol]
                profit = (position['entry_price'] - exit_price) * position['size'] * self.contract_multiplier
                self.current_capital += profit
                
                self.trades.append({
                    'symbol': symbol,
                    'type': '买入',
                    'exit_time': exit_time,
                    'exit_price': exit_price,
                    'profit': profit
                })
                del self.positions[symbol]
    
    def run(self, symbol):
        signals = self.load_signals(symbol)
        self.min_data = self.load_1min_data(symbol)
        
        for _, row in signals.iterrows():
            self.execute_trade(symbol, row['datetime'], row['close'], row['signal'])
        
        return self.generate_report()
    
    def generate_report(self):
        trades_df = pd.DataFrame(self.trades)
        total_profit = self.current_capital - self.initial_capital
        profit_pct = (total_profit / self.initial_capital) * 100
        
        report = {
            'initial_capital': self.initial_capital,
            'final_capital': self.current_capital,
            'total_profit': total_profit,
            'profit_pct': profit_pct,
            'total_trades': len(trades_df),
            'trades': trades_df
        }
        return report

def main():
    symbols = ['RU2505', 'MA2505', 'M2505']
    results = []
    
    for symbol in symbols:
        print(f"\n开始回测 {symbol}...")
        backtest = Backtest()
        result = backtest.run(symbol)
        results.append({
            'symbol': symbol,
            'profit_pct': result['profit_pct'],
            'total_trades': result['total_trades']
        })
        
        print(f"{symbol} 回测结果:")
        print(f"初始资金: {result['initial_capital']:,.2f}")
        print(f"最终资金: {result['final_capital']:,.2f}")
        print(f"总收益: {result['total_profit']:,.2f}")
        print(f"收益率: {result['profit_pct']:.2f}%")
        print(f"总交易次数: {result['total_trades']}")
        
        # Save detailed trades to CSV
        result['trades'].to_csv(f'backtest_{symbol}_trades.csv', index=False)
    
    # Save summary results
    pd.DataFrame(results).to_csv('backtest_summary.csv', index=False)

if __name__ == "__main__":
    main() 