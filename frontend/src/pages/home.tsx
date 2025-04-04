"use client";

import { useState, useEffect } from 'react';
import Head from 'next/head';
import api from '@/api';
import { motion } from 'framer-motion';
import StockCard from '@/components/StockCard';
import Watchlist from '@/components/Watchlist/App';
import { WebSocketProvider } from '@/hooks/WebSocketProvider';

export default function Home() {
  const [query, setQuery] = useState('');
  const [searchResults, setSearchResults] = useState([]);
  const [watchlist, setWatchlist] = useState([]);
  const [loading, setLoading] = useState(false);

  // Fetch user's watchlist from the API
  const fetchWatchlist = async () => {
    try {
      const res = await api.get('/watchlist/', { withCredentials: true });
      setWatchlist(res.data);
    } catch (error) {
      console.error('Error fetching watchlist:', error);
    }
  };

  useEffect(() => {
    fetchWatchlist();
  }, []);

  // Handle stock search
  const handleSearch = async (e) => {
    e.preventDefault();
    if (query.length < 2) return;
    setLoading(true);
    try {
      const res = await api.get('/stocks/search/', {
        params: { q: query },
        withCredentials: true,
      });console.log(res.data)
      setSearchResults(res.data);
    } catch (error) {
      console.error('Error searching stocks:', error);
    }
    setLoading(false);
  };

  // Handle adding a stock to the watchlist
  const handleAddToWatchlist = async (symbol) => {
    try {
      const res = await api.post(
        '/watchlist/add/',
        { symbol },
        { withCredentials: true }
      );
      if (res.data.stock) {
        fetchWatchlist();
      }
    } catch (error) {
      console.error('Error adding stock to watchlist:', error);
    }
  };

  return (
    <WebSocketProvider>
      <Head>
        <title>Stock Watchlist & Alerts</title>
      </Head>
      <div className="min-h-screen bg-gray-50 flex flex-col items-center p-4">
        <motion.h1
          className="text-4xl font-bold text-blue-600 my-8"
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
        >
          Stock Watchlist & Alerts
        </motion.h1>

        {/* Stock Search Form */}
        <form onSubmit={handleSearch} className="w-full max-w-md mb-8">
          <div className="flex">
            <input
              type="text"
              placeholder="Search stocks by name or symbol..."
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              className="flex-grow p-3 border border-gray-300 rounded-l-lg focus:outline-none focus:ring-2 focus:ring-blue-600"
              required
            />
            <button
              type="submit"
              className="bg-blue-600 text-white px-4 rounded-r-lg"
            >
              {loading ? 'Searching...' : 'Search'}
            </button>
          </div>
        </form>

        {/* Search Results */}
        <div className="w-full max-w-3xl mb-12">
          <h2 className="text-2xl font-semibold mb-4">Search Results</h2>
          {searchResults.length > 0 ? (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {searchResults.map((stock) => (
                <StockCard
                  key={stock.symbol}
                  stock={stock}
                  onAdd={handleAddToWatchlist}
                />
              ))}
            </div>
          ) : (
            <p className="text-gray-500">No search results</p>
          )}
        </div>
        <Watchlist />
      </div>
    </WebSocketProvider>
  );
}
