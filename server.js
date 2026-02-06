const express = require('express');
const bodyParser = require('body-parser');
const path = require('path');

const app = express();
const PORT = 3000;

// Middleware
app.use(bodyParser.json());
app.use(express.static(path.join(__dirname))); // Serve static files from root

// Routes
app.post('/api/book', (req, res) => {
    const { checkIn, checkOut, guests, roomType } = req.body;

    // In a real app, you would save this to a database here
    console.log('New Booking Request:', req.body);

    if (!checkIn || !checkOut || !guests || !roomType) {
        return res.status(400).json({ status: 'error', message: 'Missing required fields' });
    }

    res.json({
        status: 'success',
        message: `Booking received for ${roomType} (${guests} guests) from ${checkIn} to ${checkOut}.`
    });
});

// Start Server
app.listen(PORT, () => {
    console.log(`Server is running on http://localhost:${PORT}`);
});
