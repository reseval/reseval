import React, { useState } from 'react';

import AB from '../test/AB';
import ABX from '../test/ABX';
import MOS from '../test/MOS';
import MUSHRA from '../test/MUSHRA';
import Markdown from '../components/markdown';

import config from '../json/config.json';

import '../css/components.css';


/******************************************************************************
Constants
******************************************************************************/


// Application URL
const url = window.location.protocol + '//' + window.location.host;


/******************************************************************************
Prescreening survey
******************************************************************************/


export default function TaskPage({
    participant,
    navigation,
    files,
    conditions }) {
    /* Render the evaluation task */
    // Current progress
    const [index, setIndex] = useState(0);

    // Response from the participant
    const [response, setResponse] = useState(undefined);

    // Don't render anything until we have files and conditions
    if (typeof files === 'undefined' ||
        typeof conditions === 'undefined') {
        return null;
    }

    // Get current file to evaluate
    const file = files[index];

    function onClick() {
        // Upload response
        fetch(url + '/api/responses', {
            method: 'post',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                'Stem': file.replace(/\.[^/.]+$/, ''),
                'Participant': participant,
                'OrderAsked': index,
                'Response': response
            })
        });

        // Go to next question
        if (index + 1 < files.length) {
            setIndex(index + 1);
            setResponse(undefined);
        }

        // Proceed to follow-up survey
        else { navigation.next(); }
    }

    // Bundle props
    const props = {
        file: file,
        index: index,
        conditions: conditions,
        navigation: navigation,
        response: response,
        setResponse: setResponse,
        onClick: onClick
    };

    // Select test
    let test;
    switch (config.test) {
        case 'ab':
            test = <AB {...props} />;
            break;
        case 'abx':
            test = <ABX {...props} />;
            break;
        case 'mos':
            test = <MOS {...props} />;
            break;
        case 'mushra':
            test = <MUSHRA {...props} />;
            break;
        default:
            throw new Error(`Test type ${config.test} is not recognized`);
    }

    // Render
    return (
        <div className='section col-all'>
            <Markdown>
                {`**Question ${index + 1} of ${files.length}**\n` +
                 config.survey_instructions}
            </Markdown>
            <br />
            {test}
        </div>
    );
};
