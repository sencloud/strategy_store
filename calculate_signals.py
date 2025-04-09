import pandas as pd
import numpy as np
import talib
import os
from datetime import datetime

def calculate_ema_signals(df):
    """计算EMA8和EMA21，并生成金叉死叉信号"""
    # 计算EMA
    df['EMA8'] = talib.EMA(df['close'], timeperiod=8)
    df['EMA21'] = talib.EMA(df['close'], timeperiod=21)
    
    # 计算斜率（使用3个点的移动平均来平滑）
    df['EMA8_slope'] = df['EMA8'].diff(3) / 3
    df['EMA21_slope'] = df['EMA21'].diff(3) / 3
    
    # 计算角度（弧度）
    df['angle'] = np.arctan2(df['EMA8_slope'] - df['EMA21_slope'], 1)
    # 转换为角度
    df['angle_degrees'] = np.degrees(df['angle'])
    
    # 计算金叉死叉
    df['cross'] = np.where(df['EMA8'] > df['EMA21'], 1, -1)
    df['cross_change'] = df['cross'].diff()
    
    # 获取当前日期
    current_date = datetime.now().date()
    
    # 提取金叉和死叉信号，并过滤掉角度太小的信号（小于15度）
    golden_cross = df[(df['cross_change'] == 2) & (df['angle_degrees'] > 15)].copy()
    death_cross = df[(df['cross_change'] == -2) & (df['angle_degrees'] < -15)].copy()
    
    # 当天的信号
    golden_cross_today = golden_cross[golden_cross['datetime'].dt.date == current_date]
    death_cross_today = death_cross[death_cross['datetime'].dt.date == current_date]
    
    return golden_cross, death_cross, golden_cross_today, death_cross_today

def save_signals(golden_cross, death_cross, golden_cross_today, death_cross_today, symbol, timeframe='30min'):
    """保存金叉死叉信号到CSV文件"""
    # 如果当天没有信号，直接返回
    if golden_cross.empty and death_cross.empty:
        print(f"合约 {symbol} 没有信号")
        return
        
    signals_dir = f'signals/{timeframe}'
    if not os.path.exists(signals_dir):
        os.makedirs(signals_dir)
    
    # 保存金叉信号
    if not golden_cross.empty:
        golden_filename = f"{signals_dir}/{symbol}_golden_cross.csv"
        golden_cross[['datetime', 'close', 'EMA8', 'EMA21', 'angle_degrees']].to_csv(golden_filename, index=False, encoding='utf-8-sig')
        print(f"金叉信号已保存到: {golden_filename}")
    
    # 保存死叉信号
    if not death_cross.empty:
        death_filename = f"{signals_dir}/{symbol}_death_cross.csv"
        death_cross[['datetime', 'close', 'EMA8', 'EMA21', 'angle_degrees']].to_csv(death_filename, index=False, encoding='utf-8-sig')
        print(f"死叉信号已保存到: {death_filename}")

    # 保存当天金叉信号
    if not golden_cross_today.empty:
        golden_filename_today = f"{signals_dir}/{symbol}_golden_cross_today.csv"
        golden_cross_today[['datetime', 'close', 'EMA8', 'EMA21', 'angle_degrees']].to_csv(golden_filename_today, index=False, encoding='utf-8-sig')
        print(f"当天金叉信号已保存到: {golden_filename_today}")
    
    # 保存当天死叉信号
    if not death_cross_today.empty:
        death_filename_today = f"{signals_dir}/{symbol}_death_cross_today.csv"
        death_cross_today[['datetime', 'close', 'EMA8', 'EMA21', 'angle_degrees']].to_csv(death_filename_today, index=False, encoding='utf-8-sig')
        print(f"当天死叉信号已保存到: {death_filename_today}")

def process_file(file_path, timeframe='30min'):
    """处理单个CSV文件"""
    try:
        # 读取数据
        df = pd.read_csv(file_path)
        
        # 确保datetime列是datetime类型
        df['datetime'] = pd.to_datetime(df['datetime'])
        
        # 获取合约代码
        symbol = os.path.basename(file_path).split('_')[0]
        print(f"\n处理合约: {symbol}")
        
        # 计算信号
        golden_cross, death_cross, golden_cross_today, death_cross_today = calculate_ema_signals(df)
        
        # 保存信号
        save_signals(golden_cross, death_cross, golden_cross_today, death_cross_today, symbol, timeframe)
        
        # 打印统计信息
        print(f"金叉次数: {len(golden_cross)}")
        print(f"死叉次数: {len(death_cross)}")
        print(f"当天金叉次数: {len(golden_cross_today)}")
        print(f"当天死叉次数: {len(death_cross_today)}")

    except Exception as e:
        print(f"处理文件 {file_path} 时出错: {e}")

def aggregate_signals(timeframe='30min'):
    """汇总所有合约当天的信号到一个CSV文件"""
    signals_dir = f'signals/{timeframe}'
    if not os.path.exists(signals_dir):
        print("没有找到信号文件")
        return
        
    # 获取所有信号文件
    golden_files = [f for f in os.listdir(signals_dir) if f.endswith('_golden_cross.csv')]
    death_files = [f for f in os.listdir(signals_dir) if f.endswith('_death_cross.csv')]
    golden_files_today = [f for f in os.listdir(signals_dir) if f.endswith('_golden_cross_today.csv')]
    death_files_today = [f for f in os.listdir(signals_dir) if f.endswith('_death_cross_today.csv')]
    
    all_signals = []
    all_signals_today = []

    # 读取金叉信号
    for file in golden_files:
        symbol = file.split('_')[0]
        df = pd.read_csv(f'{signals_dir}/{file}')
        df['signal_type'] = '金叉'
        df['symbol'] = symbol
        all_signals.append(df)
    
    # 读取死叉信号
    for file in death_files:
        symbol = file.split('_')[0]
        df = pd.read_csv(f'{signals_dir}/{file}')
        df['signal_type'] = '死叉'
        df['symbol'] = symbol
        all_signals.append(df)
    
    # 读取当天金叉信号
    for file in golden_files_today:
        symbol = file.split('_')[0]
        df = pd.read_csv(f'{signals_dir}/{file}')
        df['signal_type'] = '金叉'
        df['symbol'] = symbol
        all_signals_today.append(df)
    
    # 读取当天死叉信号
    for file in death_files_today:
        symbol = file.split('_')[0]
        df = pd.read_csv(f'{signals_dir}/{file}')
        df['signal_type'] = '死叉'
        df['symbol'] = symbol
        all_signals_today.append(df)
    
    if not all_signals:
        print("没有找到任何信号")
        return
        
    # 合并所有信号
    combined_signals = pd.concat(all_signals, ignore_index=True)
    
    # 确保datetime列是datetime类型
    combined_signals['datetime'] = pd.to_datetime(combined_signals['datetime'])
    
    # 按时间倒序排序
    combined_signals = combined_signals.sort_values('datetime', ascending=False)
    
    # 保存汇总文件
    combined_signals.to_csv(f'{signals_dir}/all_signals.csv', index=False, encoding='utf-8-sig')
    
    print(f"已保存汇总信号到: {signals_dir}/all_signals.csv")
    print(f"共 {len(combined_signals)} 个信号")

    if all_signals_today:
        combined_signals_today = pd.concat(all_signals_today, ignore_index=True)
        combined_signals_today['datetime'] = pd.to_datetime(combined_signals_today['datetime'])
        combined_signals_today = combined_signals_today.sort_values('datetime', ascending=False)
        combined_signals_today.to_csv(f'{signals_dir}/all_signals_today.csv', index=False, encoding='utf-8-sig')
        print(f"已保存汇总信号到: {signals_dir}/all_signals_today.csv")
        print(f"共 {len(combined_signals_today)} 个信号")
    
    # 删除单个合约的信号文件
    for file in golden_files + death_files:
        try:
            os.remove(f'{signals_dir}/{file}')
            print(f"已删除: {signals_dir}/{file}")
        except Exception as e:
            print(f"删除文件 {signals_dir}/{file} 时出错: {e}")

def process_timeframe(timeframe):
    """处理指定时间周期的数据"""
    data_dir = f'data/{timeframe}'
    signals_dir = f'signals/{timeframe}'
    
    if not os.path.exists(data_dir):
        print(f"错误: {data_dir} 目录不存在")
        return
    
    # 创建对应的signals目录
    if os.path.exists(signals_dir):
        for file in os.listdir(signals_dir):
            try:
                os.remove(os.path.join(signals_dir, file))
                print(f"已删除: {signals_dir}/{file}")
            except Exception as e:
                print(f"删除文件 {signals_dir}/{file} 时出错: {e}")
    else:
        os.makedirs(signals_dir)
        print(f"创建{signals_dir}目录")
    
    csv_files = [f for f in os.listdir(data_dir) if f.endswith('.csv')]
    if not csv_files:
        print(f"错误: {data_dir} 目录中没有CSV文件")
        return
    
    print(f"\n处理 {timeframe} 数据:")
    print(f"找到 {len(csv_files)} 个CSV文件")
    
    # 处理每个文件
    for file in csv_files:
        file_path = os.path.join(data_dir, file)
        process_file(file_path, timeframe)
    
    # 汇总所有信号
    aggregate_signals(timeframe)

def main():
    # 确保主signals目录存在
    if not os.path.exists('signals'):
        os.makedirs('signals')
    
    # 处理30分钟和5分钟数据
    process_timeframe('30min')
    process_timeframe('5min')

if __name__ == "__main__":
    main() 