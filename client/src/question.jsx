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
    // Compute answer logic goes here
  };

  const cancelForm = () => {
    setShowForm(false);
  };
  const setIncoming = useStore((state) => state.setIncoming);
  const appendMessage = useStore((state) => state.appendMessage);
  const questionData = useStore((store) => store.questionData);
  const [answerSheet, showAnswerSheet] = useState(false);

  const HandleComputeAnswer = async () => {
    setIncoming("\u258C");
    const response = await fetch("/api/qa", {
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
            jsonPayload = JSON.parse(doneChunk.replace("\n\n**DONE**\n\n", ""));
            chunk_str = chunk_str.substring(0, doneIndex);
          }
          else {
            jsonPayload += chunk_str;
          }
          incoming_content += chunk_str;
          setIncoming(incoming_content + "\u258C");
        }
      }
      setIncoming("");
      const thought = incoming_content.slice(0,incoming_content.length - jsonPayload["result"].length);
      appendMessage({
        content: jsonPayload["result"],
        role: "system",
        temperature: 0,
        thought: thought,
        source_documents: jsonPayload["source_documents"]
      });
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
              <Button className="answer" onClick={handleComputeAnswer}>
                Compute Answer
              </Button>
              <Button className="show">Verify my answer</Button>
              <Button
                className="show"
                onClick={() => showAnswerSheet(!answerSheet)}
              >
                {answerSheet ? "Hide answer sheet" : "Show answer sheet"}
              </Button>
              <Button className="show">Lookup Sources</Button>
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
                                <FormControl fullWidth>
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
                                <FormControl fullWidth>
                                    <FormLabel>Model</FormLabel>
                                    <Select name="model" value={params.model} onChange={handleChange}>
                                    <MenuItem value="gpt-3.5-turbo-16k">gpt-3.5-turbo-16k</MenuItem>
                                    <MenuItem value="gpt-4">gpt-4</MenuItem>
                                    </Select>
                                </FormControl>
                            </Grid>
                            <Grid item xs={12} sm={6} md={6}>
                                <FormControl fullWidth>
                                    <FormLabel>Embedding size</FormLabel>
                                    <Select name="model" value={params.embedding_size} onChange={handleChange}>
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
                                    label="Debug"
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
                        <Button type="submit" variant="contained" color="primary" onClick={async (e) => {e.preventDefault(); setShowForm(false); await HandleComputeAnswer();}}>Submit</Button>
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
