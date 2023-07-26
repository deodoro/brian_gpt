import React, { useState } from 'react';
import { Button } from '@mui/material';
import useStore from './store';
import './style/question.scss'

const QuestionView = () => {
    const questionData = useStore(store => store.questionData);
    const [answerSheet, showAnswerSheet] = useState(false);

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
                <Button className="answer">
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
