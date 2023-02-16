import React, {useEffect} from 'react';

import '../css/components.css';

export default function Audio({src, reference, onEnded, onStarted, onPlay}) {
    /* Create an HTML audio element */
    // Reload audio when src changes
    useEffect(() => {
        if (typeof reference !== 'undefined' && reference.current) {
            reference.current.pause();
            reference.current.load();
        }
    }, [reference, src]);

    // Render
    return (
        <audio
            className='audio-single'
            controls
            controlsList='nodownload'
            ref={reference}
            onPlay={() => {
                if (typeof (onStarted) !== 'undefined') onStarted();
                if (typeof (onPlay) !== 'undefined') onPlay();
            }}
            onEnded={() => typeof (onEnded) !== 'undefined' && onEnded()}>
            <source src={src} type='audio/mpeg'/>
        </audio>
    );
}
