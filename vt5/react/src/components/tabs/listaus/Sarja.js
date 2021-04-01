import React from 'react';
import Joukkue from './Joukkue';

const Sarja = ({ sarja, handleJoukkueSelect }) => {
    const joukkueElems = sarja.joukkueet.map((joukkue) => {
        return <Joukkue key={`joukkue-${joukkue.id}`} joukkue={joukkue} handleJoukkueSelect={handleJoukkueSelect}/>
    })

    return (
            <li>{ sarja.id }
                <ul>
                { joukkueElems }
                </ul>
            </li>
    )
}

export default Sarja