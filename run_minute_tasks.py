import time
import schedule
import subprocess
from datetime import datetime
import logging

# 设置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('minute_tasks.log'),
        logging.StreamHandler()
    ]
)

def run_get_futures_data():
    """运行获取期货数据的脚本"""
    try:
        logging.info("开始执行 get_futures_data.py")
        subprocess.run(['python', 'get_futures_data.py'], check=True)
        logging.info("get_futures_data.py 执行完成")
    except Exception as e:
        logging.error(f"执行 get_futures_data.py 时出错: {e}")

def run_calculate_signals():
    """运行计算信号的脚本"""
    try:
        logging.info("开始执行 calculate_signals.py")
        subprocess.run(['python', 'calculate_signals.py'], check=True)
        logging.info("calculate_signals.py 执行完成")
    except Exception as e:
        logging.error(f"执行 calculate_signals.py 时出错: {e}")

def run_tasks():
    """按顺序执行两个任务"""
    current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    logging.info(f"开始执行定时任务 - {current_time}")
    
    # 先获取数据，再计算信号
    run_get_futures_data()
    run_calculate_signals()
    
    logging.info(f"定时任务执行完成 - {current_time}")

def main():
    logging.info("启动定时任务服务")
    
    # 设置每分钟执行一次任务
    schedule.every(1).minutes.do(run_tasks)
    
    # 立即执行一次任务
    run_tasks()
    
    # 持续运行定时任务
    while True:
        try:
            schedule.run_pending()
            time.sleep(1)
        except KeyboardInterrupt:
            logging.info("服务被手动停止")
            break
        except Exception as e:
            logging.error(f"运行时出错: {e}")
            time.sleep(5)  # 出错后等待5秒再继续

if __name__ == "__main__":
    main() 