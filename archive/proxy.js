const express = require('express');
const cors = require('cors');
const axios = require('axios');

const app = express();
const PORT = 3000;

// Enable CORS
app.use(cors());

// Endpoint to fetch real-time messages
app.get('/api/messages', async (req, res) => {
    try {
        const response = await axios.get('https://files.cloudgdansk.pl/d/otwarte-dane/ztm/bsk.json');
        res.json(response.data);
    } catch (error) {
        res.status(500).send('Error fetching messages');
    }
});

// New endpoint to fetch route data by ID
app.get('/api/route/:id', async (req, res) => {
    const routeId = req.params.id;
    try {
        const response = await axios.get(`https://api-url-to-fetch-route/${routeId}`); // Replace with the correct API for fetching route data
        res.json(response.data);
    } catch (error) {
        res.status(500).send('Error fetching route data');
    }
});

// Start the server
app.listen(PORT, () => {
    console.log(`Proxy server is running on http://localhost:${PORT}`);
});
