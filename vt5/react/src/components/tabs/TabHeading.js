import React from 'react';
import './TabHeading.css';

const TabHeading = ({ tabName }) => {

    return (
        <>
        <input
                className="tab-toggle"
                id={`tab-toggle-${tabName}`}
                type="radio"
                name="tabs"
        />
        <label htmlFor={`tab-toggle-${tabName}`} className="tab-label">{tabName}</label>
        </>
    )
}

export default TabHeading