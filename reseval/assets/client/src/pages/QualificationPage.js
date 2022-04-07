import React, { useMemo, useRef, useState} from 'react';
import Chance from 'chance';

import Button from '../components/Button';
import Markdown from '../components/Markdown';
import Question, {validate} from '../questions/Question';

import assignments from '../json/assignments.json';
import config from '../json/config.json';
import Media from "../components/Media";
import ListeningTest from "../questions/ListeningTest";


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
                                              setConditions
                                          }) {
    /* Render the prescreening questions asked to the participant */
    const [index, setIndex] = useState(0);
    const [response, setResponse] = useState(undefined);
    // question type can be "prescreen" or "test"
    const [questionType, setQuestionType] = useState('prescreen')
    let if_finish = false
    // Get the current question
    const questions = config.prescreen_questions;

    // randomly get listening test examples
    function getRandomSample() {
        let file = []
        let i = 0;
        while (i < test_length) {
            let idx = chance.integer({min: 0, max: 3})
            let tone = chance.integer({min: 4, max: 8})
            file.push(`tones${tone}_${idx}.wav`)
            i += 1
        }
        return file
    }

    // question index for listening test
    const [testIndex, setTestIndex] = useState(0);

    // ref for the listening test audio
    const refTest = useRef();
    // get the listening test length
    let test_length = config.listening_test_question_count;
    if (test_length === undefined) {
        test_length = 0
    }

    const file = useMemo(getRandomSample, [test_length])

    function listeningTest() {
        console.log(correct_response, response)
        // Do not proceed if the response is invalid
        if (!('if_listening_test' in config) || config.if_listening_test === false || !validate(response)) {
            if_finish = true;
            return;
        }

        if (questionType !== 'test') {
            setQuestionType('test');
            return;
        }
        // parse the correct response from file name
        let correct_response = file[testIndex].split('.')[0].split('_')[0].slice(-1)

        if (response !== correct_response) {
            console.log('end survey')
            // End survey
            navigation.go('end');
        } else {
            if (testIndex + 1 >= test_length) {
                if_finish = true
                // navigation.next()
            }
        }
        // Go to next question
        if (testIndex + 1 < test_length) {
            setTestIndex(testIndex + 1);
            setResponse(undefined);
        }
    }


    function onClick() {
        // Do not proceed if the response is invalid
        if (questions.length > 0 && !validate(response)) return;

        // Values to send to database
        let values = {};

        // Either use cached participant or create new participant
        let route;
        if (typeof participant === 'undefined') {
            values['ID'] = chance.string({length: 32, pool: characters});
            values['CompletionCode'] = completionCode;
            setParticipant(values['ID']);
            route = 'insert';
        } else {
            values['ID'] = participant;
            route = 'update';
        }

        // Add response
        if (questions.length > 0) {
            values[questions[index].name] = response;
        }

        // If the response is wrong, end the survey
        if (questionType === 'prescreen' && questions.length > 0 &&
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
            fetch(url + '/api/participants/' + route, {
                method: 'post',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(values)
            }).then(_ => {
                if (index + 1 >= questions.length) {
                    console.log('finished prescreening')

                    listeningTest()
                    // do not proceed until listening test finished
                    if (!if_finish) {
                        return
                    }
                    // Get evaluation files for this evaluator
                    fetch(url + '/api/evaluators/')
                        .then(response => response.json())
                        .then(response => setFiles(
                            assignments[response % assignments.length]))

                        // Get list of evaluation conditions
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
    }

    // Skip prescreening if there are no questions
    if (questions.length === 0) {
        if (!('if_listening_test' in config) || config.if_listening_test === false) {
            onClick();
            return null
        } else if (questionType === 'prescreen') {
            setQuestionType('test');
        }
    }

    if (questionType === 'test') {
        console.log('test_rendered!')
        // Render Listening test
        return (
            <div className='container'>
                <div className='grid grid-20-80'>
                    <div style={{width: '100%'}}/>
                </div>
                <Markdown>
                    {`**Question ${testIndex + 1} of ${test_length}**\n` +
                    config.listening_test_instructions}
                </Markdown>
                <Media
                    reference={refTest}
                    onEnded={() => {
                    }}
                    src={'listening_test_file/' + file[testIndex]}
                />
                <ListeningTest response={response} setResponse={setResponse}/>
                <Button onClick={onClick}>Next</Button>
            </div>
        );
    } else if (questions.length !== 0) {
        console.log(questions.length)
        console.log('question_rendered!')
        // Render Question
        return (
            <div className='container'>
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
    } else {
        console.log('nothing rendered!')
        return <></>
    }
}
