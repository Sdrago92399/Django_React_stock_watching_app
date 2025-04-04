import React, { createContext, useState, useEffect, useRef, useCallback } from 'react';

export const WebSocketContext = createContext(null);

export const WebSocketProvider = ({ children }) => {
  const socketRef = useRef(null);
  const [isConnected, setIsConnected] = useState(false);
  const [error, setError] = useState(null);
  const [stockData, setStockData] = useState({});

  const connectWebSocket = useCallback(() => {
    if (socketRef.current) {
      socketRef.current.close();
    }

    // Retrieve the access token from localStorage
    const token = localStorage.getItem('accessToken');

    const wsProtocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    // Append the token as a query parameter
    const wsUrl = `${wsProtocol}//${window.location.hostname}:8001/ws/stocks/?token=${token}`;

    console.log('Connecting to WebSocket:', wsUrl);
    const socket = new WebSocket(wsUrl);
    socketRef.current = socket;

    socket.onopen = () => {
      console.log('WebSocket connection established');
      setIsConnected(true);
      setError(null);
    };

    socket.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        setStockData(data);
      } catch (err) {
        console.error('Error parsing websocket message:', err);
      }
    };

    socket.onclose = (event) => {
      console.log('WebSocket connection closed', event);
      setIsConnected(false);
      setTimeout(() => {
        if (document.visibilityState !== 'hidden') {
          connectWebSocket();
        }
      }, 5000);
    };

    socket.onerror = (error) => {
      console.error('WebSocket error:', error);
      setError('Failed to connect to the stock update service');
      setIsConnected(false);
    };
  }, []);

  useEffect(() => {
    connectWebSocket();
    return () => {
      if (socketRef.current) {
        socketRef.current.close();
      }
    };
  }, [connectWebSocket]);

  return (
    <WebSocketContext.Provider value={{ stockData, isConnected, error }}>
      {children}
    </WebSocketContext.Provider>
  );
};
