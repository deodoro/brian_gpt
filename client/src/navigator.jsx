import React, { useEffect, useState } from 'react';
import axios from 'axios';
import useStore from './store';
import QuestionView from './question'
import './style/navigator.scss'

const Navigator = () => {
  const [years, setYears] = useState([]);
  const [exams, setExams] = useState([]);
  const [questions, setQuestions] = useState([]);
  const [selectedYear, setSelectedYear] = useState(null);
  const [selectedExam, setSelectedExam] = useState(null);
  const [selectedQuestion, setSelectedQuestion] = useState(null);
  const questionData = useStore(store => store.questionData);
  const setQuestionData = useStore(store => store.setQuestionData);

  useEffect(() => {
    const fetchYears = async () => {
      try {
        const response = await axios.get('/api/years');
        setYears(response.data);
      } catch (error) {
        console.error('Failed to fetch years', error);
      }
    };

    fetchYears();
  }, []); // An empty dependency array ensures this effect runs only once on component mount.

  useEffect(() => {
    const fetchQuestions = async () => {
      try {
        const response = await axios.get(`/api/questions/${selectedYear}`);
        setQuestions(response.data);
      } catch (error) {
        console.error('Failed to fetch questions', error);
      }
    };

    const fetchExams = async () => {
      try {
        const response = await axios.get(`/api/exams/${selectedYear}`);
        setExams(response.data);
      } catch (error) {
        console.error('Failed to fetch years', error);
      }
    };

    if (selectedYear) {
      fetchExams();
      fetchQuestions();
    }
  }, [selectedYear]);

  useEffect(() => {
    const fetchQuestions = async () => {
      try {
        const response = await axios.get(`/api/questions/${selectedYear}/${selectedExam}`);
        setQuestions(response.data);
      } catch (error) {
        console.error('Failed to fetch questions', error);
      }
    };

    if (selectedYear && selectedExam) {
      fetchQuestions();
    }
  }, [selectedExam]);

  useEffect(() => {
    const fetchQuestion = async () => {
      try {
        const response = await axios.get(`/api/question/${selectedQuestion}`);
        setQuestionData(response.data);
      } catch (error) {
        console.error('Failed to fetch questions', error);
      }
    };

    if (selectedQuestion)
      fetchQuestion();
  }, [selectedQuestion]);

  return (
    <div className='navigator'>
      {years.map((year, index) => (
        <div key={index} onClick={() => {setSelectedYear(year); setSelectedExam(null); setSelectedQuestion(null);}} className={`year ${year == selectedYear ? 'selected' : ''}`}>
          {year}
        </div>
      ))}
      {exams.map((exam, index) => (
        <div key={index} onClick={() => {setSelectedExam(exam); setSelectedQuestion(null);}} className={`exam ${exam == selectedExam ? 'selected' : ''}`}>
          {exam}
        </div>
      ))}
      {questions.map((question, index) => (
        <div key={index}  className={`question ${question["id"] == selectedQuestion ? 'selected' : ''}`} onClick={() => setSelectedQuestion(question["id"])}>
          <div className="question-var">{question["addr"]}</div>
        </div>
      ))}
      <QuestionView />
    </div>
  );
};

export default Navigator;

/*
Temperature -> [0, 2]
Chain -> ["stuff", "refine", "map_reduce", "map_rerank"]
Sources -> True/False
Quantity of sources to retrieve -> 5
Model -> 'gpt-3.5-turbo-16k', 'gpt-4'
*/
