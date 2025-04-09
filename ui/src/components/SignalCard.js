import React, { useState, useEffect } from 'react';
import { Card, Typography } from 'antd';
import { ArrowUpOutlined, ArrowDownOutlined } from '@ant-design/icons';
import './SignalCard.css';

const { Title, Text } = Typography;

const SignalCard = ({ symbol, name, data }) => {
  const { lastSignal, currentSignal } = data;
  const [isFlashing, setIsFlashing] = useState(false);
  
  useEffect(() => {
    if (currentSignal && currentSignal.type) {
      setIsFlashing(true);
      const timer = setTimeout(() => {
        setIsFlashing(false);
      }, 60000); // 1分钟后停止闪烁

      return () => clearTimeout(timer);
    }
  }, [currentSignal]);

  const getSignalColor = (type) => {
    return type === '金叉' ? '#f5222d' : '#52c41a';
  };

  const getSignalIcon = (type) => {
    return type === '金叉' ? <ArrowUpOutlined /> : <ArrowDownOutlined />;
  };

  const renderSignal = (signal) => {
    if (!signal || !signal.type) {
      return <div style={{ fontSize: '24px', marginTop: '10px' }}>暂无信号</div>;
    }
    
    return (
      <div style={{ 
        fontSize: '24px', 
        marginTop: '10px',
        color: getSignalColor(signal.type)
      }}>
        {getSignalIcon(signal.type)} {signal.type} @ {signal.price}
      </div>
    );
  };

  const cardClassName = `signal-card ${isFlashing ? 'signal-flash' : ''}`;

  return (
    <Card 
      className={cardClassName}
      data-signal={currentSignal?.type}
      style={{ 
        height: '200px',
        position: 'relative',
        backgroundColor: '#f0f2f5',
        color: 'black',
        border: '1px solid #d9d9d9'
      }}
    >
      <div style={{ position: 'absolute', top: '10px', left: '10px' }}>
        <Text strong>
          上一个信号: {lastSignal && lastSignal.type ? 
            <span style={{ color: getSignalColor(lastSignal.type) }}>
              {lastSignal.type} @ {lastSignal.price}
            </span> : '暂无'}
        </Text>
        <br />
        <Text style={{ fontSize: '12px' }}>
          {lastSignal && lastSignal.time ? lastSignal.time : '-'}
        </Text>
      </div>
      
      <div style={{ 
        position: 'absolute',
        top: '50%',
        left: '50%',
        transform: 'translate(-50%, -50%)',
        textAlign: 'center'
      }}>
        <Title level={3} style={{ margin: 0 }}>
          {name}
        </Title>
        <Text style={{ fontSize: '14px' }}>
          {symbol}
        </Text>
        {renderSignal(currentSignal)}
        <Text style={{ fontSize: '12px' }}>
          {currentSignal && currentSignal.time ? currentSignal.time : '-'}
        </Text>
      </div>
    </Card>
  );
};

export default SignalCard; 