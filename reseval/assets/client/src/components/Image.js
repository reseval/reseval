import React from 'react';

import '../css/components.css';

export default function Image({ src, ref }) {
    return <img alt={'Subjective evaluation media'} ref={ref} src={src} />;
};
