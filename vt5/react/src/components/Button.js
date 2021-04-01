import React from "react";

const Button = ({ onClickHandler, text }) => {

    return (
        <div>
            <button onClick={onClickHandler}>{text}</button>
        </div>
    )
};

export default Button