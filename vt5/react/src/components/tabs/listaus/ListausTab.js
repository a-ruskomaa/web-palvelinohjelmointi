import React from 'react';
import Sarja from './Sarja';

const ListausTab = ({sarjat, handleJoukkueSelect }) => {
    
    const sarjaElems = sarjat.length > 0 ? sarjat.map((sarja) => {
        return <Sarja key={`sarja-${sarja.id}`} sarja={sarja} handleJoukkueSelect={handleJoukkueSelect}/>
    }) : []

    return (
        <div className="tab-content">
            <ul>
                { sarjaElems.length > 0 ? sarjaElems : "Kilpailussa ei ole sarjoja" }
            </ul>
        </div>
    )
}

export default ListausTab