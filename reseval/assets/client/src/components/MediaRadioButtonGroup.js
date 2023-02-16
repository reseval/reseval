import React from 'react';

import Media from './Media';

import '../css/components.css';


/******************************************************************************
Radio buttons with corresponding media (audio, image, etc.)
******************************************************************************/


function MediaRadioButton({
	file,
	condition,
	response,
	setResponse,
	reference,
	active,
	onEnded }) {
	/* Create a media element with a corresponding radio button */
	// Get radio button state
	let state = active ? 'active' : '';
	if (active && condition === response) {
		state = 'active selected';
	}

	// Render radio button and media
	return (
		<li className='listitem grid grid-20-80'>
            <div
				className={`check col-1 ${state}`}
				onClick={() => active && setResponse(condition)}>
                <div className='inside' />
            </div>
			<Media
				src={condition + '/' + file}
				reference={reference}
				onEnded={onEnded}
			/>
		</li>
	);
}

export default function MediaRadioButtonGroup({
	file,
	conditions,
	response,
	setResponse,
	references,
	active,
	onEndeds }) {
	/* Create a group of media elements with corresponding radio buttons */
	const radioButtonGroup = conditions.map((condition, key) =>
		<MediaRadioButton
			file={file}
			condition={condition}
			key={key}
			response={response}
			setResponse={setResponse}
			reference={references[key]}
			active={active}
			onEnded={onEndeds[key]}
		/>
	);
	return <ul>{radioButtonGroup}</ul>;
}
