import React, { useState, useRef } from "react";
import { Box, Button, Checkbox, FormControl, FormControlLabel, FormLabel, Grid, MenuItem, Select, TextField } from "@mui/material";
import useStore from "./store";
import "./style/custom_query.scss";
import TextareaAutosize from "react-textarea-autosize";

const CustomQueryView = () => {
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

  const setIncoming = useStore((state) => state.setIncoming);
  const appendMessage = useStore((state) => state.appendMessage);
  const text = useStore(state => state.text);
  const setText = useStore(state => state.setText);
  const setNotice = useStore(state => state.setNotice);
  const textareaRef = useRef(null);
  const [query, setQuery] = useState("");

  const handleVerifyAnswer = async () => {
    if (text.trim()) {
      appendMessage({
        role: "user",
        content: "Verify if my answer for this question is correct. If not, please provide the correct answer and explain where I went wrong.\n\n" +
          "question: " + query + "\n\n" +
          "my answer: " + text,
        send: true,
      });
      setText("");
    }
    else {
      setNotice("Please type an answer before clicking");
    }
  }

  const FetchComputeAnswer = async () => {
    const apiUrl = process.env.REACT_APP_API_URL || '/api';

    appendMessage({
      content: query,
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
        query: query,
      }),
    });

    const decoder = new TextDecoder("utf-8");

    let incoming_content = "";
    async function processResponse() {
      let reader = response.body.getReader();
      let doneIndex = -1;
      let jsonPayload = "";

      // eslint-disable-next-line no-constant-condition
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
    }
    processResponse();
  };

  const handleSubmit = async () => {

  }

  // On keydown, if enter is pressed, submit the message
  const handleKeyDown = (event) => {
    if (event.key === 'Enter' && !event.shiftKey) {
      event.preventDefault();
      handleSubmit();
    }
  };

  return (
    <div>
        <div className="query-data">
            <TextareaAutosize
                className="custom-query"
                placeholder="Type your question here"
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                onKeyDown={handleKeyDown}
                ref={textareaRef}
                rows={10}
                />
        </div>
        <div>

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
                    <Button type="submit" variant="contained" color="primary" onClick={async (e) => {e.preventDefault(); await FetchComputeAnswer();}}>Compute Answer</Button>
                    <Button className="verify" onClick={handleVerifyAnswer}>Verify my answer</Button>
                </Box>
            </form>
        </Box>
        </div>
    </div>
  );
};

export default CustomQueryView;


// In a perfectly contestable market, price equals marginal cost.
