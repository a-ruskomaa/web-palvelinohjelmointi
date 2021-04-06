import React from 'react';

const LeimausInput = ({
                        aika,
                        rasti,
                        index,
                        // poista,
                        rastit: kilpailunRastit,
                        onAikaInputChange,
                        onAikaInputBlur,
                        onRastiSelectChange,
                        onPoistaInputChange }) => {

    const optionElems = kilpailunRastit.map((rasti) => {
        return <option key={`leimaus-${index}-option-${rasti.id}`} value={rasti.id}>{rasti.koodi}</option>
    })

    return (
        <div>
            <label htmlFor={`leimausform-aika-${index}`}>Aika</label>
            <input
                type="text"
                name="aika"
                value={aika}
                id={`leimausform-aika-${index}`}
                placeholder="yyyy-mm-dd hh:mm:ss"
                onChange={(e) => onAikaInputChange(e,index)}
                onBlur={(e) => onAikaInputBlur(e, index)}/>
            <label htmlFor={`leimausform-rasti-${index}`}>Rasti</label>
            <select
                id={`leimausform-rasti-${index}`}
                name="rasti"
                value={rasti}
                onChange={(e) => onRastiSelectChange(e,index)}>
                    { optionElems }
            </select>
            <label htmlFor={`leimausform-poista-${index}`}>Poista?</label>
            <input
                type="checkbox"
                id={`leimausform-poista-${index}`}
                name="poista"
                value="poista"
                // checked={poista}
                onChange={(e) => onPoistaInputChange(e,index)}
            />
        </div>
    )
}

export default LeimausInput