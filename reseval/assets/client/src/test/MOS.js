import Chance from 'chance';
import React, { useRef, useState } from 'react';

import Media from '../components/Media';
import RadioButtonGroup from '../components/RadioButtonGroup';

import '../css/components.css';

import Button from '../components/Button';


/******************************************************************************
Constants
******************************************************************************/


// Random number generator
const chance = new Chance();


/******************************************************************************
Mean opinion score evaluation
******************************************************************************/


export default function MOS({
    file,
    conditions,
    response,
    setResponse,
    onClick }) {
    /* Render a MOS evaluation task */
    const reference = useRef();

    // Whether the audio has ended
    const [ended, setEnded] = useState(false);

    function clickHandler() {
        // Send response to database and go to next question
        onClick();

        // Reset audio files
        setEnded(false);
    }

    // Select condition
    const condition = chance.pickone(conditions);

    // Render
    return (
        <>
            <Media
                src={condition + '/' + file}
                reference={reference}
                onEnded={() => setEnded(true)}
            />
            <RadioButtonGroup
                response={
                    typeof response === 'undefined' ? response :
                    Number(response.slice(-1))}
                setResponse={index => setResponse(`${condition}-${index}`)}
                active={ended}
            />
            <Button
                onClick={() => {
                    typeof response !== 'undefined' &&
                        ended &&
                        clickHandler()
                }}
            >
                Next
            </Button>
        </>
    );
};
