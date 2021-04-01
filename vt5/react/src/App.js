import React, { useState, useEffect } from "react";
import "App.css";
import Kilpailut from "components/Kilpailut";
import Button from "components/Button";
import Main from "components/Main";
import { auth } from "services/firebase";
import { signIn, signOut } from "services/authService";
import { useAuthState } from "react-firebase-hooks/auth";
import dataService from "services/dataService";

const App = () => {
    const [user, loading, error] = useAuthState(auth);
    const [kaikkiKilpailut, setKaikkiKilpailut] = useState([]);
    const [valittuKilpailu, setValittuKilpailu] = useState();

    const onKilpailuChange = (event) => {
        const kilpailu = kaikkiKilpailut.find(
            (k) => (k.id === event.target.value)
        );
        setValittuKilpailu(Object.assign({},kilpailu));
    };

    useEffect(() => {
        if (user) {
            console.log("Käyttäjä vaihtui, nollataan kilpailu");
            dataService.haeKaikkiKilpailut().then((data) => {
                setKaikkiKilpailut(data);
                console.log("Haettu kaikki kilpailut", data);
                if (data.length > 0) {
                    console.log("valitaan eka vaihtoehto", data[0]);
                    setValittuKilpailu(data[0]);
                } else {
                    console.log("valitaan tyhjä kisa");
                    setValittuKilpailu();
                }
            });
        }
    }, [user]);

    return user ? (
        <div className="App">
            <Kilpailut
                kaikkiKilpailut={kaikkiKilpailut}
                onKilpailuChange={onKilpailuChange}
                valittuKilpailuId={valittuKilpailu ? valittuKilpailu.id : ""}
            />
            <h1>Tulospalvelu</h1>
            {valittuKilpailu ? (
                <>
                    <h2>{valittuKilpailu.id}</h2>
                    <Button onClickHandler={signOut} text="Kirjaudu ulos" />
                    <Main kilpailuId={valittuKilpailu.id} />
                </>
            ) : (
                <h2>{"Valitse kilpailu!"}</h2>
            )}
        </div>
    ) : (
        <div className="App">
            <h1>Tulospalvelu</h1>
            <Button onClickHandler={signIn} text="Kirjaudu sisään" />
        </div>
    );
};

export default App;
