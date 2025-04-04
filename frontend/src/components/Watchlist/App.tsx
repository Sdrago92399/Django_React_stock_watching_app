import React, { useState, useEffect, useContext } from 'react';
import WatchlistCard from './WatchlistCard'; // Import the Watchlist component
import { WebSocketContext } from '@/hooks/WebSocketProvider'; // WebSocket provider

export default function App() {
  const { stockData, isConnected, error } = useContext(WebSocketContext);
  const [watchlist, setWatchlist] = useState([]);

  useEffect(() => {
    if (stockData?.type === 'watchlist_update') {console.log(stockData.stocks)
      // Assuming the WebSocket sends an object with a "stocks" array for the watchlist
      setWatchlist(stockData.stocks);
    }
  }, [stockData]);

  return (
    <div className="App">
      {isConnected ? (
        <WatchlistCard watchlist={watchlist} />
      ) : (
        <p className="text-gray-500">Connecting to WebSocket...</p>
      )}
      {error && <p className="text-red-500">Error: {error}</p>}
    </div>
  );
}
