// server.js
const express = require('express');
const multer = require('multer'); // Library to handle file uploads
const cors = require('cors');
const path = require('path');
const fs = require('fs');

const app = express();
const PORT = process.env.PORT || 3000;

// 1. Middleware
app.use(cors());
app.use(express.json());
// Serve the static HTML file from a 'public' folder
app.use(express.static(path.join(__dirname, 'public')));

// 2. Configure File Upload Storage
// We will save uploaded photos to an 'uploads' folder
const uploadDir = path.join(__dirname, 'uploads');
if (!fs.existsSync(uploadDir)){
    fs.mkdirSync(uploadDir);
}

const storage = multer.diskStorage({
    destination: function (req, file, cb) {
        cb(null, uploadDir);
    },
    filename: function (req, file, cb) {
        // Create a unique filename: timestamp-originalname
        const uniqueSuffix = Date.now() + '-' + Math.round(Math.random() * 1E9);
        cb(null, uniqueSuffix + path.extname(file.originalname));
    }
});

const upload = multer({ storage: storage });

// 3. API Route to handle Order Submission
app.post('/api/submit-order', upload.single('paymentPhoto'), (req, res) => {
    try {
        if (!req.file) {
            return res.status(400).send('No payment photo uploaded.');
        }

        // 4. Capture Data
        const orderData = {
            bookingName: req.body.bookingName,
            contact: req.body.contact,
            school: req.body.school,
            className: req.body.className, // 'class' is a reserved keyword in JS
            cartItems: JSON.parse(req.body.cart), // Parse the stringified cart
            photoPath: req.file.path,
            submittedAt: new Date()
        };

        // 5. Log to console (and ideally save to a database later)
        console.log('--- NEW ORDER RECEIVED ---');
        console.log(orderData);

        // For this demo, we save the order details to a text file so you don't lose them
        const logEntry = `\n${JSON.stringify(orderData)}\n-------------------`;
        fs.appendFileSync(path.join(__dirname, 'orders.txt'), logEntry);

        res.status(200).json({ message: 'Order submitted successfully!' });

    } catch (error) {
        console.error(error);
        res.status(500).send('Server error processing order.');
    }
});

// Start Server
app.listen(PORT, () => {
    console.log(`Server running on port ${PORT}`);
});