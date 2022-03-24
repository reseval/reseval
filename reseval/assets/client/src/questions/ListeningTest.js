export default function ListeningTest({response,setResponse}) {
    /* Render a multiple choice question */
    let answers = ['1','2','3','4','5','6']
    return (
        <ul className='MultipleChoice'>
            {answers.map((item, key) =>
                <Choice
                    key={key}
                    response={response}
                    setResponse={setResponse}
                    label={item}/>
            )}
        </ul>
    )
}

function ParseAnswer({file}) {

}

function Choice({response, setResponse, label}) {
    /* Render one choice of a multiple choice question */
    return (
        <li className='grid grid-20-80'>
            <div style={{display: 'flex', justifyContent: 'center', width: '100%'}}>
                <div
                    className={`check active col-1 ${label === response ? 'selected' : ''}`}
                    onClick={() => setResponse(label)}>
                    <div className='inside'/>
                </div>
            </div>
            <div style={{display: 'flex', width: '100%'}}>
                <label onClick={() => setResponse(label)}>{label}</label>
            </div>
        </li>
    )
}
