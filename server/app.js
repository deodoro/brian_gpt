import express from 'express';
import bodyParser from 'body-parser';
import { chat_handler } from './chat_handler.js';
import { qa_handler } from './qa_handler.js';
// import { extract_handler, summarize_handler } from './content_handler.js';
import db_handlers from './db_handler.js';
import morgan from 'morgan';
import path from 'path';
import multer from 'multer';
import dotenv from 'dotenv';
import { fileURLToPath } from 'url';
import { dirname } from 'path';

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

dotenv.config();

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

app.use('/api', db_handlers);
app.post('/api/chat', bodyParser.json(), chat_handler);
app.post('/api/qa', bodyParser.json(), qa_handler);

const port = process.env.PORT || 7071;
app.listen(port, () => {
    console.log(`Server listening on port ${port}`);
});
