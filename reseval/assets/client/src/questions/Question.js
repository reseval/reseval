import FreeResponse from './FreeResponse';
import MultipleChoice from './MultipleChoice';

export default function Question({question, response, setResponse}) {
    /* Render a question */
    // Maybe render multiple choice
    if (question.type === 'multiple-choice') {
        return <MultipleChoice
            response={response}
            setResponse={setResponse}
            answers={question.answers}
        />;
    }

    // Maybe render free response
    if (question.type === 'free-response') {
        return <FreeResponse
            placeholder={question.placeholder}
            setResponse={setResponse}
        />;
    }

    // Unrecognized question type
    throw new Error(`Question type ${question.type} is not recognized`);
}


export function validate(response) {
    /* Error check question response */
    // Require input to be non-empty
    if (typeof response === 'undefined' || !response.trim()) {
        alert('Please leave a response.');
        return false;
    }
    return true;
}
