import akshare as ak
import pandas as pd
import os
import shutil
from datetime import datetime
import time
import concurrent.futures
import random

def get_all_futures_symbols():
    """获取所有期货品种的连续合约代码，并替换为2505和2509"""
    try:
        # 获取新浪主力连续合约品种一览表
        # futures_list = ak.futures_display_main_sina()
        symbols = ["RB2510", "MA2505", "SA2505", "RM2509", "FU2507", "FG2505", 
                   "V2505", "HC2510", "Y2509", "BU2506", "SP2505", "AL2505", 
                   "AO2505", "SH2505", "C2505", "EB2505", "LH2505", "PP2505", 
                   "M2509", "I2509", "TA2505", "PX2505", "L2505", "OI2505", 
                   "UR2505", "SR2505", "NI2505", "SM2505", "A2505", "ZN2505",
                   "B2505", "JD2505"]
                
        print(f"获取到{len(symbols)}个合约代码")
        return symbols
    except Exception as e:
        print(f"获取合约列表失败: {e}")
        return []

def get_5min_data(symbol, max_retries=3):
    """获取单个合约的5分钟数据，添加重试机制"""
    for attempt in range(max_retries):
        try:
            # 获取5分钟K线数据
            df = ak.futures_zh_minute_sina(symbol=symbol, period="5")
            if df is not None and not df.empty:
                # 添加时间戳列
                df['timestamp'] = datetime.now().strftime('%Y%m%d_%H%M%S')
                return df
            else:
                print(f"获取{symbol}数据为空，尝试重试 {attempt+1}/{max_retries}")
        except Exception as e:
            print(f"获取{symbol}数据失败: {e}，尝试重试 {attempt+1}/{max_retries}")
        
        # 随机延迟0.5-2秒，避免请求过于频繁
        time.sleep(random.uniform(0.5, 2))
    
    print(f"获取{symbol}数据失败，已达到最大重试次数")
    return None

def get_30min_data(symbol, max_retries=3):
    """获取单个合约的30分钟数据，添加重试机制"""
    for attempt in range(max_retries):
        try:
            # 获取30分钟K线数据
            df = ak.futures_zh_minute_sina(symbol=symbol, period="30")
            if df is not None and not df.empty:
                # 添加时间戳列
                df['timestamp'] = datetime.now().strftime('%Y%m%d_%H%M%S')
                return df
            else:
                print(f"获取{symbol}数据为空，尝试重试 {attempt+1}/{max_retries}")
        except Exception as e:
            print(f"获取{symbol}数据失败: {e}，尝试重试 {attempt+1}/{max_retries}")
        
        # 随机延迟0.5-2秒，避免请求过于频繁
        time.sleep(random.uniform(0.5, 2))
    
    print(f"获取{symbol}数据失败，已达到最大重试次数")
    return None

def get_1min_data(symbol, max_retries=3):
    """获取单个合约的1分钟数据，添加重试机制"""
    for attempt in range(max_retries):
        try:
            # 获取1分钟K线数据
            df = ak.futures_zh_minute_sina(symbol=symbol, period="1")
            if df is not None and not df.empty:
                # 添加时间戳列
                df['timestamp'] = datetime.now().strftime('%Y%m%d_%H%M%S')
                return df
            else:
                print(f"获取{symbol}数据为空，尝试重试 {attempt+1}/{max_retries}")
        except Exception as e:
            print(f"获取{symbol}数据失败: {e}，尝试重试 {attempt+1}/{max_retries}")
        
        # 随机延迟0.5-2秒，避免请求过于频繁
        time.sleep(random.uniform(0.5, 2))
    
    print(f"获取{symbol}数据失败，已达到最大重试次数")
    return None

def save_to_csv(df, symbol, timeframe):
    """保存数据到CSV文件"""
    if df is not None and not df.empty:
        # 创建对应时间周期的目录
        data_dir = f'data/{timeframe}min'
        if not os.path.exists(data_dir):
            os.makedirs(data_dir)
        
        # 生成文件名
        filename = f"{data_dir}/{symbol}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        df.to_csv(filename, index=False, encoding='utf-8-sig')
        print(f"数据已保存到: {filename}")

def process_symbol(symbol):
    """处理单个合约的数据获取和保存"""
    print(f"\n正在获取 {symbol} 的数据...")
    
    # 获取5分钟数据
    df_5min = get_5min_data(symbol)
    if df_5min is not None:
        save_to_csv(df_5min, symbol, "5")
    
    # 获取30分钟数据
    df_30min = get_30min_data(symbol)
    if df_30min is not None:
        save_to_csv(df_30min, symbol, "30")
    
    # 获取1分钟数据
    # df_1min = get_1min_data(symbol)
    # if df_1min is not None:
    #     save_to_csv(df_1min, symbol, "1")
    
    # 添加随机延时避免请求过于频繁
    time.sleep(random.uniform(0.5, 1.5))
    return symbol

def clear_directory(directory_path):
    """清空指定目录下的所有文件"""
    if os.path.exists(directory_path):
        for filename in os.listdir(directory_path):
            file_path = os.path.join(directory_path, filename)
            try:
                if os.path.isfile(file_path):
                    os.unlink(file_path)
                elif os.path.isdir(file_path):
                    shutil.rmtree(file_path)
            except Exception as e:
                print(f"清理文件 {file_path} 时出错: {e}")
        print(f"已清空目录: {directory_path}")
    else:
        print(f"目录不存在: {directory_path}")

def main():
    # 清空5min和30min目录
    clear_directory('data/5min')
    clear_directory('data/30min')
    
    # 获取所有期货品种的主力和次主力合约代码
    symbols = get_all_futures_symbols()
    if not symbols:
        print("未能获取合约列表，程序退出")
        return
    
    print(f"\n开始获取以下合约的行情数据：{symbols}")
    
    # 使用更保守的并行度，减少并发请求数量
    max_workers = 3  # 降低并行度
    
    # 使用ThreadPoolExecutor并行处理
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        # 提交所有任务并获取结果
        futures = [executor.submit(process_symbol, symbol) for symbol in symbols]
        
        # 等待所有任务完成
        for future in concurrent.futures.as_completed(futures):
            try:
                symbol = future.result()
                print(f"完成获取 {symbol} 的数据")
            except Exception as e:
                print(f"处理合约时发生错误: {e}")

if __name__ == "__main__":
    main() 