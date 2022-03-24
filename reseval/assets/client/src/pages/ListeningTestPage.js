import React, {createContext, useMemo, useState} from 'react';

import Markdown from '../components/Markdown';

import config from '../json/config.json';

import '../css/components.css';
import ListeningTest from "../questions/ListeningTest";
import {validate} from "../questions/Question";
import Button from "../components/Button";


/******************************************************************************
 Constants
 ******************************************************************************/


// Application URL
const url = window.location.protocol + '//' + window.location.host;

// Global state of any currently playing media
export const MediaContext = createContext({
    mediaRef: '',
    setMediaRef: () => {
    }
});


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


    function onClick() {
        // Do not proceed if the response is invalid
        if (config.if_listening_test === false) return;


        // If the response is wrong, end the survey
        // if (questions.length > 0 &&
        //     'correct_answer' in questions[index] &&
        //     response !== questions[index].correct_answer)
        if (response !=='1')
        {

            // End survey
            navigation.go('end');
        } else {
            navigation.next()
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
            <Markdown>
                {`**Question 1 of 1**\n` +
                config.listening_test_instructions}
            </Markdown>
            <ListeningTest response={response} setResponse={setResponse}/>
            <Button onClick={onClick}>Next</Button>
        </div>
    );
};
