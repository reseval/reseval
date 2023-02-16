import React, {useEffect} from 'react';

import '../css/components.css';

export default function Video({src, reference, onEnded, onStarted, onPlay}) {
    /* Create an HTML video element */
    // Reload video when src changes
    useEffect(() => {
        if (reference.current) {
            reference.current.pause();
            reference.current.load();
        }
    }, [reference, src]);

    // Render
    return (
        <video
            controls
            ref={reference}
            style={{minWidth: '150px', maxWidth: '750px'}}
            onPlay={() => {
                if (typeof (onStarted) !== 'undefined') onStarted();
                if (typeof (onPlay) !== 'undefined') onPlay();
            }}
            onEnded={() => typeof (onEnded) !== 'undefined' && onEnded()}
        >
            <source src={src} type='video/mp4'/>
        </video>
    );
}
