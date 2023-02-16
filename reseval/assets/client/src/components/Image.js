import React, { useEffect } from 'react';

import '../css/components.css';

export default function Image({ src, onEnded }) {
    /* Render an image */
    // Call onEnded when the file changes
    useEffect(
        () => typeof (onEnded) !== 'undefined' && onEnded(),
        [src, onEnded]
    );

    // Render
    return <img
        alt={'Subjective evaluation media'}
        src={src}
        style={{ minWidth: '150px', maxWidth: '750px' }}
    />;
}
