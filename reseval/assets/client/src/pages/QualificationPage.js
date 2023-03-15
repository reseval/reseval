import React, {useMemo, useRef, useState} from 'react';
import Chance from 'chance';

import Button from '../components/Button';
import Markdown from '../components/Markdown';
import Media from "../components/Media";
import ListeningTest from "../questions/ListeningTest";
import Question, {validate} from '../questions/Question';

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
    setConditions,
    setEvaluatorId
}) {
    /* Render the prescreening questions asked to the participant */
    const [index, setIndex] = useState(0);
    const [response, setResponse] = useState(undefined);

    // Question type can be "prescreen" or "listening-test"
    const [questionType, setQuestionType] = useState('prescreen')

    // Whether the listening test has finished
    let if_finish = false

    // Get the current question
    const questions = config.prescreen_questions;

    // Listening test index
    const [testIndex, setTestIndex] = useState(0);
    const [audioEnded, setAudioEnded] = useState(false);

    // Listening test retries
    const [retries, setRetries] = useState(undefined);

    // Listening test audio reference
    const refTest = useRef();

    // Number of listening test examples
    let test_length = 0;
    if ('listening_test' in config) {
        test_length = config.listening_test.num_questions;
        if (retries === undefined) {
            setRetries(config.listening_test.retries);
        }
    }

    // The listening test audio
    const file = useMemo(getRandomSample, [test_length])

    function getRandomSample() {
        /* Retrieve a random audio files for listening test */
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

    function listeningTest() {
        /* Interaction logic for listening test */
        // Skip if we are not performing a listening test
        if (!('listening_test' in config)) {
            if_finish = true;
            return;
        }

        // Change question type for listening test
        if (questionType !== 'listening-test') {
            setQuestionType('listening-test');
            return;
        }

        // Parse the true number of tones from the filename
        let correct_response =
            file[testIndex].split('.')[0].split('_')[0].slice(-1);

        // Fail prescreening if the wrong answer is given
        if (response !== correct_response) {
            if (retries > 0) {
                const plural = retries > 1 ? 's' : '';
                const message = `Incorrect. Please put on headphones, move ` +
                    `to a quiet location, and try again. You have ` +
                    `${retries} attempt${plural} remaining.`
                alert(message);
                setRetries(retries - 1);
                return;
            } else {
                window.scroll(0, 0);
                navigation.go('end');
            }
        } else {
            // End listening test if we've answered enough questions
            if (testIndex + 1 >= test_length) {
                if_finish = true
                return
            }
        }

        // Go to next question
        if (testIndex + 1 < test_length) {
            setAudioEnded(false)
            setTestIndex(testIndex + 1);
            setRetries(config.listening_test.retries);
            setResponse(undefined);
            window.scroll(0, 0);
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
                    // enter listening test
                    listeningTest()
                    // do not proceed until listening test is finished
                    if (!if_finish) {
                        return
                    }
                    // Get evaluation files for this evaluator
                    fetch(url + '/api/participants/')
                        .then(response => response.json())
                        .then(response => {
                            const evaluatorId = response.length - 1;
                            setFiles(
                                assignments[evaluatorId % assignments.length]);
                            setEvaluatorId(evaluatorId);
                        })

                        // Get list of evaluation conditions
                        .then(_ => {

                            if (config.test === 'wordselect') {
                                navigation.next();
                            } else {
                                fetch(url + '/api/conditions')
                                    .then(response => response.json())
                                    .then(response => {
                                        setConditions(
                                            response.map(
                                                cond => cond.Condition))

                                        // Go to evaluation
                                    }).then(_ => {
                                        window.scroll(0, 0);
                                        navigation.next();
                                    })
                            }
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
        if (!('listening_test' in config)) {
            onClick();
            return null
        } else if (questionType === 'prescreen') {
            setQuestionType('listening-test');
        }
    }

    if (questionType === 'listening-test') {
        // Render listening test
        return (
            <div className='container'>
                <Markdown>
                    {`**Question ${testIndex + 1} of ${test_length}**\n` +
                    config.listening_test.instructions}
                </Markdown>
                <Media
                    reference={refTest}
                    onEnded={() => setAudioEnded(true)}
                    src={'listening_test/' + file[testIndex]}
                />
                <ListeningTest
                    response={response}
                    setResponse={setResponse}
                    active={audioEnded}
                />
                <Button
                    active={audioEnded && typeof response !== 'undefined'}
                    onClick={() => {
                        typeof response !== 'undefined' &&
                        audioEnded &&
                        onClick()
                    }}
                >
                    Next
                </Button>
            </div>
        );
    } else if (questions.length !== 0) {
        // Render prescreening question
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
                <Button
                    active={typeof response !== 'undefined' && response.trim()}
                    onClick={onClick}
                >
                    Next
                </Button>
            </div>
        );
    } else { return <></>; }
}
