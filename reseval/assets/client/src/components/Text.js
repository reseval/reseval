import React, { useEffect, useState } from 'react';

import '../css/components.css';

export default function Text({ src, onEnded }) {
    /* Create a textbox */
    // Call onEnded immediately (and only once) when the file changes
    useEffect(
        () => typeof (onEnded) !== 'undefined' ? onEnded() : undefined,
        [src, onEnded]
    );

    // Get text
    const [text, setText] = useState(undefined);

    // Update text when the file changes
    useEffect(() => {
        fetch(src, { method: 'GET' })
            .then(response => response.text())
            .then(response => setText(response))
    }, [src]);

    // Wait until we have text
    if (typeof text === 'undefined') { return null; }

    // Render
    return (
        <div
            style={{
                color: 'black',
                justifyContent: 'center',
                display: 'flex',
                width: '90%'
            }}
        >
            {text}
        </div>);
}
