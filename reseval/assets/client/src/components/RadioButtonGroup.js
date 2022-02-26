import React from 'react';

import '../css/components.css';


/******************************************************************************
Radio buttons
******************************************************************************/


export default function RadioButtonGroup({ response, setResponse, active }) {
	/* Create a group of radio buttons */
	const buttons = [...Array(5).keys()].map(index => {

		// Get radio button state
		let state = active ? 'active' : '';
		if (index === response) {
			state = 'active selected';
		}

		// Render a button
		return (
			<RadioButtonText
				onClick={() => active && setResponse(index)}
				state={state}
				text={index + 1}
			/>
		);
	});

	// Render button group
	return (
		<ul>
			<li className='grid'>
				{buttons}
			</li>
		</ul>
	);
};

function RadioButtonText({ onClick, state, text }) {
	/* Render a radio button with corresponding text */
	return (
		<div style={{margin: 'auto', textAlign: 'center'}}>
			<div className={`check col-1 ${state}`} onClick={onClick}>
				<div className='inside' />
			</div>
			<p>{text}</p>
		</div>
	);
}
