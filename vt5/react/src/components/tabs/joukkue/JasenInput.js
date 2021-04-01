import React from "react";

const JasenInput = ({ value, index, onChangeHandler, domRef }) => {
    return (
        <div>
            <label htmlFor={`jasen-${index}`}>Jäsen {index + 1}</label>
            <input
                id={`jasen-${index}`}
                name="jasen"
                type="text"
                value={value}
                ref={domRef}
                onChange={(e) => {
                    onChangeHandler(index, e);
                }}
            />
        </div>
    );
};

export default JasenInput;
