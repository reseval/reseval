import React from 'react';

import Button from '../components/Button';
import Markdown from '../components/markdown';

import '../css/components.css';

import config from '../json/config.json'

export default function WelcomePage({ navigation }) {
	/* Renders the first page that participants visit */
	return (
		<div className='container'>
			<Markdown>{config.welcome_text}</Markdown>
			<Button onClick={navigation.next}>I Agree</Button>
		</div>
	);
}
