import React, {useContext} from 'react';

import Audio from './Audio';
import Image from './Image';
import Text from './Text';
import Video from './Video';

import config from '../json/config.json';
import {MediaContext} from "../pages/TaskPage";


/******************************************************************************
 Render media objects (audio, image, etc.)
 ******************************************************************************/


export default function Media(props) {
    /* Render a media object (audio, image, etc.) */
    // Retrieve the global state, which contains any currently playing media
    let {mediaRef, setMediaRef} = useContext(MediaContext);

    function onPlayed() {
        if (mediaRef !== props.reference) {

            // Do nothing if it is the same media that is being played
            if (mediaRef !== undefined) {

                // Pause old media to prevent both playing simultaneously
                mediaRef.current.pause()

                // Set the play head to the beginning
                mediaRef.current.currentTime = 0
            }

            // Replace the media in the context
            setMediaRef(props.reference)
        }
    }

    props.onPlayed = onPlayed

    // Get file URL
    if (config['local']) {
        props.src = '/evaluation-files/' + props.src;
    } else {
        switch (config.storage) {
            case 'aws':
                props.src = `https://${config['bucket']}.s3.amazonaws.com/${props.src}`;
                break;
            default:
                throw new Error(
                    `Storage location ${config.storage} is not recognized`);
        }
    }

    let media;
    switch (config.datatype) {
        case 'audio':
            media = <Audio {...props} />;
            break;
        case 'image':
            media = <Image {...props} />;
            break;
        case 'text':
            media = <Text {...props} />;
            break;
        case 'video':
            media = <Video {...props} />;
            break;
        default:
            throw new Error(`Datatype ${config.datatype} is not recognized`);
    }

    return (
        <div
            style={{
                display: 'flex',
                justifyContent: 'center',
                padding: '10px'
            }}
        >
            {media}
        </div>);
}
