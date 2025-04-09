import React, { useState, useEffect } from 'react';
import { Layout, Row, Col, Typography } from 'antd';
import SignalCard from './components/SignalCard';
import './App.css';

const { Header, Content } = Layout;
const { Text } = Typography;

// 模拟数据
const mockData = {
  'RB2510': {
    name: '螺纹钢',
    lastSignal: { type: '金叉', price: 3500, time: '2024-04-07 10:00' },
    currentSignal: { type: '死叉', price: 3480, time: '2024-04-07 10:05' }
  },
  'MA2505': {
    name: '甲醇',
    lastSignal: { type: '死叉', price: 4200, time: '2024-04-07 10:00' },
    currentSignal: { type: '金叉', price: 4220, time: '2024-04-07 10:05' }
  },
  'SA2505': {
    name: '纯碱',
    lastSignal: { type: '金叉', price: 2800, time: '2024-04-07 10:00' },
    currentSignal: { type: '金叉', price: 2820, time: '2024-04-07 10:05' }
  },
  'RM2509': {
    name: '菜粕',
    lastSignal: { type: '死叉', price: 3100, time: '2024-04-07 10:00' },
    currentSignal: { type: '死叉', price: 3080, time: '2024-04-07 10:05' }
  },
  'FU2507': {
    name: '燃料油',
    lastSignal: { type: '金叉', price: 2900, time: '2024-04-07 10:00' },
    currentSignal: { type: '金叉', price: 2920, time: '2024-04-07 10:05' }
  },
  'FG2505': {
    name: '玻璃',
    lastSignal: { type: '死叉', price: 1800, time: '2024-04-07 10:00' },
    currentSignal: { type: '死叉', price: 1780, time: '2024-04-07 10:05' }
  },
  'V2505': {
    name: 'PVC',
    lastSignal: { type: '金叉', price: 6200, time: '2024-04-07 10:00' },
    currentSignal: { type: '金叉', price: 6220, time: '2024-04-07 10:05' }
  },
  'HC2510': {
    name: '热轧卷板',
    lastSignal: { type: '死叉', price: 3800, time: '2024-04-07 10:00' },
    currentSignal: { type: '死叉', price: 3780, time: '2024-04-07 10:05' }
  },
  'Y2509': {
    name: '豆油',
    lastSignal: { type: '金叉', price: 7500, time: '2024-04-07 10:00' },
    currentSignal: { type: '金叉', price: 7520, time: '2024-04-07 10:05' }
  },
  'BU2506': {
    name: '沥青',
    lastSignal: { type: '死叉', price: 3600, time: '2024-04-07 10:00' },
    currentSignal: { type: '死叉', price: 3580, time: '2024-04-07 10:05' }
  },
  'SP2505': {
    name: '纸浆',
    lastSignal: null,
    currentSignal: null
  },
  'AL2505': {
    name: '铝',
    lastSignal: { type: '金叉', price: 18500, time: '2024-04-07 10:00' },
    currentSignal: { type: '金叉', price: 18520, time: '2024-04-07 10:05' }
  }
};

function App() {
  const [currentTime, setCurrentTime] = useState(new Date());

  useEffect(() => {
    const timer = setInterval(() => {
      setCurrentTime(new Date());
    }, 1000);

    return () => clearInterval(timer);
  }, []);

  const formatTime = (date) => {
    return date.toLocaleString('zh-CN', {
      year: 'numeric',
      month: '2-digit',
      day: '2-digit',
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit',
      hour12: false
    });
  };

  return (
    <Layout className="layout">
      <Header className="header">
        <h1 style={{ color: 'white', margin: 0 }}>期货交易信号监控</h1>
        <div style={{ color: 'white', fontSize: '16px' }}>
          {formatTime(currentTime)}
        </div>
      </Header>
      <Content className="content">
        <Row gutter={[16, 16]}>
          {Object.entries(mockData).map(([symbol, data]) => (
            <Col span={6} key={symbol}>
              <SignalCard symbol={symbol} name={data.name} data={data} />
            </Col>
          ))}
        </Row>
      </Content>
    </Layout>
  );
}

export default App; 