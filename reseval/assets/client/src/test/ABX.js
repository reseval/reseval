import Chance from 'chance';
import React, { useRef, useState } from 'react';

import Media from '../components/Media';
import MediaRadioButtonGroup from '../components/MediaRadioButtonGroup';

import '../css/components.css';

import Button from '../components/Button';


/******************************************************************************
Constants
******************************************************************************/


// Random number generator
const chance = new Chance();


/******************************************************************************
ABX test
******************************************************************************/


export default function ABX({
    file,
    conditions,
    response,
    setResponse,
    onClick }) {
    /* Render an ABX evaluation task */
    const refX = useRef();
    const refA = useRef();
    const refB = useRef();

    // Whether the media has ended
    const [XEnded, setXEnded] = useState(false);
    const [AEnded, setAEnded] = useState(false);
    const [BEnded, setBEnded] = useState(false);

    // Non-deterministic ordering of media elements
    const conditions_no_reference = conditions.filter(
        condition => condition !== 'reference')
    const [permutation, setPermutation] = useState(
        chance.shuffle([...Array(conditions_no_reference.length).keys()]));
    const permuted_conditions = permutation.map(
        index => conditions_no_reference[index]);

    function clickHandler() {
        // Send response to database and go to next question
        onClick();

        // Reset media files
        setXEnded(false);
        setAEnded(false);
        setBEnded(false);

        // Get a new permutation
        setPermutation(
            chance.shuffle([...Array(conditions_no_reference.length).keys()]));
    }

    // Can we advance?
    const advance =
        typeof response !== 'undefined' && XEnded && AEnded && BEnded;

    // Render
    return (
        <>
            <div className='grid grid-20-80'>
                <div style={{width: '100%'}}/>
                <Media
                    src={'reference/' + file}
                    reference={refX}
                    onEnded={() => setXEnded(true)}
                />
            </div>
            <MediaRadioButtonGroup
                file={file}
                conditions={permuted_conditions}
                response={response}
                setResponse={setResponse}
                references={[refA, refB]}
                active={XEnded && AEnded && BEnded}
                onEndeds={[() => setAEnded(true), () => setBEnded(true)]}
            />
            <Button
                active={advance}
                onClick={() => {advance && clickHandler()}}
            >
                Next
            </Button>
        </>
    );
}
