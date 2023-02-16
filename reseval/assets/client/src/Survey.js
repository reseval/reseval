import Chance from 'chance';
import React, {useState} from 'react';
import {useStep} from 'react-hooks-helper';

import './css/components.css';

import EndPage from './pages/EndPage';
import FeedbackPage from './pages/FeedbackPage';
import QualificationPage from './pages/QualificationPage';
import TaskPage from './pages/TaskPage';
import WelcomePage from './pages/WelcomePage';


/******************************************************************************
 Constants
 ******************************************************************************/


// Random number generator
const chance = new Chance();

// Completion code for participant
const completionCode = chance.string({length: 10});

// Chronological ordering of pages visited by participants during evaluation
const steps = [
    {id: 'welcome'},
    {id: 'prescreen'},
    {id: 'task'},
    {id: 'feedback'},
    {id: 'end'}];


/******************************************************************************
 Subjective evaluation survey
 ******************************************************************************/


export default function Survey() {
    /* Page navigation management for surveys */
    // Start at the welcome page
    const {step, navigation} = useStep({initialStep: 0, steps});

    // Participant id
    const [participant, setParticipant] = useState(undefined);

    // Evaluation conditions
    const [conditions, setConditions] = useState(undefined);

    // Evaluation files
    const [files, setFiles] = useState(undefined);
    // Evaluator Id; this is an incremental integer id starts from 0
    const [evaluatorId, setEvaluatorId] = useState(undefined);
    // Render current page
    switch (step.id) {
        case 'welcome':
            return <WelcomePage navigation={navigation}/>;
        case 'prescreen':
            return <QualificationPage
                participant={participant}
                setParticipant={setParticipant}
                completionCode={completionCode}
                setFiles={setFiles}
                setConditions={setConditions}
                setEvaluatorId={setEvaluatorId}
                navigation={navigation}
            />;
        case 'task':
            return <TaskPage
                files={files}
                conditions={conditions}
                participant={participant}
                navigation={navigation}
                evaluatorId={evaluatorId}
            />;
        case 'feedback':
            return <FeedbackPage
                navigation={navigation}
                participant={participant}
            />;
        case 'end':
            return <EndPage completionCode={completionCode}/>;
        default:
            return
    }
}
