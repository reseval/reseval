import { useState } from 'react';

import Button from '../components/Button';
import Markdown from '../components/Markdown';
import Question, { validate } from '../questions/Question';

import config from '../json/config.json';


/******************************************************************************
Constants
******************************************************************************/


const url = window.location.protocol + '//' + window.location.host;


/******************************************************************************
Follow-up Survey
******************************************************************************/


export default function FeedbackPage({ navigation, participant }) {
    /* Render the prescreening questions asked to the participant */
    const [index, setIndex] = useState(0);
    const [response, setResponse] = useState(undefined);

    // Skip if we have no questions
    const questions = config.followup_questions;
    if (typeof questions === 'undefined') {
        window.scroll(0, 0);
        navigation.next();
        return <></>;
    }

    // Get the current question
    const question = questions[index];

    function onClick() {
        // Do not proceed if the respons is invalid
        if (!validate(response)) return;

        // Get the name of the question
        const name = question.name;

        // Upload response to database
        fetch(url + '/api/participants/update', {
            method: 'post',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ ID: participant, [name]: response })
        });

        // If the response is wrong, end the survey
        if ('correct_answer' in question &&
            response !== question.correct_answer) {
            window.scroll(0, 0);
            navigation.go('end');
        }

        // Go to next question
        else if (index + 1 < questions.length) {
            setIndex(index + 1);
            setResponse(undefined);
            window.scroll(0, 0);
        }

        // Finished survey
        else {
            window.scroll(0, 0);
            navigation.next();
        }
    }

    // Render
    return (
        <div className='container'>
            <Markdown>
                {
                    `## **Post-Evaluation Survey**\n` +
                    `**Question ${index + 1} of ${questions.length}**\n` +
                    question.text
                }
            </Markdown>
            <Question
                question={question}
                response={response}
                setResponse={setResponse}
            />
            <Button
                active={typeof response !== 'undefined' && response.trim()}
                onClick={onClick}
            >
                Submit
            </Button>
        </div>
    );
}
