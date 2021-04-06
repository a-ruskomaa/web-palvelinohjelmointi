import React from "react";

const SarjaInput = ({id, valittuSarja, onSelectHandler, index}) => {

    return (
        <div>
        <label htmlFor={`sarja-input-${id}`}>{id}</label>
        <input
            id={`sarja-input-${id}`}
            type="radio"
            name="sarja"
            value={id}
            required
            checked={id === valittuSarja}
            onChange={onSelectHandler}
            >
        </input>
        </div>
    )
}

export default SarjaInput