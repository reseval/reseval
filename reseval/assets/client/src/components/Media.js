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
    // TODO - evaluation file URL is being used even when using S3
    if (config['local']) {
        console.log('Is local');
        props.src = '/evaluation-files/' + props.src;
    } else {
        console.log('Is not local');
        switch (config.storage) {
            case 'aws':
                console.log('Is aws');
                props.src = `https://${config['bucket']}.s3.amazonaws.com/${props.src}`;
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
