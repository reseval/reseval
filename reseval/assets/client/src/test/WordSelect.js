import React, { useRef, useState } from 'react';

import Media from '../components/Media';
import WordSelection from '../components/WordSelection';

import '../css/components.css';

import Button from '../components/Button';


/******************************************************************************
Word selection test
******************************************************************************/


export default function WordSelect({ file, response, setResponse, onClick }) {
    /* Render a word selection task */
    const ref = useRef();

    // Whether the media has started
    const [started, setStarted] = useState(false);

    // Whether the media has ended
    const [ended, setEnded] = useState(0);

    function clickHandler() {
        // Send response to database and go to next question
        onClick();

        // Reset media files
        setStarted(false);
        setEnded(0);

        // Reset response
        setResponse(undefined);
    }

    // We can advance after at least two listens and one word selected
    const advance = (
        typeof response !== 'undefined' &&
        response.indexOf('1') > -1 &&
        ended >= 2);

    // Render
    return (
        <>
            <div className='grid grid-20-80'>
                <div style={{ width: '100%' }} />
                <Media
                    src={file}
                    reference={ref}
                    onEnded={() => setEnded(ended + 1)}
                    onStarted={() => setStarted(true)}
                />
            </div>
            <WordSelection
                file={file.substr(0, file.lastIndexOf('.')) + '-words.txt'}
                response={response}
                setResponse={setResponse}
                active={started}
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
