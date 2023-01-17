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

    // Whether the media has ended
    const [ended, setEnded] = useState(false);

    function clickHandler() {
        // Send response to database and go to next question
        onClick();

        // Reset media files
        setEnded(false);

        // Reset response
        setResponse(undefined);
    }

    // Can we advance?
    const advance = typeof response !== 'undefined' && ended;

    // Render
    return (
        <>
            <div className='grid grid-20-80'>
                <div style={{ width: '100%' }} />
                <Media
                    src={file}
                    reference={ref}
                    onEnded={() => setEnded(true)}
                />
            </div>
            <WordSelection
                file={file.substr(0, file.lastIndexOf('.')) + '-words.txt'}
                response={response}
                setResponse={setResponse}
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
};
