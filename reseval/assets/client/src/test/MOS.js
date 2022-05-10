import React, { useRef, useState } from 'react';

import Media from '../components/Media';
import RadioButtonGroup from '../components/RadioButtonGroup';

import '../css/components.css';

import Button from '../components/Button';


/******************************************************************************
Constants
******************************************************************************/



/******************************************************************************
Mean opinion score evaluation
******************************************************************************/


export default function MOS({
    file,
    index,
    response,
    setResponse,
    mosCondition,
    onClick }) {
    /* Render a MOS evaluation task */
    const reference = useRef();

    // Whether the media has ended
    const [ended, setEnded] = useState(false);
    // get conditions
    const [condition, setCondition] = useState(mosCondition[index]);

    function clickHandler() {
        // Send response to database and go to next question
        onClick();

        // Reset media files
        setEnded(false);

        // go to the next condition
        setCondition(mosCondition[index+1])
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
