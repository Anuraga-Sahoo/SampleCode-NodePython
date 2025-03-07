const express = require('express');
const axios = require('axios');
const cors = require('cors');
const app = express();
const PORT = 3000;

// Enable JSON parsing and CORS
app.use(express.json());
app.use(cors());

// Cache to store API responses
const cache = {};
const CACHE_DURATION = 5 * 60 * 1000; // 5 minutes in milliseconds

// Sample third-party API endpoints
const STOCK_API_URL = 'https://api.marketdata.app/v1/stocks/quotes';

/**
 * Get stock quote data
 */
app.get('/api/stocks', async (req, res) => {
    try {
        const { symbol } = req.query;
        
        if (!symbol) {
            return res.status(400).json({ error: 'Stock symbol is required' });
        }
        
        // Check cache first
        const cacheKey = `stock_${symbol}`;
        if (cache[cacheKey] && (Date.now() - cache[cacheKey].timestamp) < CACHE_DURATION) {
            console.log(`Serving stock data for ${symbol} from cache`);
            return res.json(cache[cacheKey].data);
        }
        
        // Fetch from third-party API
        const response = await axios.get(`${STOCK_API_URL}/${symbol}`);
        
        // Format the response data
        const stockData = {
            symbol: symbol.toUpperCase(),
            price: response.data.price,
            change: response.data.change,
            change_percent: response.data.change_percent,
            volume: response.data.volume,
            updated_at: new Date().toISOString()
        };
        
        // Update cache
        cache[cacheKey] = {
            data: stockData,
            timestamp: Date.now()
        };
        
        res.json(stockData);
    } catch (error) {
        console.error('Stock API error:', error.response?.data || error.message);
        res.status(error.response?.status || 500).json({
            error: error.response?.data?.message || 'Failed to fetch stock data'
        });
    }
});

/**
 * Generic endpoint that can proxy requests to any API
 */
app.post('/api/fetch', async (req, res) => {
    try {
        const { url, method = 'GET', headers = {}, data = null } = req.body;
        
        if (!url) {
            return res.status(400).json({ error: 'URL is required' });
        }
        
        // Make the request to the external API
        const response = await axios({
            method,
            url,
            headers,
            data,
        });
        
        res.json({
            status: response.status,
            statusText: response.statusText,
            data: response.data,
            headers: response.headers,
        });
    } catch (error) {
        console.error('Generic API error:', error.response?.data || error.message);
        res.status(error.response?.status || 500).json({
            error: error.response?.data || 'Failed to fetch data from the specified API'
        });
    }
});

// Health check endpoint
app.get('/health', (req, res) => {
    res.json({ status: 'ok', timestamp: new Date().toISOString() });
});

// Start the server
app.listen(PORT, () => {
    console.log(`API connector server running on port ${PORT}`);
    console.log(`Stock endpoint: http://localhost:${PORT}/api/stocks?symbol=AAPL`);
});