import React from 'react';

export default function Button({ active, onClick, children }) {
    /* Render the button used to continue to the next page */
    return (
        <div>
            <button
                className={'button' + (active ? ' active': '')}
                onClick={onClick}
            >
                {children}
            </button>
        </div>
    );
}
