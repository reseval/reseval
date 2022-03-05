import React from 'react';

import '../css/components.css';

export default function Image({ src }) {
    return <img
        alt={'Subjective evaluation media'}
        src={src}
        style={{ minWidth: '150px', maxWidth: '750px' }}
    />;
};
