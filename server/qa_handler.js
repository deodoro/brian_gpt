import { createClient } from "redis";
import { OpenAI } from "langchain/llms/openai";
import { OpenAIEmbeddings } from "langchain/embeddings/openai";
import { RetrievalQAChain } from "langchain/chains";
import { RedisVectorStore } from "langchain/vectorstores/redis";
import { MergerRetrieveChain } from "langchain/chains/mergeretrieve";
import { Readable } from 'stream';

const qa = async (query) => {
    const llm = new OpenAI({openAIApiKey: process.env.OPENAI_API_KEY});
    const client = createClient({
        url: process.env.REDIS_URL ?? "redis://localhost:6379",
      });
      await client.connect();
      const stores = ['paper', 'book', 'blog', 'lecture', 'notes'].map((name) => {
        return new RedisVectorStore(new OpenAIEmbeddings(), {
            redisClient: client,
            indexName: `${name}_350`,
          });
      });
      const vectorStore = new MergerRetrieveChain(stores);
      const chain = RetrievalQAChain.fromLLM(llm, vectorStore.asRetriever(5), {
        returnSourceDocuments: true,
      });
      const chainRes = await chain.call({ query: query });
      console.dir(chainRes);
      return chainRes;
}

const qa_handler = async (req, res) => {
  const t = await qa(req.body['query']);
  let jsonStr = JSON.stringify(t, null, 2);
  console.log(jsonStr);

  let readStream = new Readable({
    read() {
      this.push(jsonStr);
      this.push(null); // indicates end-of-file basically - the end of the stream
    }
  });

  res.setHeader('Content-Type', 'application/json');

  readStream.on('data', chunk => {
    res.write(chunk);
  });

  readStream.on('end', () => {
    res.end();
  });
};

export { qa_handler };
