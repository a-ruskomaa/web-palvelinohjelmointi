import React, { useEffect, useState, useMemo } from "react";
import RastiInput from './RastiInput'
import dataService from "services/dataService";

const RastiTab = ({ kilpailunRastit, valittuKilpailu, dataUpdated }) => {
    const [rastit, setRastit] = useState([]);
    const [statusMsg, setStatusMsg] = useState();

    // käytetään memoa dom-elementtien referenssien tallentamiseen
    const inputRefs = useMemo(() => Array(rastit.length).fill(0).map(i => [React.createRef(), React.createRef()]), [rastit]);

    // tallennetaan kilpailun rastit komponentin tilaan muokkauksia varten
    useEffect(() => {
        const muokattavatRastit = [...kilpailunRastit]
        // lisätään tyhjä rivi uutta rastia varten
        muokattavatRastit.push({ koodi: "", lat: undefined, lon: undefined, uusi: true })
        setRastit(muokattavatRastit)
        return () => {
            setRastit()
        }
    }, [kilpailunRastit])

    // käsittelee koodi-inputin change-eventin
    const onKoodiInputChange = (event, i) => {
        const koodiInput = event.target;
        const koodi = koodiInput.value;

        koodiInput.setCustomValidity("");

        // ei tyhjiä kenttiä
        if (koodi.trim() === "") {
            koodiInput.setCustomValidity("Koodi ei voi olla tyhjä!")
        }

        const muokattavatRastit = [...rastit]
        muokattavatRastit[i].koodi = koodi;
        muokattavatRastit[i].muokattu = true;

        // jos muokataan viimeistä rastia, lisätään uusi rivi
        if (i === rastit.length - 1) {
            muokattavatRastit.push({ koodi: "", lat: "", lon: "", uusi: true })
        }

        setRastit(muokattavatRastit);
    }

    // käsittelee koodi-inputin blur-eventin
    const onKoodiInputBlur = (event, index) => {
        const koodiInput = event.target;
        const koodi = koodiInput.value;

        // onko kilpailussa jo sama koodi
        if (index !== rastit.length - 1 && koodi !== "") {
            const toinen = rastit.find((r, i) => r.koodi === koodi && i !== index)
            if (toinen) {
                koodiInput.setCustomValidity("Koodi on jo käytössä!")
            }
        }
    }

    // käsittelee lat-inputin change-eventin
    const onLatInputChange = (event, i) => {
        const latInput = event.target;
        const lat = latInput.value;

        latInput.setCustomValidity("");
        // tarkistetaan että arvo on oikealla välillä oleva (liuku)luku
        try {
            const latFloat = parseFloat(lat);
            if (latFloat > 90 || latFloat < -90) {
                latInput.setCustomValidity("Anna arvo väliltä [-90,90]!");
            }
        } catch (error) {
            latInput.setCustomValidity("Virheellinen arvo!");
        }

        const muokattavatRastit = [...rastit];
        muokattavatRastit[i].lat = lat;
        muokattavatRastit[i].muokattu = true;
        setRastit(muokattavatRastit);
    }

    // käsittelee lon-inputin change-eventin
    const onLonInputChange = (event, i) => {
        const lonInput = event.target;
        const lon = lonInput.value;

        lonInput.setCustomValidity("");
        // tarkistetaan että arvo on oikealla välillä oleva (liuku)luku
        try {
            const lonFloat = parseFloat(lon);
            if (lonFloat > 180 || lonFloat < -180) {
                lonInput.setCustomValidity("Anna arvo väliltä [-180,180]!");
            }
        } catch (error) {
            lonInput.setCustomValidity("Virheellinen arvo!");
        }

        const muokattavatRastit = [...rastit];
        muokattavatRastit[i].lon = lon;
        muokattavatRastit[i].muokattu = true;
        setRastit(muokattavatRastit);
    }

    // käsittelee poistokentän change-eventin
    const onPoistaInputChange = (event, i) => {
        const muokattavatRastit = [...rastit]
        muokattavatRastit[i].poista = event.target.value;
        setRastit(muokattavatRastit);
    }

    // käsittelee lomakkeen lähetyksen
    const onSubmitForm = (event) => {
        event.preventDefault();
        setStatusMsg();
        const rastiForm = event.target;

        validateLatLng();

        if (rastiForm.reportValidity()) {
            let poistaLeimaukset = false;
            // jos joku rasti on merkitty poistettavaksi, varmistetaan mitä tehdään
            if (rastit.some(r => r.poista)) {
                poistaLeimaukset = window.confirm("Poistetaanko myös poistettavien rastien leimaukset?");
                const varmistaPoisto = window.confirm("Haluatko varmasti poistaa valitut rastit ja niiden leimaukset?");
                // ei poistetakaan
                if (!varmistaPoisto) {
                    rastit.forEach(r => {
                        r.poista = false;
                    })
                }
            }

            // tallennellaan rastit
            dataService.tallennaKilpailunRastit(valittuKilpailu.id, rastit.slice(0, -1), poistaLeimaukset)
                .then(() => {
                    setStatusMsg(['info', 'Tiedot tallennettu!']);
                    setTimeout(dataUpdated, 1000)
                })
                .catch((e) =>
                    setStatusMsg(['error', `Virhe tietojen tallennuksessa: ${e.message}`])
                );
        }
    };

    // merkkaa tyhjät lat ja lng input-kentät invalideiksi
    const validateLatLng = () => {
        inputRefs.forEach((refs, index) => {
            refs.forEach(ref => {
                const input = ref.current
                if (input.value === "" && index !== inputRefs.length - 1) {
                    input.setCustomValidity("Kenttä ei voi olla tyhjä!")
                } else if (input.validationmessage === "Kenttä ei voi olla tyhjä!") {
                    input.current.setCustomValidity("")
                }
            })
        })
    }


    const rastiElems = rastit.map((rasti, i) => {
        return <RastiInput
            key={`rasti-input-${i}`}
            index={i}
            koodi={rasti.koodi}
            lat={rasti.lat}
            lon={rasti.lon}
            domRef={inputRefs[i]}
            onKoodiInputChange={onKoodiInputChange}
            onKoodiInputBlur={onKoodiInputBlur}
            onLatInputChange={onLatInputChange}
            onLonInputChange={onLonInputChange}
            onPoistaInputChange={onPoistaInputChange} />
    })


    return (
        <section>
            <h3>Kilpailun "{valittuKilpailu.id}" rastit: </h3>
            <form className="rastiform" onSubmit={onSubmitForm} noValidate>
                {rastiElems}
                {statusMsg ?
                    <div className={`message ${statusMsg[0]}`}>{statusMsg[1]}</div> :
                    null}
                <button type="submit">Tallenna</button>
            </form>
        </section>
    )
}



export default RastiTab