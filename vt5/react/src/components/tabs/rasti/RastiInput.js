import React from 'react';

const RastiInput = ({
    index,
    koodi,
    lat,
    lon,
    domRef,
    onKoodiInputChange,
    onKoodiInputBlur,
    onLatInputChange,
    onLonInputChange,
    onPoistaInputChange }) => {

    return (
        <div>
            <label htmlFor={`rastiform-koodi-${index}`}>Koodi</label>
            <input
                type="text"
                name="koodi"
                value={koodi}
                id={`rastiform-koodi-${index}`}
                onChange={(e) => onKoodiInputChange(e, index)}
                onBlur={(e) => onKoodiInputBlur(e, index)} />

            <label htmlFor={`rastiform-lat-${index}`}>Lat</label>
            <input
                type="text"
                name="lat"
                placeholder="62.241677684"
                value={lat}
                ref={domRef[0]}
                id={`rastiform-lat-${index}`}
                onChange={(e) => onLatInputChange(e, index)} />

            <label htmlFor={`rastiform-lon-${index}`}>Lon</label>
            <input
                type="text"
                name="lon"
                placeholder="25.749498121"
                value={lon}
                ref={domRef[1]}
                id={`rastiform-lon-${index}`}
                onChange={(e) => onLonInputChange(e, index)} />

            <label htmlFor={`rastiform-poista-${index}`}>Poista?</label>
            <input
                type="checkbox"
                id={`rastiform-poista-${index}`}
                name="poista"
                value="poista"
                // checked={poista}
                onChange={(e) => onPoistaInputChange(e, index)}
            />
        </div>
    )
}


export default RastiInput