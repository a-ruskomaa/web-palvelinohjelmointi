import React from "react";

const Button = ({ className, onClickHandler, text }) => {

    return (
        <div>
            <button className={className}  onClick={onClickHandler}>{text}</button>
        </div>
    )
};

export default Button