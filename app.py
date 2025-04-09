import streamlit as st
import pandas as pd
from backtest import Backtest
import plotly.graph_objects as go
from datetime import datetime

# def plot_trades(trades_df):
#     # 创建买入和卖出的时间序列
#     buy_trades = trades_df[trades_df['type'] == '买入']
#     sell_trades = trades_df[trades_df['type'] == '卖出']
    
#     # 创建图表
#     fig = go.Figure()
    
#     # 添加买入点
#     fig.add_trace(go.Scatter(
#         x=buy_trades['entry_time'],
#         y=buy_trades['entry_price'],
#         mode='markers',
#         name='买入',
#         marker=dict(color='red', size=10)
#     ))
    
#     # 添加卖出点
#     fig.add_trace(go.Scatter(
#         x=sell_trades['exit_time'],
#         y=sell_trades['exit_price'],
#         mode='markers',
#         name='卖出',
#         marker=dict(color='green', size=10)
#     ))
    
#     # 更新布局
#     fig.update_layout(
#         title='交易点位图',
#         xaxis_title='时间',
#         yaxis_title='价格',
#         showlegend=True
#     )
    
#     return fig

def main():
    st.set_page_config(page_title="期货回测系统", layout="wide")
    st.title("期货回测系统")
    
    # 添加回测按钮
    if st.button("开始回测"):
        with st.spinner("正在执行回测..."):
            symbols = ['RU2505', 'MA2505', 'M2505']
            results = []
            
            # 创建进度条
            progress_bar = st.progress(0)
            
            for i, symbol in enumerate(symbols):
                # 执行回测
                backtest = Backtest()
                result = backtest.run(symbol)
                results.append({
                    'symbol': symbol,
                    'profit_pct': result['profit_pct'],
                    'total_trades': result['total_trades'],
                    'total_profit': result['total_profit'],
                    'trades': result['trades']
                })
                
                # 更新进度条
                progress_bar.progress((i + 1) / len(symbols))
            
            # 创建标签页
            tabs = st.tabs(symbols)
            
            # 在每个标签页中显示结果
            for tab, result in zip(tabs, results):
                with tab:
                    # 显示回测结果
                    col1, col2, col3, col4 = st.columns(4)
                    with col1:
                        st.metric("总收益", f"{result['total_profit']:,.2f}")
                    with col2:
                        st.metric("收益率", f"{result['profit_pct']:.2f}%")
                    with col3:
                        st.metric("交易次数", result['total_trades'])
                    with col4:
                        st.metric("平均收益", f"{result['total_profit']/result['total_trades']:,.2f}")
                    
                    # 显示交易图表
                    # st.plotly_chart(plot_trades(result['trades']), use_container_width=True)
                    
                    # 显示交易记录表格
                    st.subheader("交易记录")
                    st.dataframe(result['trades'], use_container_width=True)
            
            # 显示总体回测结果
            st.subheader("总体回测结果")
            summary_df = pd.DataFrame([{
                '品种': r['symbol'],
                '总收益': r['total_profit'],
                '收益率': f"{r['profit_pct']:.2f}%",
                '交易次数': r['total_trades'],
                '平均收益': r['total_profit']/r['total_trades']
            } for r in results])
            st.dataframe(summary_df, use_container_width=True)
            
            # 保存回测结果
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            for result in results:
                result['trades'].to_csv(f'backtest_{result["symbol"]}_{timestamp}.csv', index=False)
            pd.DataFrame(summary_df).to_csv(f'backtest_summary_{timestamp}.csv', index=False)
            
            st.success("回测完成！结果已保存。")

if __name__ == "__main__":
    main() 