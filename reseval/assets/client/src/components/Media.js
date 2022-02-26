import React from 'react';

import Audio from './Audio';
import Image from './Image';
import Text from './Text';
import Video from './Video';

import config from '../json/config.json';


/******************************************************************************
Render media objects (audio, image, etc.)
******************************************************************************/


export default function Media(props) {
    /* Render a media object (audio, image, etc.) */
    // Get file URL
    if (config['local']) {
        props.src = '/evaluation-files/' + props.src;
    } else {
        switch (config.storage) {
            case 'aws':
                props.src = 's3://' + props.src;
                break;
            default:
                throw new Error(
                    `Storage location ${config.storage} is not recognized`);
        }
    }

    switch (config.datatype) {
        case 'audio':
            return <Audio {...props} />;
        case 'image':
            props.onEnded();
            delete props.onEnded;
            return <Image {...props} />;
        case 'text':
            props.onEnded();
            delete props.onEnded;
            return <Text {...props} />;
        case 'video':
            return <Video {...props} />;
        default:
            throw new Error(`Datatype ${config.datatype} is not recognized`);
    }
}
