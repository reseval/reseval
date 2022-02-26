import React from 'react';

export default function Button({ onClick, children }) {
    /* Render the button used to continue to the next page */
    return (
        <div>
            <button className='button' onClick={onClick}>
                {children}
            </button>
        </div>
    );
}
