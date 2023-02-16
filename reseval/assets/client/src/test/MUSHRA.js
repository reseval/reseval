import Chance from 'chance';
import React, {createRef, useMemo, useState} from 'react';

import MediaSliderGroup from '../components/MediaSliderGroup';

import '../css/components.css';

import Button from '../components/Button';


/******************************************************************************
 Constants
 ******************************************************************************/


// Random number generator
const chance = new Chance();


/******************************************************************************
 MUSHRA test
 ******************************************************************************/


export default function MUSHRA({file, conditions, setResponse, onClick}) {
    /* Render a MUSHRA evaluation task */
    // Create a ref for each media object
    const refs = useMemo(
        () => conditions.map(() => createRef()), [conditions]);

    // Whether file has ended
    const [endeds, setEndeds] = useState(Array(conditions.length).fill(false));

    // Whether sliders have been touched
    const [toucheds, setToucheds] = useState(
        Array(conditions.length).fill(false));

    // Non-deterministic ordering of media elements
    const [permutation, setPermutation] = useState(
        chance.shuffle([...Array(conditions.length).keys()]));
    const permuted_conditions = permutation.map(index => conditions[index]);

    // Responses corresponding to each slider
    const [scores, setScores] = useState(Array(conditions.length).fill(50));

    function clickHandler() {

        // Send response to database and go to next question
        onClick();

        // Reset media files
        setEndeds(Array(conditions.length).fill(false));

        // Reset Slider if_touched flag
        setToucheds(Array(conditions.length).fill(false));

        // Reset scores
        setScores(Array(conditions.length).fill(50));

        // Get a new permutation
        setPermutation(chance.shuffle([...Array(conditions.length).keys()]));
    }

    // Can we advance?
    const advance =
        endeds.every(item => item === true) &&
        toucheds.some(item => item === true);

    // Render
    return (
        <>
            <MediaSliderGroup
                file={file}
                conditions={permuted_conditions}
                permutation={permutation}
                scores={scores}
                setScores={setScores}
                setResponse={setResponse}
                refs={refs}
                endeds={endeds}
                setEndeds={setEndeds}
                toucheds={toucheds}
                setToucheds={setToucheds}
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
