import ReactMarkdown from 'react-markdown';

import config from '../json/config.json';


/******************************************************************************
Templated markdown
******************************************************************************/


export default function Markdown({ children }) {
    /* Render templated Markdown */

    // TODO - resolve templates

    return <ReactMarkdown>{ children }</ReactMarkdown>
}
