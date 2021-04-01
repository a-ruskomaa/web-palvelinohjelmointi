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

    const jasenInputRefs = [
        useRef(null),
        useRef(null),
        useRef(null),
        useRef(null),
        useRef(null),
    ];

    // Nollataan lomake jos kilpailu vaihtuu
    useEffect(() => {
        if (valittuJoukkue) {
            console.log("Täytetään lomake");
            setId(valittuJoukkue.id);
            setNimi(valittuJoukkue.nimi);
            setSarja(valittuJoukkue.sarja);
            setJasenet(
                valittuJoukkue.jasenet.concat(
                    Array(5 - valittuJoukkue.jasenet.length).fill("")
                )
            );
        } else {
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
                        setSarja(malliJoukkue.sarja);
                        setJasenet(
                            malliJoukkue.jasenet.concat(
                                Array(5 - malliJoukkue.jasenet.length).fill("")
                            )
                        );
                    }
                });
        }
        return () => {
            resetForm();
            console.log("Lomake nollattu");
        };
    }, [kilpailuId, valittuJoukkue]);

    const resetForm = () => {
        setId();
        setNimi("");
        setSarja();
        setJasenet(Array(5).fill(""));
        setPoista(false)
        setStatusMsg();
    };

    const onNimiInputChange = (event) => {
        const nimiInput = event.target;
        nimiInput.setCustomValidity("");

        if (nimiInput.value.trim() === "") {
            nimiInput.setCustomValidity("Joukkueen nimi ei voi ola tyhjä!");
        }

        setNimi(nimiInput.value);
    };

    const onNimiInputBlur = (event) => {
        const nimiInput = event.target;

        if (nimiInput.validity.valid) {
            sarjat.forEach((sarja) => {
                const samanNimisia = sarja.joukkueet.some(
                    (j) =>
                        j.nimi.toLowerCase() ===
                            nimiInput.value.trim().toLowerCase() && j.id !== id
                );
                if (samanNimisia) {
                    nimiInput.setCustomValidity(
                        "Kilpailussa on jo samanniminen joukkue!"
                    );
                }
            });
        }
    };

    const onJasenInputChange = (i, event) => {
        const jasenInput = event.target;

        jasenInput.setCustomValidity("");

        if (jasenInput.value.match(/\d/)) {
            jasenInput.setCustomValidity(
                "Jäsenen nimessä ei saa olla numeroita"
            );
        } else if (jasenInput.value !== "" && jasenInput.value.trim() === "") {
            jasenInput.setCustomValidity("Jäsenen nimi ei voi olla tyhjä");
        }

        let updatedJasenet = [...jasenet];
        updatedJasenet[i] = jasenInput.value;
        setJasenet(updatedJasenet);
    };

    const onSarjaInputChange = (event) => {
        setSarja(event.target.value);
    };

    const onPoistaInputChange = (event) => {
        setPoista(event.target.checked);
    };

    const validateJasenet = (jasenet) => {
        const jasenInputs = jasenInputRefs.map((ref) => ref.current);
        if (jasenet.length < 2 || jasenet.length > 5) {
            const ekaTyhja = jasenInputs.find((jasenInput) => {
                console.log(jasenInput);

                return jasenInput.value.trim() == "";
            });
            ekaTyhja.setCustomValidity("Anna 2-5 jäsentä!");
        } else {
            jasenInputs.forEach((j) => {
                if (j.validationMessage === "Anna 2-5 jäsentä!") {
                    j.setCustomValidity("");
                }
            });
        }
    };

    const onSubmitForm = (event) => {
        event.preventDefault();
        if (
            poista &&
            window.confirm(`Haluatko varmasti poistaa joukkueen ${nimi}?`)
        ) {
            console.log("poistetaan", nimi);
            dataService
                .poistaJoukkue(id)
                .then(() => {
                    resetForm();
                    setStatusMsg(['info','Tiedot tallennettu!']);
                    dataUpdated();
                })
                .catch((e) =>
                    setStatusMsg(['error',`Virhe tietojen tallennuksessa: ${e.message}`])
                );
            return;
        }
        const form = event.target;
        const lisaaja = user.email;
        const kilpailu = kilpailuId;
        const joukkue = {
            nimi: nimi.trim(),
            sarja,
            jasenet: jasenet
                .filter((j) => j.trim() !== "")
                .map((j) => j.trim())
                .sort((a, b) => a.localeCompare(b)),
            lisaaja,
            kilpailu,
        };
        validateJasenet(joukkue.jasenet);
        if (form.reportValidity()) {
            if (id) {
                console.log("muokataan", id, joukkue);
                dataService
                    .tallennaMuokattuJoukkue(id, joukkue)
                    .then(() => {
                        resetForm();
                        setStatusMsg(['info','Tiedot tallennettu!']);
                        dataUpdated();
                    })
                    .catch((e) =>
                        setStatusMsg(['error',`Virhe tietojen tallennuksessa: ${e.message}`])
                    );
            } else {
                console.log("tallennetaan", joukkue);
                dataService
                    .lisaaJoukkue(joukkue)
                    .then(() => {
                        resetForm();
                        setStatusMsg(['info','Tiedot tallennettu!']);
                        dataUpdated();
                    })
                    .catch((e) =>
                        setStatusMsg(['error',`Virhe tietojen tallennuksessa: ${e.message}`])
                    );
            }
        }
    };

    const sarjaInputElems = sarjat
        ? sarjat.map((sarja, i) => {
              return (
                  <SarjaInput
                      key={`sarja-${sarja.id}`}
                      id={sarja.id}
                      valittuSarja={sarja.id}
                      onSelectHandler={onSarjaInputChange}
                      index={i}
                  />
              );
          })
        : [];

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
                { statusMsg ? 
                <div className={statusMsg[0]}>{statusMsg[1]}</div> :
                null }
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
                <button type="submit">Tallenna</button>
            </form>
        </section>
    );
};

export default JoukkueTab;
