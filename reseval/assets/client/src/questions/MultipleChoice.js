export default function MultipleChoice({ response, setResponse, answers }) {
    /* Render a multiple choice question */
    return (
        <ul className='MultipleChoice'>
            {answers.map((item, key) =>
                <Choice
                    key={key}
                    index={key}
                    response={response}
                    setResponse={setResponse}
                    label={item} />
            )}
        </ul>
    )
}

function Choice({ index, response, setResponse, label }) {
    /* Render one choice of a multiple choice question */
    return (
        <li className='grid'>
            <div
                className={`check active col-1 ${label === response ? 'selected' : ''}`}
                onClick={() => setResponse(label)}>
                <div className='inside' />
            </div>
            <label
                htmlFor=''
                className='col-3'
                onClick={() => setResponse(label)}>
                {label}
            </label>
        </li>
    )
}
