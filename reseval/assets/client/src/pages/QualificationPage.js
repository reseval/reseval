import React, { useState } from 'react';
import Chance from 'chance';

import Button from '../components/Button';
import Markdown from '../components/markdown';
import Question, { validate } from '../questions/Question';

import assignments from '../json/assignments.json';
import config from '../json/config.json';


/******************************************************************************
Constants
******************************************************************************/


// Random number generator
const chance = new Chance();

// Valid characters for random participant ID
const characters =
    'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789';

// Application URL
const url = window.location.protocol + '//' + window.location.host;


/******************************************************************************
Prescreening survey
******************************************************************************/


export default function QualificationPage({
    navigation,
    participant,
    setParticipant,
    completionCode,
    setFiles,
    setConditions }) {
    /* Render the prescreening questions asked to the participant */
    const [index, setIndex] = useState(0);
    const [response, setResponse] = useState(undefined);

    // Get the current question
    const questions = config.prescreen_questions;

    function onClick() {
        // Do not proceed if the respons is invalid
        if (questions.length > 0 && !validate(response)) return;

        // Values to send to database
        let values = {};

        // Either use cached participant or create new participant
        let route;
        if (typeof participant === 'undefined') {
            values['ID'] = chance.string({ length: 32, pool: characters });
            values['CompletionCode'] = completionCode;
            setParticipant(values['ID']);
            route = 'insert';
        } else {
            values['ID'] = participant;
            route = 'update';
        }

        // Add response
        if (questions.length > 0) { values[questions[index].name] = response; }

        // If the response is wrong, end the survey
        if (questions.length > 0 &&
            'correct_answer' in questions[index] &&
            response !== questions[index].correct_answer) {

            // Upload response to database
            fetch(url + '/api/participants/' + route, {
                method: 'post',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(values)
            });

            // End survey
            navigation.go('end');
        } else {
            // Upload response to database
            // TODO - insert may be failing
            fetch(url + '/api/participants/' + route, {
                method: 'post',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(values)
            }).then(_ => {
                if (index + 1 >= questions.length) {

                    // Get evaluation files for this evaluator
                    fetch(url + '/api/evaluators/')
                        .then(response => response.json())
                        .then(response => setFiles(assignments[response]))

                        // Get list of evaluation conditions
                        // TODO - this fetch may be failing
                        .then(_ => {
                            fetch(url + '/api/conditions')
                                .then(response => response.json())
                                .then(response => {
                                    setConditions(
                                        response.map(
                                            cond => cond.Condition))

                                // Go to evaluation
                                }).then(_ => navigation.next())
                        });
                }
            });
        }

        // Go to next question
        if (index + 1 < questions.length) {
            setIndex(index + 1);
            setResponse(undefined);
        }
    };

    // Skip prescreening if there are no questions
    if (questions.length === 0) { onClick(); }

    // Render
    return (
        <div className='container grid'>
            <Markdown>
                {`**Question ${index + 1}** ${questions[index].text}`}
            </Markdown>
            <Question
                question={questions[index]}
                response={response}
                setResponse={setResponse}
            />
            <Button onClick={onClick}>Next</Button>
        </div>
    );
}
