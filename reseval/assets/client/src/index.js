import React from 'react';
import ReactDOM from 'react-dom';
import { BrowserView, MobileView } from 'react-device-detect';
import App from './App';
import 'bootstrap/dist/css/bootstrap.min.css';

import './css/index.css';

ReactDOM.render(
    <React.StrictMode>
        <BrowserView>
            <App />
        </BrowserView>
        <MobileView>
            <h1>
                This app does not display properly on mobile devices.
                Please switch to a computer browser.
            </h1>
        </MobileView>
    </React.StrictMode>,
    document.getElementById('root')
);
