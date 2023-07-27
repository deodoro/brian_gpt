import React, { useState } from 'react';
import { Button } from '@mui/material';
import useStore from './store';
import './style/question.scss'

const QuestionView = () => {
    const setIncoming = useStore(state => state.setIncoming);
    const appendMessage = useStore(state => state.appendMessage);
    const questionData = useStore(store => store.questionData);
    const [answerSheet, showAnswerSheet] = useState(false);

    const HandleComputeAnswer = async () => {

        setIncoming("\u258C")

        const response = await fetch("/api/qa", {
            method: 'POST',
            headers: {
            'Content-Type': 'application/json'
            },
            body: JSON.stringify({
            "query": questionData["enunciate"],
            "temperature": 0.2,
            "chain": "stuff",
            "sources": true,
            "k": 5,
            "model": "gpt-3.5-turbo-16k"
            })
        });

        let completeResponse = "";
        const decoder = new TextDecoder('utf-8');

        let incoming_content = "";
        async function processResponse() {
            let reader = response.body.getReader();
            let doneStreaming = false;

            while (true) {
                let doneIndex = -1;
                const { done, value: chunk } = await reader.read();
                if (done) { break; }

                let chunk_str = decoder.decode(chunk);

                if (doneStreaming) {
                    chunk_str = '';
                }
                else {
                    doneIndex = chunk_str.indexOf('\n\n**DONE**');
                }

                if (doneIndex !== -1) {
                    let doneChunk = chunk_str.substring(doneIndex, chunk_str.length);
                    const json_str = doneChunk.replace('**DONE**\n\n', '');
                    chunk_str = chunk_str.substring(0, doneIndex);
                    doneStreaming = true;
                }
                incoming_content += chunk_str;
                setIncoming(incoming_content + "\u258C");
            }
            appendMessage({ content: incoming_content, role: "system", temperature: 0 });
        }

        processResponse();
    };

    return (
        <div>
           {questionData && questionData["exam"] &&
             <>
                <div className="question-data">
                    <div className="question-id">{questionData["exam"]} exam, year {questionData["year"]}, part {questionData["part"]}, number {questionData["number"]}</div>
                    <div className="question-enunciate">{questionData["enunciate"]}</div>
                    <div className={`question-answer ${answerSheet ? 'show' : 'hide'}`}>{[questionData["answer"], questionData["explanation"]].join(",")}</div>
                </div>
                <div>
                <Button className="answer" onClick={HandleComputeAnswer}>
                    Compute Answer
                </Button>
                <Button className="show">
                    Verify my answer
                </Button>
                <Button className="show" onClick={() => showAnswerSheet(!answerSheet)}>
                    {answerSheet ? "Hide answer sheet" : "Show answer sheet"}
                </Button>
                <Button className="show">
                    Lookup Sources
                </Button>
            </div>
             </>}
        </div>);
}

export default QuestionView;
