import React from 'react';

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
    if (active && response[index]) {
        state = 'active selected';
    }

    function onClick() {
        // Do nothing if media hasn't finished
        if (!active) return;

        // Toggle boolean response vector
        let newResponse = response.slice();
        newResponse[index] = !newResponse[index];
        setResponse(newResponse);
    }

    // Render radio button and media
    // TODO - styling
    return (
        <div className='grid'>
            <div className={`check col-1 ${state}`} onClick={onClick}>
                <div className='inside'/>
            </div>
            {word}
        </div>
    );
};

export default function WordSelection({
    file,
    response,
    setResponse,
    active}) {
    /* Create a group of words with corresponding radio buttons */
    // Get text
    const [text, setText] = useState(undefined);

    // Update text when the file changes
    useEffect(() => {
        fetch(file)
            .then(response => response.text())
            .then(response => setText(response))
    }, [file]);

    // Wait until we have text
    if (typeof text === 'undefined') { return null; }

    // Split text into words
    words = text.split(/\s+/);

    // Give each word a radio button
    const radioButtonGroup = words.map((word, key) =>
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
    return <>radioButtonGroup</>;
};
