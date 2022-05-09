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

    // Whether the media has ended
    const [ended, setEnded] = useState(false);

    // Select random condition
    // TODO - balanced selection over both files and conditions
    const [condition, setCondition] = useState(chance.pickone(conditions));

    function clickHandler() {
        // Send response to database and go to next question
        onClick();

        // Reset media files
        setEnded(false);

        // Draw a new random condition
        setCondition(chance.pickone(conditions));
    }

    // Can we advance?
    const advance = typeof response !== 'undefined' && ended;

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
                active={advance}
                onClick={() => {advance && clickHandler()}}
            >
                Next
            </Button>
        </>
    );
};
