import React from 'react';
import { auth } from 'services/firebase'
import { useAuthState } from 'react-firebase-hooks/auth';
import './Joukkue.css'

const Joukkue = ({ joukkue, handleJoukkueSelect }) => {
    const [user, loading, error] = useAuthState(auth);

    const jasenElems = joukkue.jasenet.map((jasen) => {
        return <li key={`jasen-${joukkue.id}-${jasen}`}>{jasen}</li>
    })

    const label = user.email === joukkue.lisaaja ?
                <span className="joukkue-nimi" onClick={() => handleJoukkueSelect(joukkue.id)}>{joukkue.nimi}</span> :
                joukkue.nimi

    return (
        <li>
            { label }
            <ul>
            { jasenElems }
            </ul>
        </li>
    )
}

export default Joukkue