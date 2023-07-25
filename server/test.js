const { OpenAI } = require("langchain/llms/openai");
const { loadSummarizationChain } = require("langchain/chains");
const { RecursiveCharacterTextSplitter } = require("langchain/text_splitter");
const { Configuration, OpenAIApi } = require("azure-openai");
const mammoth = require('mammoth');
const fs = require('fs');
const os = require('os');
const path = require('path');

const MAX_LENTGH = 1000;

require('dotenv').config();

const f = async () => {
    const prompt = `You are a helpful assistant. Write a concise summary of the following.\n\n\n\n`;

    const model = new OpenAI({
        modelName: process.env.AZURE_MODEL_NAME,
        azureOpenAIApiKey: process.env.AZURE_OPENAI_KEY,
        azureOpenAIApiDeploymentName: process.env.AZURE_DEPLOYMENT_NAME,
        azureOpenAIApiInstanceName: process.env.AZURE_INSTANCE_NAME,
        azureOpenAIApiVersion: process.env.AZURE_API_VERSION,
    });

    stripNonPrintableAndRepeatedChars = function(str) {
        // Replace non-printable characters
        let strippedString = str.replace(/[\x00-\x1F]/g, "");

        // Replace repeated characters
        strippedString = strippedString.replace(/(.)\1+/g, "$1");

        return strippedString;
    }

    const do_it = async (text, level) => {
        const textSplitter = new RecursiveCharacterTextSplitter({ chunkSize: 30000 });
        const cleanText = stripNonPrintableAndRepeatedChars(text);
        const docs = await textSplitter.createDocuments([cleanText]);
        const replies = [];
        console.log(`Level ${level} Split ${cleanText.lengh} into ${docs.length} documents`);
        this.openAiApi = new OpenAIApi(
            new Configuration({
                apiKey: this.apiKey,
                azure: {
                    apiKey: process.env.AZURE_OPENAI_KEY,
                    endpoint: process.env.AZURE_ENDPOINT
                }
            }),
        );

        const f = false;
        for (const doc of docs) {
            // if (f) {
            //     await new Promise(resolve => setTimeout(resolve, 5000));
            // }
            // else {
            //     f = true;
            // }
            const reply = await this.openAiApi.createChatCompletion({
                model: process.env.AZURE_DEPLOYMENT_NAME,
                messages: [
                    {role: "system", content: prompt + doc.pageContent}
                ],
                temperature: 0.9,
            });
            replies.push(reply.data.choices[0].message.content);
        }

        const summary = replies.join("\n\n");
        if (summary.length < MAX_LENTGH || level > 3) {
            return summary;
        }
        else {
            return do_it(summary, level + 1);
        }
    }

    const homeDir = os.homedir();
    console.log(path.join(homeDir, 'src/testing/sample.txt'));
    const text = fs.readFileSync(path.join(homeDir, 'src/testing/sample.txt'), 'utf8');
    console.log(await do_it(text, 0));
}

f();
