import React, { useState, useEffect } from "react";
import "App.css";
import Kilpailut from "components/Kilpailut";
import Button from "components/Button";
import Main from "components/Main";
import { auth } from "services/firebase";
import { signIn, signOut } from "services/authService";
import { useAuthState } from "react-firebase-hooks/auth";
import dataService from "services/dataService";

// Ylin ohjelmakomponentti, jossa hallinnoidaan valitun kilpailun tilaa
// ja renderöidään muu sisältö sen mukaan onko kilpailua valittuna
const App = () => {
    const [user, loading, error] = useAuthState(auth);
    const [kaikkiKilpailut, setKaikkiKilpailut] = useState([]);
    const [valittuKilpailu, setValittuKilpailu] = useState();

    // koppaa kilpailun id:n select-valikon eventistä
    // ja asettaa id:tä vastaavan kilpailun valituksi
    const onKilpailuChange = (event) => {
        const kilpailu = kaikkiKilpailut.find(
            (k) => (k.id === event.target.value)
        );
        setValittuKilpailu(Object.assign({},kilpailu));
    };

    // käyttäjän kirjautuessa sisään haetaan kaikki kilpailut
    // ja asetetaan ensimmäinen oletusarvoisesti valituksi
    useEffect(() => {
        if (user) {
            dataService.haeKaikkiKilpailut().then((data) => {
                console.log("kilpailut",data)
                setKaikkiKilpailut(data);
                if (data.length > 0) {
                    setValittuKilpailu(data[0]);
                } else {
                    setValittuKilpailu();
                }
            }).catch(error => {
                console.log(error)
            });
        }
    }, [user]);

    return user ? (
        // jos käyttäjä on kirjautuneena
        <div className="App">
            <Kilpailut
                kaikkiKilpailut={kaikkiKilpailut}
                onKilpailuChange={onKilpailuChange}
                valittuKilpailuId={valittuKilpailu ? valittuKilpailu.id : ""}
            />
            <h1>Tulospalvelu</h1>
            {valittuKilpailu ? (
                // jos kilpailu on valittuna
                <>
                    <h2>{valittuKilpailu.id}</h2>
                    <Button onClickHandler={signOut} text="Kirjaudu ulos" />
                    <Main valittuKilpailu={valittuKilpailu} />
                </>
            ) : (
                // jos kilpailua ei valittuna
                <h2>{"Valitse kilpailu!"}</h2>
            )}
        </div>
    ) : (
        // jos ei käyttäjää
        <div className="App">
            <h1>Tulospalvelu</h1>
            <Button onClickHandler={signIn} text="Kirjaudu sisään" />
        </div>
    );
};

export default App;
