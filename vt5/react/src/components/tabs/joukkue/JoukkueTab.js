import React, { useEffect, useState, useRef } from "react";
import SarjaInput from "./SarjaInput";
import "./JoukkueTab.css";
import JasenInput from "./JasenInput";
import dataService from "services/dataService";
import { auth } from "services/firebase";
import { useAuthState } from "react-firebase-hooks/auth";

const JoukkueTab = ({ sarjat, kilpailuId, valittuJoukkue, dataUpdated }) => {
    const [user, loading, error] = useAuthState(auth);
    const [id, setId] = useState();
    const [nimi, setNimi] = useState("");
    const [sarja, setSarja] = useState();
    const [jasenet, setJasenet] = useState(Array(5).fill(""));
    const [poista, setPoista] = useState(false);
    const [statusMsg, setStatusMsg] = useState();

    // refit jäsenten input-kenttien dom-elementteihin 
    const jasenInputRefs = [
        useRef(null),
        useRef(null),
        useRef(null),
        useRef(null),
        useRef(null),
    ];

    // jos kilpailu vaihtuu tai joukkue valitaan
    useEffect(() => {
        // jos joukkue valitaan, täytetään lomake valitun joukkueen tiedoilla
        if (valittuJoukkue) {
            setId(valittuJoukkue.id);
            setNimi(valittuJoukkue.nimi);
            setSarja(valittuJoukkue.sarja);
            setJasenet(
                valittuJoukkue.jasenet.concat(
                    Array(5 - valittuJoukkue.jasenet.length).fill("")
                )
            );
        } else {
            // jos joukkuetta ei ole valittuna, etsitään käyttäjän joukkueita muista kilpailuista 
            dataService
                .haeJoukkueetRajauksilla([
                    ["lisaaja", "==", user.email],
                    ["kilpailu", "!=", kilpailuId],
                ])
                .then((muutJoukkueet) => {
                    if (muutJoukkueet.length > 0) {
                        const malliJoukkue = muutJoukkueet[0];
                        setId();
                        setNimi(malliJoukkue.nimi);
                        setSarja(sarjat[0].id);
                        setJasenet(
                            malliJoukkue.jasenet.concat(
                                Array(5 - malliJoukkue.jasenet.length).fill("")
                            )
                        );
                    }
                }).catch((error) => {
                    console.log(error)
                });
            // valitaan oletuksena ensimmäinen sarja jos lomaketta ei täytetä
            if (sarja === undefined && sarjat.length > 0) {
                setSarja(sarjat[0].id)
            }
        }
        // palautetaan funktio joka nollaa lomakkeen tilan kun komponentti unmountataan, turha?
        // return () => {
        //     resetForm();
        //     console.log("Lomake nollattu");
        // };
    }, [kilpailuId, valittuJoukkue, user.email]);

    // nolla lomakkeen
    const resetForm = () => {
        setId();
        setNimi("");
        setSarja();
        setJasenet(Array(5).fill(""));
        setPoista(false)
        setStatusMsg();
    };

    // käsittelee nimikentän input-tapahtuman
    const onNimiInputChange = (event) => {
        const nimiInput = event.target;
        nimiInput.setCustomValidity("");

        // ei sallita tyhjiä nimiä
        if (nimiInput.value.trim() === "") {
            nimiInput.setCustomValidity("Joukkueen nimi ei voi ola tyhjä!");
        }

        setNimi(nimiInput.value);
    };

    // käsittelee nimikentän blur-tapahtuman
    const onNimiInputBlur = (event) => {
        const nimiInput = event.target;

        // jos nimi on muuten validi, tarkistetaan ettei ole samannimisiä
        if (nimiInput.validity.valid) {
            sarjat.forEach((sarja) => {
                const samanNimisia = sarja.joukkueet
                    .some(j => j.nimi.toLowerCase() ===
                        nimiInput.value.trim().toLowerCase() &&
                        j.id !== id);
                if (samanNimisia) {
                    nimiInput.setCustomValidity(
                        "Kilpailussa on jo samanniminen joukkue!"
                    );
                }
            });
        }
    };

    // käsittelee jäsenkentän input-tapahtuman
    const onJasenInputChange = (i, event) => {
        const jasenInput = event.target;

        jasenInput.setCustomValidity("");

        // ei sallita numeroita
        if (jasenInput.value.match(/\d/)) {
            jasenInput.setCustomValidity(
                "Jäsenen nimessä ei saa olla numeroita"
            );
            // ...eikä pelkästä whitespacesta koostuvia nimiä. ei huomioida tyhjiä kenttiä. 
        } else if (jasenInput.value !== "" && jasenInput.value.trim() === "") {
            jasenInput.setCustomValidity("Jäsenen nimi ei voi olla tyhjä");
        }

        let updatedJasenet = [...jasenet];
        updatedJasenet[i] = jasenInput.value;
        setJasenet(updatedJasenet);
    };

    // käsittelee sarjan input-tapahtuman
    const onSarjaInputChange = (event) => {
        setSarja(event.target.value);
    };

    // käsittelee poistokentän input-tapahtuman
    const onPoistaInputChange = (event) => {
        setPoista(event.target.checked);
    };

    // validoi jäsenet
    const validateJasenet = (jasenet) => {
        // haetaan refit dom-elementteihin
        const jasenInputs = jasenInputRefs.map((ref) => ref.current);
        // jos jäseniä on ei-sallittu määrä
        if (jasenet.length < 2 || jasenet.length > 5) {
            // etsitään ensimmäinen tyhjä input ja invalidoidaan se
            const ekaTyhja = jasenInputs.find(jasenInput => jasenInput.value.trim() === "");
            ekaTyhja.setCustomValidity("Anna 2-5 jäsentä!");
        } else {
            // nollataan mahdolliset aiemmat invalidoinnit
            jasenInputs.forEach((j) => {
                if (j.validationMessage === "Anna 2-5 jäsentä!") {
                    j.setCustomValidity("");
                }
            });
        }
    };

    // käsittelee lomakken lähetyksen
    const onSubmitForm = (event) => {
        event.preventDefault();
        setStatusMsg();
        // jos ollaan poistamassa, varmistetaan vielä
        if (poista &&
            window.confirm(`Haluatko varmasti poistaa joukkueen ${nimi}?`)) {
            // poistetaan joukkue ja tyhjennetään lomake
            dataService
                .poistaJoukkue(id)
                .then(() => {
                    resetForm();
                    setStatusMsg(['info', 'Tiedot tallennettu!']);
                    setTimeout(dataUpdated, 1000)
                })
                // kopataan mahdolliset virheet
                .catch((e) =>
                    setStatusMsg(['error', `Virhe tietojen tallennuksessa: ${e.message}`])
                );
            return;
        }

        const form = event.target;
        const lisaaja = user.email;
        const kilpailu = kilpailuId;
        // kootaan kenttien tiedot 
        const joukkue = {
            nimi: nimi.trim(),
            sarja,
            jasenet: jasenet
                .filter((j) => j !== "")
                .map((j) => j.trim())
                .sort((a, b) => a.localeCompare(b)),
            lisaaja,
            kilpailu,
            leimauksia: valittuJoukkue ? valittuJoukkue.leimauksia : 0
        };
        // tarkistetaan että jäseniä on oikea määrä
        validateJasenet(joukkue.jasenet);
        if (form.reportValidity()) {
            // jos id, ollaan muokkaamassa olemassa olevaa joukkuetta
            if (id) {
                //tallennellaan
                dataService
                    .tallennaMuokattuJoukkue(id, joukkue)
                    .then(() => {
                        resetForm();
                        setStatusMsg(['info', 'Tiedot tallennettu!']);
                        setTimeout(dataUpdated, 1000)
                    })
                    .catch((e) =>
                        setStatusMsg(['error', `Virhe tietojen tallennuksessa: ${e.message}`])
                    );
                // ...muuten lisätään uutena joukkueena
            } else {
                dataService
                    .lisaaJoukkue(joukkue)
                    .then(() => {
                        resetForm();
                        setStatusMsg(['info', 'Tiedot tallennettu!']);
                        setTimeout(dataUpdated, 1000)
                    })
                    .catch((e) =>
                        setStatusMsg(['error', `Virhe tietojen tallennuksessa: ${e.message}`])
                    );
            }
        }
    };

    // sarjainputit
    const sarjaInputElems = sarjat
        ? sarjat.map((s, i) => {
            return (
                <SarjaInput
                    key={`sarja-${s.id}`}
                    id={s.id}
                    valittuSarja={sarja}
                    onSelectHandler={onSarjaInputChange}
                    index={i}
                />
            );
        })
        : [];

    // jäseninputit
    const jasenInputElems = [...Array(5).keys()].map((index) => {
        return (
            <JasenInput
                key={`jasenInput-${index}`}
                index={index}
                value={jasenet[index]}
                onChangeHandler={onJasenInputChange}
                domRef={jasenInputRefs[index]}
            />
        );
    });

    return (
        <section>
            {/* Vvlitaan otsikko sen mukaan ollaanko muokkaamassa vanhaa vai lisäämässä uutta */}
            { valittuJoukkue ? <h3>Muokkaa joukkuetta</h3> : <h3>Lisää joukkue</h3>}
            <form className="joukkueform" onSubmit={onSubmitForm} noValidate>
                <label htmlFor="joukkueform-nimi">Nimi</label>
                <input
                    id="joukkueform-nimi"
                    name="nimi"
                    required="required"
                    type="text"
                    value={nimi}
                    onChange={onNimiInputChange}
                    onBlur={onNimiInputBlur}
                />
                <label>Sarja</label>
                <div>{sarjaInputElems}</div>
                <label>Jäsenet</label>
                <div>{jasenInputElems}</div>
                {/* näytetään poistokenttä vain muokattaessa */}
                {valittuJoukkue ? (
                    <>
                        <label htmlFor={`joukkueform-poista`}>
                            Poista joukkue
                        </label>
                        <input
                            type="checkbox"
                            id={`joukkueform-poista`}
                            name="poista"
                            value="poista"
                            checked={poista}
                            onChange={onPoistaInputChange}
                        />
                    </>
                ) : null}
                {statusMsg ?
                    <div className={`message ${statusMsg[0]}`}>{statusMsg[1]}</div> : null}
                <button type="submit">Tallenna</button>
            </form>
        </section>
    );
};

export default JoukkueTab;
