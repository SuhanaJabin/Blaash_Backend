const express = require('express');
const mongoose = require('mongoose');
const routes = require('./routes');
const app = express();

const port = 3001;


app.use(express.json()); 
app.use('/api', routes); 


mongoose.connect('mongodb://localhost:27017/expense_manager', { useNewUrlParser: true, useUnifiedTopology: true })
    .then(() => {
        console.log('Connected to MongoDB');
        app.listen(port, () => console.log(`Server is running on port ${port}`));
    })
    .catch(err => console.error('Failed to connect to MongoDB', err));


const db = mongoose.connection;
db.on('error', console.error.bind(console, 'connection error:'));
db.once('open', function () {
    console.log('MongoDB connection is open');
});
