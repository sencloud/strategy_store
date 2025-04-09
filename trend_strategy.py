import pandas as pd
import numpy as np
import talib
import os
from datetime import datetime
from get_futures_data import get_30min_data, get_5min_data, get_all_futures_symbols

def calculate_trend_signals(df, timeframe='30min'):
    """计算EMA8和EMA21趋势信号"""
    # 计算EMA
    df['EMA8'] = talib.EMA(df['close'], timeperiod=8)
    df['EMA21'] = talib.EMA(df['close'], timeperiod=21)
    
    # 计算趋势
    df['trend'] = np.where(df['EMA8'] > df['EMA21'], 1, -1)  # 1表示多头趋势，-1表示空头趋势
    df['trend_change'] = df['trend'].diff()
    
    # 计算斜率和角度（用于过滤信号）
    df['EMA8_slope'] = df['EMA8'].diff(3) / 3
    df['EMA21_slope'] = df['EMA21'].diff(3) / 3
    df['angle'] = np.degrees(np.arctan2(df['EMA8_slope'] - df['EMA21_slope'], 1))
    
    return df

def get_current_trend(symbol):
    """获取当前30分钟和5分钟趋势"""
    # 获取30分钟数据
    df_30min = get_30min_data(symbol)
    if df_30min is None or df_30min.empty:
        return None, None
    
    # 获取5分钟数据
    df_5min = get_5min_data(symbol)
    if df_5min is None or df_5min.empty:
        return None, None
    
    # 计算30分钟趋势
    df_30min = calculate_trend_signals(df_30min, '30min')
    current_30min_trend = df_30min.iloc[-1]['trend']
    
    # 计算5分钟趋势
    df_5min = calculate_trend_signals(df_5min, '5min')
    current_5min_trend = df_5min.iloc[-1]['trend']
    last_5min_trend_change = df_5min.iloc[-1]['trend_change']
    
    return {
        '30min_trend': current_30min_trend,
        '5min_trend': current_5min_trend,
        '5min_trend_change': last_5min_trend_change,
        '30min_price': df_30min.iloc[-1]['close'],
        '5min_price': df_5min.iloc[-1]['close'],
        '30min_angle': df_30min.iloc[-1]['angle'],
        '5min_angle': df_5min.iloc[-1]['angle'],
        'datetime': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }

def check_trading_signal(symbol_trends):
    """检查是否满足交易信号条件"""
    if not symbol_trends:
        return None
    
    thirty_min_trend = symbol_trends['30min_trend']
    five_min_trend = symbol_trends['5min_trend']
    five_min_trend_change = symbol_trends['5min_trend_change']
    
    # 信号条件：
    # 1. 30分钟处于多头趋势，5分钟从空头转多头 -> 做多
    # 2. 30分钟处于空头趋势，5分钟从多头转空头 -> 做空
    
    signal = None
    if thirty_min_trend == 1:  # 30分钟多头趋势
        if five_min_trend == 1 and five_min_trend_change == 2:  # 5分钟由空转多
            signal = {
                'type': 'LONG',
                'reason': '30分钟多头趋势，5分钟金叉',
                'price': symbol_trends['5min_price'],
                'datetime': symbol_trends['datetime']
            }
    elif thirty_min_trend == -1:  # 30分钟空头趋势
        if five_min_trend == -1 and five_min_trend_change == -2:  # 5分钟由多转空
            signal = {
                'type': 'SHORT',
                'reason': '30分钟空头趋势，5分钟死叉',
                'price': symbol_trends['5min_price'],
                'datetime': symbol_trends['datetime']
            }
    
    return signal

def save_signal(signal, symbol):
    """保存交易信号到CSV文件"""
    if not signal:
        return
    
    # 确保signals目录存在
    if not os.path.exists('signals'):
        os.makedirs('signals')
    
    # 创建信号DataFrame
    signal_df = pd.DataFrame([{
        'symbol': symbol,
        'datetime': signal['datetime'],
        'type': signal['type'],
        'price': signal['price'],
        'reason': signal['reason']
    }])
    
    # 保存到CSV
    filename = f'signals/trend_signals_{datetime.now().strftime("%Y%m%d")}.csv'
    mode = 'a' if os.path.exists(filename) else 'w'
    header = not os.path.exists(filename)
    signal_df.to_csv(filename, mode=mode, header=header, index=False, encoding='utf-8-sig')
    print(f"信号已保存到: {filename}")

def main():
    """主函数：获取所有合约的趋势信号"""
    symbols = get_all_futures_symbols()
    if not symbols:
        print("未能获取合约列表，程序退出")
        return
    
    for symbol in symbols:
        print(f"\n处理合约: {symbol}")
        try:
            # 获取趋势数据
            trends = get_current_trend(symbol)
            if trends:
                # 检查是否有交易信号
                signal = check_trading_signal(trends)
                if signal:
                    print(f"发现{signal['type']}信号: {symbol}")
                    print(f"原因: {signal['reason']}")
                    print(f"价格: {signal['price']}")
                    print(f"时间: {signal['datetime']}")
                    # 保存信号
                    save_signal(signal, symbol)
                else:
                    print(f"没有交易信号")
            else:
                print(f"获取趋势数据失败")
        except Exception as e:
            print(f"处理合约 {symbol} 时出错: {e}")
        
if __name__ == "__main__":
    main() 