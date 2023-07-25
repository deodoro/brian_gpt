const { Configuration, OpenAIApi } = require("openai");
const { loadSummarizationChain } = require("langchain/chains");
const { RecursiveCharacterTextSplitter } = require("langchain/text_splitter");
const axios = require('axios');
const pdfParse = require('pdf-parse');
const mammoth = require('mammoth');

require('dotenv').config();

const extract_contents = async (url) => {
    try {
        const response = await axios.get(url, { responseType: 'arraybuffer' });
        const contentType = response.headers['content-type'];

        if (contentType === 'application/pdf') {
            const dataBuffer = Buffer.from(response.data);
            const data = await pdfParse(dataBuffer);
            return data.text;
        } else if (contentType === 'application/vnd.openxmlformats-officedocument.wordprocessingml.document') {
            const { value } = await mammoth.extractRawText({ buffer: Buffer.from(response.data) });
            return value;
        } else if (contentType === 'text/plain') {
            const text = Buffer.from(response.data).toString('utf8');
            return text;
        }
    }
    catch (err) {
        console.log(err);
    }
    return null;
};

const extract_handler = async (req, res) => {
    if (!req.query.url) {
        return res.status(400).send('Missing URL parameter');
    }

    const contents = await extract_contents(req.query.url);

    if (contents === null) {
        res.status(400).send('Unsupported file type');
    }
    else {
        res.send(contents);
    }
};

const run_langchain = async (text) => {
    try {
        const model = new OpenAIApi(
            new Configuration({
                model: "gpt-3.5-turbo-16k",
                apiKey: process.env.OPENAI_API_KEY,
            }),
        );
        const textSplitter = new RecursiveCharacterTextSplitter({ chunkSize: 20000 });
        const docs = await textSplitter.createDocuments([text]);
        console.log(`Split into ${docs.length} documents`);

        const chain = loadSummarizationChain(model, { type: "map_reduce" });
        const res = await chain.call({
            input_documents: docs,
        });
        if (res)
            return res.text;
        else
            return null;
    }
    catch (err) {
        console.log(err);
        return null;
    }
}

const run_customized = async (text, MAX_LENTGH) => {
    const prompt = `You are a helpful assistant. Write a summary of the following.\n\n\n\n`;

    const model = new OpenAIApi(
        new Configuration({
            model: "gpt-3.5-turbo-16k",
            apiKey: process.env.OPENAI_API_KEY,
        }),
    );

    stripNonPrintableAndRepeatedChars = function(str) {
        const strippedString = str.replace(/[\x00-\x1F]/g, "");
        return strippedString.replace(/(.)\1+/g, "$1");
    }

    const do_it = async (text, level) => {
        const textSplitter = new RecursiveCharacterTextSplitter({ chunkSize: 30000 });
        const cleanText = stripNonPrintableAndRepeatedChars(text);
        const docs = await textSplitter.createDocuments([cleanText]);
        const replies = [];
        console.log(`Level ${level} Split ${cleanText.lengh} into ${docs.length} documents`);
        this.openAiApi = new OpenAIApi(
            new Configuration({
                apiKey: process.env.OPENAI_API_KEY,
            }),
        );

        let f = false;
        for (const doc of docs) {
            if (f && process.env.model === "gpt-4") {
                // Breathing time for GPT-4 API
                await new Promise(resolve => setTimeout(resolve, 2000));
            }
            else {
                f = true;
            }
            const reply = await this.openAiApi.createChatCompletion({
                messages: [
                    {role: "system", content: prompt + doc.pageContent}
                ],
                temperature: 0.9,
            });
            replies.push(reply.data.choices[0].message.content);
        }

        const summary = replies.join("\n\n");
        if (summary.length < MAX_LENTGH || level > 1) {
            console.log(`Done level ${level}`);
            return summary;
        }
        else {
            return do_it(summary, level + 1);
        }
    }
    return do_it(text, 0);
}

const summarize_handler = async (req, res) => {
    let contents;

    if (req.file) { // If a file is uploaded
        if (req.file.mimetype === 'application/pdf') { // If the file is a PDF
            console.log('Reading contents from uploaded PDF file');
            const data = await pdfParse(req.file.buffer);
            contents = data.text;
        } else {
            return res.status(400).send('Unsupported file type for upload. Only PDF is supported.');
        }
    } else if (req.query.url) { // If a URL is provided
        console.log(`Extracting contents from ${req.query.url}`);
        contents = await extract_contents(req.query.url);

        if (contents === null) {
            return res.status(400).send('Unsupported file type or unable to extract contents from the URL');
        }
    } else {
        return res.status(400).send('Either a URL parameter or a file upload is required');
    }

    console.log(`Summarizing ${contents.length} characters`);
    // const summary = await run_langchain(contents);
    const summary = await run_customized(contents, 2000);
    console.log("Finished");
    res.type('application/json');
    res.send(JSON.stringify({text: summary}));
};

module.exports = {extract_handler, summarize_handler, run_langchain};
