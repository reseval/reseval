import Chance from 'chance';
import React, { useRef, useState } from 'react';

import MediaRadioButtonGroup from '../components/MediaRadioButtonGroup';

import '../css/components.css';

import Button from '../components/Button';


/******************************************************************************
Constants
******************************************************************************/


// Random number generator
const chance = new Chance();


/******************************************************************************
AB test
******************************************************************************/


export default function AB({
    file,
    conditions,
    response,
    setResponse,
    onClick }) {
    /* Render an AB evaluation task */
    const refA = useRef();
    const refB = useRef();

    // Whether file has ended
    const [AEnded, setAEnded] = useState(false);
    const [BEnded, setBEnded] = useState(false);

    // Non-deterministic ordering of media elements
    const [permutation, setPermutation] = useState(
        chance.shuffle([...Array(conditions.length).keys()]));
    const permuted_conditions = permutation.map(index => conditions[index]);

    function clickHandler() {
        // Send response and update index
        onClick();

        // Reset media components
        setAEnded(false);
        setBEnded(false);

        // Get a new permutation
        setPermutation(chance.shuffle([...Array(conditions.length).keys()]));
    }

    // Can we advance?
    const advance = typeof response !== 'undefined' && AEnded && BEnded;

    // Render
    return (
        <>
            <MediaRadioButtonGroup
                file={file}
                conditions={permuted_conditions}
                response={response}
                setResponse={setResponse}
                references={[refA, refB]}
                active={AEnded && BEnded}
                onEndeds={[() => setAEnded(true), () => setBEnded(true)]}
            />
            <Button
                active={advance}
                onClick={() => advance && clickHandler()}
            >
                Next
            </Button>
        </>
    );
}
