import React from 'react';
import { motion } from 'framer-motion';

export default function StockCard({ stock, onAdd }) {
  const { symbol, name, type, region, currency, quote } = stock;

  return (
    <motion.div
      key={symbol}
      className="p-4 bg-white shadow rounded-lg flex flex-col md:flex-row justify-between items-center"
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
    >
      <div>
        {/* Stock Details */}
        <p className="font-bold text-xl">{symbol}</p>
        <p className="text-sm text-gray-600">{name}</p>
        <p className="text-xs text-gray-500">Type: {type}</p>
        <p className="text-xs text-gray-500">Region: {region}</p>
        <p className="text-xs text-gray-500">Currency: {currency}</p>

        {/* Quote Details */}
        {quote ? (
          <>
            <p className="text-lg font-semibold text-green-600">
              Price: ${quote.price.toFixed(2)} ({currency})
            </p>
            <p
              className={`text-sm ${
                quote.change_percent >= 0 ? 'text-green-600' : 'text-red-600'
              }`}
            >
              Change: {quote.change_percent >= 0 ? '+' : ''}
              {quote.change_percent.toFixed(2)}%
            </p>
            <p className="text-xs text-gray-500">
              Volume: {quote.volume.toLocaleString()}
            </p>
            <p className="text-xs text-gray-500">
              Last Trading Day: {quote.latest_trading_day}
            </p>
          </>
        ) : (
          <p className="text-sm text-gray-500">Loading...</p>
        )}
      </div>
      
      {/* Add to Watchlist Button */}
      <button
        onClick={() => onAdd(symbol)}
        className="mt-4 md:mt-0 bg-green-500 hover:bg-green-600 text-white px-4 py-2 rounded"
      >
        Add to Watchlist
      </button>
    </motion.div>
  );
}
