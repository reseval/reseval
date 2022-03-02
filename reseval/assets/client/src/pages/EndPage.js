import Markdown from '../components/Markdown';

import config from '../json/config.json';

export default function EndPage({ completionCode }) {
    /* Display the final page with a completion code for the participant */
    // Format platform string
    let platform_string;
    const platform = config.crowdsource.platform;
    if (platform === 'mturk') {
        platform_string = 'Amazon Mechanical Turk'
    } else {
        throw new Error(`Platform ${platform} is not recognized`);
    }
    const message =
        `Thank you for your participation. Please copy and paste the ` +
        `following code into ${platform_string}.`

    // Render
    return (
        <div className='container'>
            <Markdown>{message}</Markdown>
            <h1>{completionCode}</h1>
        </div>
    );
}
