import React, {useMemo, useRef, useState} from 'react';

import Markdown from '../components/Markdown';

import config from '../json/config.json';

import '../css/components.css';
import ListeningTest from "../questions/ListeningTest";
import Button from "../components/Button";
import Media from "../components/Media";
import {validate} from "../questions/Question";
import Chance from 'chance';


/******************************************************************************
 Constants
 ******************************************************************************/


// Application URL
const url = window.location.protocol + '//' + window.location.host;
// Random number generator
const chance = new Chance();


/******************************************************************************
 Prescreening survey
 ******************************************************************************/


export default function ListeningTestPage({
                                              navigation,
                                              participant,
                                              setParticipant,
                                              completionCode,
                                              setFiles,
                                              setConditions
                                          }) {
    /* Render the prescreening questions asked to the participant */
    const refTest = useRef();
    const [index, setIndex] = useState(0);
    const [response, setResponse] = useState(undefined);
    const test_length = config.listening_test_question_count;

    // randomly get listening test examples
    function getRandomSample() {
        let file = []
        let i = 0;
        while (i < test_length) {
            let idx = chance.integer({min: 0, max: 3})
            let tone = chance.integer({min: 4, max: 8})
            file.push(`tones${tone}_${idx}.wav`)
            i+=1
        }
        return file
    }

    const file = useMemo(getRandomSample, [test_length])
    let correct_response = file[index].split('.')[0].split('_')[0].slice(-1)


    function onClick() {
        // Do not proceed if the response is invalid
        if (config.if_listening_test === false || !validate(response)) return;


        if (response !== correct_response) {

            // End survey
            navigation.go('end');
        } else {
            if (index + 1 >= test_length) {
                navigation.next()
            }
        }
        // Go to next question
        if (index + 1 < test_length) {
            setIndex(index + 1);
            setResponse(undefined);
        }
    }

    // Skip listening test if there are no questions
    if (config.if_listening_test === false) {
        onClick();
        return null;
    }

    // Render
    return (
        <div className='container'>
            <p> listening test</p>
            <div className='grid grid-20-80'>
                <div style={{width: '100%'}}/>
                <Media
                    reference={refTest}
                    onEnded={() => {

                    }}
                    src={'listening_test_file/' + file[index]}
                />
            </div>
            <Markdown>
                {`**Question ${index + 1} of ${test_length}**\n` +
                config.listening_test_instructions}
            </Markdown>
            <ListeningTest response={response} setResponse={setResponse}/>
            <Button onClick={onClick}>Next</Button>
        </div>
    );
};
