export default function ListeningTest({response, setResponse, active}) {
    /* Render a multiple choice question for listening test */
    // enumerated answers
    let answers = ['1', '2', '3', '4', '5', '6', '7', '8', '9', '10']
    return (
        <ul>
            {answers.map((item, key) =>
                <Choice
                    key={key}
                    response={response}
                    setResponse={setResponse}
                    label={item}
                    active={active}
                />
            )}
        </ul>
    )
}

function Choice({response, setResponse, label, active}) {
    return (
        <li className='listitem grid grid-20-80'>
            <div style={{display: 'flex', justifyContent: 'center', width: '100%'}}>
                <div
                    className={`check col-1 ${active ? ' active' : ''}` +
                               `${label === response ? ' selected' : ''}`}
                    onClick={() => active && setResponse(label)}>
                    <div className='inside'/>
                </div>
            </div>
            <div style={{display: 'flex', width: '100%'}}>
                <label
                    className='choices'
                    onClick={() => active && setResponse(label)}
                >
                    {label}
                </label>
            </div>
        </li>
    )
}
