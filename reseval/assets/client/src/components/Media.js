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

    function onPlay() {
        if (mediaRef !== props.reference) {

            // Do nothing if it is the same media that is being played
            if (mediaRef !== undefined && mediaRef.current !== undefined) {

                // Pause old media to prevent both playing simultaneously
                mediaRef.current.pause()

                // Set the play head to the beginning
                mediaRef.current.currentTime = 0
            }

            // Replace the media in the context
            setMediaRef(props.reference)
        }
    }

    // Add callback prop
    const newProps = {...props};
    newProps.onPlay = onPlay;

    // Update file source prop
    if (config['local']) {
        newProps.src = '/evaluation-files/' + newProps.src;
    } else {
        switch (config.storage) {
            case 'aws':
                newProps.src = `https://${config['bucket']}.s3.amazonaws.com/${newProps.src}`;
                break;
            default:
                throw new Error(
                    `Storage location ${config.storage} is not recognized`);
        }
    }

    // Lock props
    Object.preventExtensions(newProps);

    // Get datatype
    let media;
    switch (config.datatype) {
        case 'audio':
            media = <Audio {...newProps} />;
            break;
        case 'image':
            media = <Image {...newProps} />;
            break;
        case 'text':
            media = <Text {...newProps} />;
            break;
        case 'video':
            media = <Video {...newProps} />;
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
        </div>
    );
}
