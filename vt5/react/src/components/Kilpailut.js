import React, { useEffect, useState } from "react";

const Kilpailut = ( { kaikkiKilpailut, onKilpailuChange, valittuKilpailuId } ) => {

    const options = kaikkiKilpailut.map((kilpailu) => {
        return <option key={`kilpailu-option-${kilpailu.id}`} value={kilpailu.id}>{kilpailu.id}</option>
    })

    return (
        <div id="kilpailu-content">
        <label>Valitse kilpailu
        <select onChange={onKilpailuChange} value={valittuKilpailuId}>
            { options }
        </select>
        </label>
    </div>
    )
};

export default Kilpailut