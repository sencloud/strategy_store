import streamlit as st
import pandas as pd
import time
from datetime import datetime, timedelta
import os
from get_futures_data import get_all_futures_symbols, process_symbol
from calculate_signals import calculate_ema_signals
import concurrent.futures
import numpy as np
import talib

def load_latest_data():
    """加载最新的5分钟数据"""
    data_dir = 'data/5min'
    if not os.path.exists(data_dir):
        return {}
    
    latest_data = {}
    today = datetime.now().date()
    yesterday = today - timedelta(days=1)
    
    for file in os.listdir(data_dir):
        if file.endswith('.csv'):
            symbol = file.split('_')[0]
            file_path = os.path.join(data_dir, file)
            df = pd.read_csv(file_path)
            df['datetime'] = pd.to_datetime(df['datetime'])
            # 只保留今天和昨天的数据
            df = df[df['datetime'].dt.date >= yesterday]
            if not df.empty:
                latest_data[symbol] = df
    
    return latest_data

def process_latest_data(data_dict):
    """处理最新数据并计算信号"""
    results = {}
    for symbol, df in data_dict.items():
        golden_cross, death_cross = calculate_ema_signals(df)
        results[symbol] = {
            'golden_cross': golden_cross,
            'death_cross': death_cross
        }
    return results

def format_signal_df(df, signal_type):
    """格式化信号数据框"""
    if df.empty:
        return pd.DataFrame()
    
    df = df[['symbol', 'datetime', 'close']].copy()
    df['datetime'] = df['datetime'].dt.strftime('%Y-%m-%d %H:%M')
    df.columns = ['品种', '信号时间', '价格']
    df['信号类型'] = signal_type
    return df.sort_values('信号时间', ascending=False)

def predict_cross_signals(data_dict):
    """预测可能出现的金叉死叉信号"""
    potential_signals = []
    
    for symbol, df in data_dict.items():
        if len(df) < 30:  # 确保有足够的数据计算EMA
            continue
            
        # 计算EMA
        df['EMA8'] = talib.EMA(df['close'], timeperiod=8)
        df['EMA21'] = talib.EMA(df['close'], timeperiod=21)
        
        # 计算斜率
        df['EMA8_slope'] = df['EMA8'].diff(3) / 3
        df['EMA21_slope'] = df['EMA21'].diff(3) / 3
        
        # 获取最近5个数据点
        recent_data = df.tail(5)
        
        # 计算EMA之间的距离变化趋势
        ema_distances = recent_data['EMA8'] - recent_data['EMA21']
        ema_distance_trend = ema_distances.diff().mean()
        
        # 计算斜率差的变化趋势
        slope_diffs = recent_data['EMA8_slope'] - recent_data['EMA21_slope']
        slope_diff_trend = slope_diffs.diff().mean()
        
        # 获取最新数据点
        latest = recent_data.iloc[-1]
        
        # 计算EMA之间的距离
        ema_distance = latest['EMA8'] - latest['EMA21']
        
        # 判断潜在信号
        if abs(ema_distance) < latest['close'] * 0.002:  # EMA距离小于价格的0.2%
            # 计算趋势强度
            trend_strength = abs(ema_distance_trend) * 1000
            
            if ema_distance_trend > 0 and slope_diff_trend > 0:  # 趋势向上，可能金叉
                potential_signals.append({
                    'symbol': symbol,
                    'datetime': latest['datetime'],
                    'close': latest['close'],
                    'signal_type': '潜在金叉',
                    'confidence': min(100, int(trend_strength))
                })
            elif ema_distance_trend < 0 and slope_diff_trend < 0:  # 趋势向下，可能死叉
                potential_signals.append({
                    'symbol': symbol,
                    'datetime': latest['datetime'],
                    'close': latest['close'],
                    'signal_type': '潜在死叉',
                    'confidence': min(100, int(trend_strength))
                })
    
    return pd.DataFrame(potential_signals)

def main():
    st.title("期货实时监控")
    
    # 初始化session state
    if 'last_update' not in st.session_state:
        st.session_state.last_update = None
    
    # 创建自动刷新按钮
    auto_refresh = st.checkbox("自动刷新（每分钟）", value=True)
    
    # 显示上次更新时间
    if st.session_state.last_update:
        st.write(f"上次更新时间: {st.session_state.last_update}")
    
    # 获取所有期货品种
    symbols = get_all_futures_symbols()
    
    # 创建进度条
    progress_bar = st.progress(0)
    
    # 获取最新数据
    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
        futures = [executor.submit(process_symbol, symbol) for symbol in symbols]
        for i, future in enumerate(concurrent.futures.as_completed(futures)):
            progress_bar.progress((i + 1) / len(symbols))
    
    # 加载并处理数据
    data_dict = load_latest_data()
    results = process_latest_data(data_dict)
    
    # 预测潜在信号
    potential_signals = predict_cross_signals(data_dict)
    
    # 创建三个列来显示信号
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.subheader("金叉信号")
        golden_signals = []
        for symbol, data in results.items():
            if not data['golden_cross'].empty:
                df = data['golden_cross'].copy()
                df['symbol'] = symbol
                golden_signals.append(df)
        
        if golden_signals:
            golden_df = pd.concat(golden_signals)
            golden_df = format_signal_df(golden_df, '金叉')
            st.dataframe(golden_df)
        else:
            st.write("无金叉信号")
    
    with col2:
        st.subheader("死叉信号")
        death_signals = []
        for symbol, data in results.items():
            if not data['death_cross'].empty:
                df = data['death_cross'].copy()
                df['symbol'] = symbol
                death_signals.append(df)
        
        if death_signals:
            death_df = pd.concat(death_signals)
            death_df = format_signal_df(death_df, '死叉')
            st.dataframe(death_df)
        else:
            st.write("无死叉信号")
    
    with col3:
        st.subheader("潜在信号")
        if not potential_signals.empty:
            potential_signals['datetime'] = pd.to_datetime(potential_signals['datetime']).dt.strftime('%Y-%m-%d %H:%M')
            potential_signals = potential_signals.sort_values('confidence', ascending=False)
            st.dataframe(potential_signals[['symbol', 'datetime', 'close', 'signal_type', 'confidence']].rename(
                columns={'symbol': '品种', 'datetime': '信号时间', 'close': '价格', 'signal_type': '信号类型', 'confidence': '置信度'}
            ))
        else:
            st.write("无潜在信号")
    
    # 更新最后更新时间
    st.session_state.last_update = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # 自动刷新
    if auto_refresh:
        time.sleep(60)
        st.rerun()

if __name__ == "__main__":
    main() 