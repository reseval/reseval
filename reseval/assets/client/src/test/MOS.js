import React, {useRef, useState} from 'react';

import Media from '../components/Media';
import RadioButtonGroup from '../components/RadioButtonGroup';
import conditions from '../json/conditions.json';

import '../css/components.css';

import Button from '../components/Button';


/******************************************************************************
 Mean opinion score evaluation
 ******************************************************************************/


export default function MOS({
    file,
    index,
    response,
    setResponse,
    evaluatorId,
    onClick
}) {
    /* Render a MOS evaluation task */
    const reference = useRef();

    // Conditions to use for this evaluator
    const conditionList = conditions[evaluatorId % conditions.length]

    // Condition of the current file
    const [condition, setCondition] = useState(conditionList[index]);

    // Whether the media has ended
    const [ended, setEnded] = useState(false);

    function clickHandler() {
        // Send response to database and go to next question
        onClick();

        // Reset media files
        setEnded(false);

        // Update condition
        setCondition(conditionList[index + 1])
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
                onClick={() => { advance && clickHandler() }}
            >
                Next
            </Button>
        </>
    );
}
