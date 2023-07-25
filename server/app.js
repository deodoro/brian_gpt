const express = require('express');
const { chat_handler } = require('./chat_handler');
const { extract_handler, summarize_handler } = require('./content_handler');
const morgan = require('morgan');
const path = require('path');
const multer = require('multer');

require('dotenv').config();

const bodyParser = require('body-parser');
const app = express();

const upload = multer({ storage: multer.memoryStorage() });
app.use(morgan('combined'));

app.use(express.static(path.join(__dirname, 'public')));

app.use((req, res, next) => {
    if (!req.path.startsWith('/api')) {
        res.sendFile(path.join(__dirname, 'public/index.html'));
    } else {
        next();
    }
});

app.post('/api/chat', bodyParser.json(), chat_handler);
app.get('/api/extract', bodyParser.json(), extract_handler);
app.post('/api/summarize', upload.single('file'), summarize_handler);

const port = process.env.PORT || 7071;
app.listen(port, () => {
    console.log(`Server listening on port ${port}`);
});
