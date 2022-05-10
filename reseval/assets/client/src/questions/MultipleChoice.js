export default function MultipleChoice({ response, setResponse, answers }) {
    /* Render a multiple choice question */
    return (
        <ul>
            {answers.map((item, key) =>
                <Choice
                    key={key}
                    response={response}
                    setResponse={setResponse}
                    label={item} />
            )}
        </ul>
    )
}

function Choice({ response, setResponse, label }) {
    /* Render one choice of a multiple choice question */
    return (
        <li className='listitem grid grid-20-80'>
            <div style={{display: 'flex', justifyContent: 'center', width: '100%'}}>
                <div
                    className={`check active col-1 ${label === response ? 'selected' : ''}`}
                    onClick={() => setResponse(label)}>
                    <div className='inside' />
                </div>
            </div>
            <div style={{display: 'flex', width: '100%' }}>
                <label
                    className='choices'
                    onClick={() => setResponse(label)}
                >
                    {label}
                </label>
            </div>
        </li>
    )
}
