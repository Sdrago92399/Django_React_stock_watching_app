import React from 'react';
import { motion } from 'framer-motion';

export default function WatchlistCard({ watchlist }) {
  return (
    <div className="w-full max-w-3xl">
      <h2 className="text-2xl font-semibold mb-4">Your Watchlist</h2>
      {watchlist.length > 0 ? (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {watchlist.map((item) => (
            <motion.div
              key={item.stock__symbol}
              className="p-4 bg-white shadow rounded-lg flex justify-between items-center"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
            >
              <div>
                <p className="font-bold">{item.stock__symbol}</p>
                <p className="text-sm text-gray-600">{item.stock__name}</p>
                <p className="text-lg font-semibold text-green-600">
                  ${item.stock__last_price}
                </p>
                <p
                  className={`text-sm ${
                    item.stock__change_percent >= 0
                      ? 'text-green-600'
                      : 'text-red-600'
                  }`}
                >
                  {item.stock__change_percent >= 0 ? '+' : ''}
                  {item.stock__change_percent}%
                </p>
              </div>
            </motion.div>
          ))}
        </div>
      ) : (
        <p className="text-gray-500">Your watchlist is empty.</p>
      )}
    </div>
  );
}
