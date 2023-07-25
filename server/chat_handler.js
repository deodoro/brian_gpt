const { Configuration, OpenAIApi } = require("openai");

require('dotenv').config();
console.log(process.env.OPENAI_API_KEY);

async function streamToBuffer(readableStream) {
    return new Promise((resolve, reject) => {
      const chunks = [];
      readableStream.on("data", (data) => {
        chunks.push(data instanceof Buffer ? data : Buffer.from(data));
      });
      readableStream.on("end", () => {
        resolve(Buffer.concat(chunks));
      });
      readableStream.on("error", reject);
    });
}

chat_handler = async (req, res) => {
    try {
        let chat = req.body.chat.filter(i => ["system", "user"].includes(i.role));
        let chatId = req.body.chatId;
        let temperature = 0.3 + req.body.temperature * 0.5;

        this.openAiApi = new OpenAIApi(
            new Configuration({
                apiKey: process.env.OPENAI_API_KEY,
            }),
        );

        const response = await this.openAiApi.createChatCompletion({
            model: "gpt-3.5-turbo-16k",
            messages: [
                {role: "system", content: "You are a helpful assistant."},
                ...chat.map(i => ({role: i.role, content: i.content}))
            ],
            temperature: temperature,
            stream: true
        }, { responseType: 'stream' });

        const stream = response.data;
        let result = '';

        res.set({
            'Content-Type': 'text/event-stream;charset=utf-8',
            'Cache-Control': 'no-cache'
        });

        stream.on('data', chunk => {
            const payloads = chunk.toString().split("\n\n");
            let partial = '';
            for (const payload of payloads) {
                if (payload.includes('[DONE]')) return;
                if (payload.startsWith("data:")) {
                    try {
                        const data = JSON.parse(payload.replace("data: ", ""));
                        const chunk = data.choices[0].delta?.content;
                        if (chunk) {
                            res.write(chunk);
                            result += chunk;
                        }
                    }
                    catch (e) {
                        // console.error(e);
                    }
                }
            }
        });

        stream.on('end', async () => {
            res.end();
        });

        stream.on('error', (err) => {
            res.emit('error', err);
        });
    } catch (e) {
        console.error(e);
        res.status(500).send({error: "Internal server error"});
    }
};

module.exports = { chat_handler };
