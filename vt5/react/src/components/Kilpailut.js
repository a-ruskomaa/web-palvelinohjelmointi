import React from "react";

const Kilpailut = ( { kaikkiKilpailut, onKilpailuChange, valittuKilpailuId } ) => {

    const options = kaikkiKilpailut.map((kilpailu) => {
        return <option key={`kilpailu-option-${kilpailu.id}`} value={kilpailu.id}>{kilpailu.id}</option>
    })

    return (
        <div id="kilpailu-content">
        <label htmlFor="kilpailu-select">Valitse kilpailu</label>
        <select id="kilpailu-select" onChange={onKilpailuChange} value={valittuKilpailuId}>
            { options }
        </select>
    </div>
    )
};

export default Kilpailut