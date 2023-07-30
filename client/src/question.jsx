import React, { useState } from "react";
import { Box, Button, Checkbox, FormControl, FormControlLabel, FormLabel, Grid, MenuItem, Select, TextField } from "@mui/material";
import useStore from "./store";
import "./style/question.scss";

const QuestionView = () => {
  const [showForm, setShowForm] = useState(false);
  const [params, setParams] = useState({
    temperature: 0.2,
    chain: "stuff",
    sources: false,
    verbose: false,
    k: 5,
    model: "gpt-3.5-turbo-16k",
    embedding_size: "350",
  });

  const handleChange = (e) => {
    const { name, value } = e.target;
    setParams((prevParams) => ({ ...prevParams, [name]: value }));
  };

  const handleComputeAnswer = () => {
    setShowForm(true);
  };

  const cancelForm = () => {
    setShowForm(false);
  };
  const setIncoming = useStore((state) => state.setIncoming);
  const appendMessage = useStore((state) => state.appendMessage);
  const questionData = useStore((store) => store.questionData);
  const text = useStore(state => state.text);
  const setText = useStore(state => state.setText);
  const [answerSheet, showAnswerSheet] = useState(false);
  const setNotice = useStore(state => state.setNotice);

  const handleVerifyAnswer = async () => {
    if (text.trim()) {
      appendMessage({
        role: "user",
        content: "Verify if my answer for this question is correct. If not, please provide the correct answer and explain where I went wrong.\n\n" +
          "question: " + questionData["enunciate"] + "\n\n" +
          "answer sheet: " + questionData["answer"] + "." + questionData["explanation"] + "\n\n" +
          "my answer: " + text,
        send: true,
      });
      setText("");
    }
    else {
      setNotice("Please type an answer before clicking");
    }
  }

  const handleCompareAnswers = async () => {
    const cached = JSON.parse(localStorage.getItem(`answer_${questionData["addr"].trim()}`));
    if (cached && (Date.now() - new Date(cached.timestamp) < 24 * 60 * 60 * 1000)) {
      appendMessage({
        role: "user",
        content: "Analyze and discuss this answer. Expand and discuss related microeconomics concepts. Assume the answer key is always the correct answer.\n\n" +
        "question=\n" + questionData["enunciate"] + "\n\n" +
        "answer key=\n" + questionData["answer"] + "." + questionData["explanation"] + "\n\n",
        send: true,
      });
    }
    else {
      setNotice("Please COMPUTE ANSWER before analyzing");
    }
  };

  const FetchComputeAnswer = async () => {
    const apiUrl = process.env.API_URL || '/api';
    const localStorageKey = `answer_${questionData["addr"].trim()}`;

    appendMessage({
      content: questionData["enunciate"],
      role: "user"
    });
    setIncoming("\u258C");

    const response = await fetch(`${apiUrl}/qa`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        ...params,
        query: questionData["enunciate"],
      }),
    });

    let completeResponse = "";
    const decoder = new TextDecoder("utf-8");

    let incoming_content = "";
    async function processResponse() {
      let reader = response.body.getReader();
      let doneIndex = -1;
      let jsonPayload = "";

      while (true) {
        const { done, value: chunk } = await reader.read();
        if (done) {
          break;
        }

        let chunk_str = decoder.decode(chunk);

        if (doneIndex == -1) {
          doneIndex = chunk_str.indexOf("\n\n**DONE**");
          if (doneIndex !== -1) {
            let doneChunk = chunk_str.substring(doneIndex, chunk_str.length);
            try {
              jsonPayload = JSON.parse(doneChunk.replace("\n\n**DONE**\n\n", ""));
              chunk_str = chunk_str.substring(0, doneIndex);
            }
            catch (e) {
              console.error(`Error parsing JSON: ${e}\n$${doneChunk}`);
            }
          }
          else {
            jsonPayload += chunk_str;
          }
          incoming_content += chunk_str;
          setIncoming(incoming_content + "\u258C");
        }
      }
      setIncoming("");
      let thought = null;
      let content = incoming_content;
      if (jsonPayload && jsonPayload["result"]) {
        content = jsonPayload["result"];
        thought = incoming_content.slice(0,incoming_content.length - content.length);
      }
      appendMessage({
        content: content,
        role: "system",
        temperature: 0,
        thought: thought,
        source_documents: jsonPayload["source_documents"],
        params: params,
      });
      localStorage.setItem(localStorageKey, JSON.stringify({content: content, timestamp: new Date().toISOString()}));
    }
    processResponse();
  };

  return (
    <div>
      {questionData && questionData["exam"] && (
        <>
          <div className="question-data">
            <div className="question-id">
              {questionData["exam"]} exam, year {questionData["year"]}, part{" "}
              {questionData["part"]}, number {questionData["number"]}
            </div>
            <div className="question-enunciate">
              {questionData["enunciate"]}
            </div>
            <div className={`question-answer ${answerSheet ? "show" : "hide"}`}>
              {[questionData["answer"], questionData["explanation"]].join(",")}
            </div>
          </div>
          <div>
            <Box>
              <Button className="answer" onClick={handleComputeAnswer}>Compute Answer</Button>
              <Button className="verify" onClick={handleVerifyAnswer}>Verify my answer</Button>
              <Button className="show" onClick={() => showAnswerSheet(!answerSheet)}>
                {answerSheet ? "Hide answer key" : "Show answer key"}
              </Button>
              <Button className="show" onClick={handleCompareAnswers}>Analyze answer key</Button>
            </Box>

            {showForm &&
            <Box className='parameter-form'>
                <form>
                    <FormControl component="fieldset">
                        <FormLabel component="legend">Parameters</FormLabel>
                        <Grid container spacing={3}>
                            <Grid item xs={12} sm={6} md={6}>
                                <TextField label="Temperature" name="temperature" value={params.temperature} onChange={handleChange} />
                            </Grid>
                            <Grid item xs={12} sm={6} md={6}>
                                <TextField label="#Sources" name="k" value={params.k} onChange={handleChange} />
                            </Grid>
                            <Grid item xs={12} sm={6} md={6}>
                                <FormControl fullWidth className="select">
                                    <FormLabel>Chain</FormLabel>
                                    <Select name="chain" value={params.chain} onChange={handleChange}>
                                    <MenuItem value="stuff">stuff</MenuItem>
                                    <MenuItem value="refine">refine</MenuItem>
                                    <MenuItem value="map_reduce">map_reduce</MenuItem>
                                    <MenuItem value="map_rerank">map_rerank</MenuItem>
                                    </Select>
                                </FormControl>
                            </Grid>
                            <Grid item xs={12} sm={6} md={6}>
                                <FormControl fullWidth className="select">
                                    <FormLabel>Model</FormLabel>
                                    <Select name="model" value={params.model} onChange={handleChange}>
                                    <MenuItem value="gpt-3.5-turbo-16k">gpt-3.5-turbo-16k</MenuItem>
                                    <MenuItem value="gpt-4">gpt-4</MenuItem>
                                    </Select>
                                </FormControl>
                            </Grid>
                            <Grid item xs={12} sm={6} md={6}>
                                <FormControl fullWidth className="select">
                                    <FormLabel>Embedding size</FormLabel>
                                    <Select name="embedding_size" value={params.embedding_size} onChange={handleChange}>
                                    <MenuItem value="350">350</MenuItem>
                                    <MenuItem value="750">750</MenuItem>
                                    <MenuItem value="1500">1500</MenuItem>
                                    <MenuItem value="3000">3000</MenuItem>
                                    </Select>
                                </FormControl>
                            </Grid>
                            <Grid item xs={12} sm={6} md={3}>
                                <FormControlLabel
                                    control={<Checkbox name="sources" checked={params.sources} onChange={(e) => handleChange({ target: { name: e.target.name, value: e.target.checked } })} />}
                                    label="Retrieve sources"
                                />
                            </Grid>
                            <Grid item xs={12} sm={6} md={3}>
                                <FormControlLabel
                                    control={<Checkbox name="verbose" checked={params.verbose} onChange={(e) => handleChange({ target: { name: e.target.name, value: e.target.checked } })} />}
                                    label="Verbose"
                                />
                            </Grid>
                        </Grid>
                    </FormControl>
                    <Box className='footer'>
                        <Button type="submit" variant="contained" color="primary" onClick={async (e) => {e.preventDefault(); setShowForm(false); await FetchComputeAnswer();}}>Submit</Button>
                        <Button type="button" variant="contained" color="secondary" onClick={cancelForm}>
                            Cancel
                        </Button>
                    </Box>
                </form>
            </Box>
            }
          </div>
        </>
      )}
    </div>
  );
};

export default QuestionView;
