import React, { useEffect, useState } from 'react';

import config from '../json/config.json';

import '../css/components.css';


/******************************************************************************
Word selection interface
******************************************************************************/


function WordRadioButton({
    word,
    index,
    response,
    setResponse,
    active}) {
    /* Create a word with a corresponding radio button */
    // Get radio button state
    let state = active ? 'active' : '';
    if (active && typeof response !== 'undefined' && response[index] === '1') {
        state = 'active selected';
    }

    function onClick() {
        // Do nothing if media hasn't finished
        if (!active) return;

        // Toggle response array
        setResponse(
            response.slice(0, index) +
            (response[index] === '0' ? '1' : '0') +
            response.slice(index + 1));
    }

    // Render radio button and media
    return (
        <div className='word'>
            <div
                className={`check col-1 ${state}`}
                style={{margin: 'auto'}}
                onClick={onClick}
            />
            <div>{word}</div>
        </div>
    );
};

export default function WordSelection({
    file,
    response,
    setResponse,
    active}) {
    /* Create a group of words with corresponding radio buttons */
    // Update filename
    if (config['local']) {
        file = '/evaluation-files/' + file;
    } else {
        switch (config.storage) {
            case 'aws':
                file = `https://${config['bucket']}.s3.amazonaws.com/${file}`;
                break;
            default:
                throw new Error(
                    `Storage location ${config.storage} is not recognized`);
        }
    }

    // Get text
    const [text, setText] = useState(undefined);

    // Update text and reset response when the file changes
    useEffect(() => {
        fetch(file)
        .then(response => response.text())
        .then(response => {
            const words = response.split(/\s+/);
            setText(words);
            setResponse('0'.repeat(words.length));
        })
    }, [file]);

    // Wait until we have text
    if (typeof text === 'undefined') { return null; }

    // Give each word a radio button
    const radioButtonGroup = text.map((word, key) =>
        <WordRadioButton
            word={word}
            key={key}
            index={key}
            response={response}
            setResponse={setResponse}
            active={active}
        />
    );

    // Render
    return <div className='wordselect'>{radioButtonGroup}</div>;
};
