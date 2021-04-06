import React, { useEffect, useState } from "react";
import LeimausInput from './LeimausInput'
import dataService from "services/dataService";

const LeimausTab = ({ kayttajanJoukkue, kilpailunRastit, valittuKilpailu, dataUpdated }) => {
    const [leimaukset, setLeimaukset] = useState([]);
    const [loadingLeimaukset, setLoadingLeimaukset] = useState(false);
    const [statusMsg, setStatusMsg] = useState();

    // haetaan joukkueen leimaukset joukkueen vaihtuessa tai ensimmäisellä latauksella
    useEffect(() => {
        setLoadingLeimaukset(true);
        // haetaan leimaukse
        dataService.haeJoukkueenLeimaukset(kayttajanJoukkue.id)
            .then(leimaukset => {
                // lisätään tyhjä leimaus uuden lisäämistä varten
                leimaukset.push({ aika: "", rasti: "", uusi: true });
                setLeimaukset(leimaukset);
                setLoadingLeimaukset(false);
            })
        return (() => {
            setLoadingLeimaukset(false);
        })
    }, [kayttajanJoukkue])

    // käsittelee aikainputit change-eventin
    const onAikaInputChange = (event, i) => {
        const muokatutLeimaukset = [...leimaukset]
        muokatutLeimaukset[i].aika = event.target.value;
        // merkataan leimaus muokatuksi
        muokatutLeimaukset[i].muokattu = true;
        // jos muokataan uutta leimausta, tallenetaan tilaan myös oletusarvoinen rasti
        if (muokatutLeimaukset[i].rasti === "") {
            muokatutLeimaukset[i].rasti = kilpailunRastit[0].id
        }
        // jos muokataan viimeistä kenttää, lisätään uusi tyhjä leimaus
        if (i === leimaukset.length - 1) {
            muokatutLeimaukset.push({ aika: "", rasti: "", uusi: true })
        }
        setLeimaukset(muokatutLeimaukset);
    };

    // käsitteleen aikaunputin blur-eventin
    const onAikaInputBlur = (event, i) => {
        const aikaInput = event.target;

        // ei validoida viimeistä kenttää, koska se on aina tyhjä
        if (i !== leimaukset.length - 1) {
            aikaInput.setCustomValidity("");
            // koitetaan parsia kentän sisällöstä date
            let date;
            try {
                // tähän olisi parempi käyttää esim. momentJS kirjastoa
                date = aikaleimaDateksi(aikaInput.value)
                if (isNaN(date.getTime())) {
                    aikaInput.setCustomValidity("Virheellinen aika!")
                    return 
                }
            } catch (error) {
                // jos parse ei onnistunut, invalidoidaan kenttä
                aikaInput.setCustomValidity("Virheellinen aika!")
                return
            }
            let alkuaika;
            try {
                // muunnetaan kilpailun alkuaika dateksi
                alkuaika = aikaleimaDateksi(valittuKilpailu.alkuaika)
            } catch (error) {
                console.log(error);
            }
            // verrataan kilpailun alkuaikaan
            if (date < alkuaika) {
                aikaInput.setCustomValidity(`Leimaus ei voi olla ennen kilpailun alkua: (${valittuKilpailu.alkuaika}!`)
            }
        }
    }


    /** 
     * Muuntaa yyyy-MM-dd hh:ss:mm-muotoisen merkkijonon Date-objektiksi
     * @param {string} aikaleima
     * @returns {Date}
     */
    const aikaleimaDateksi = (aikaleima) => {
        let ajat = aikaleima.split(/\D+/).map(t => parseInt(t));
        // miinustetaan kuukauden arvosta yksi, koska javascript
        ajat[1]--;
        let date = new Date(...ajat);
        //tarkistetaan vielä että päivämäärä meni oikein
        if (date.getFullYear() === ajat[0] &&
            date.getMonth() === ajat[1] &&
            date.getDate() === ajat[2] &&
            date.getHours() === ajat[3] &&
            date.getMinutes() === ajat[4] &&
            date.getSeconds() === ajat[5]) {
            return date;
        } else {
            //palautetaan invalid date jos meni pieleen
            return new Date("foo");
        }
    }

    // käsitellään rastin valinta
    const onRastiSelectChange = (event, i) => {
        const muokatutLeimaukset = [...leimaukset]
        muokatutLeimaukset[i].rasti = event.target.value;
        // merkataan leimaus muokatuksi
        muokatutLeimaukset[i].muokattu = true;
        setLeimaukset(muokatutLeimaukset);
    };

    // käsitellään poistokentän valinta
    const onPoistaInputChange = (event, i) => {
        const muokatutLeimaukset = [...leimaukset]
        muokatutLeimaukset[i].poista = event.target.value;
        setLeimaukset(muokatutLeimaukset);
    };


    // käsittelee lomakkeen lähetyksen
    const onSubmitForm = (event) => {
        event.preventDefault();
        setStatusMsg();
        const leimausForm = event.target;


        if (leimausForm.reportValidity()) {
            // tallennetaan leimaukset, jätetään viimeinen tyhjä rivi huomioimatta
            dataService.tallennaJoukkueenLeimaukset(kayttajanJoukkue.id, leimaukset.slice(0, -1))
                .then(() => {
                    setStatusMsg(['info', 'Tiedot tallennettu!'])
                    setTimeout(dataUpdated, 1000)
                })
                .catch((e) =>
                    setStatusMsg(['error', `Virhe tietojen tallennuksessa: ${e.message}`])
                );
        }
    };

    
    const leimausElems = leimaukset.map((leimaus, i) => {
        return <LeimausInput
            key={`leimausInput-${i}`}
            aika={leimaus.aika}
            rasti={leimaus.rasti}
            index={i}
            rastit={kilpailunRastit}
            onAikaInputChange={onAikaInputChange}
            onRastiSelectChange={onRastiSelectChange}
            onPoistaInputChange={onPoistaInputChange}
            onAikaInputBlur={onAikaInputBlur} />
    })

    return (
        <section>
            <h3>Joukkueen "{kayttajanJoukkue.nimi}" leimaukset: </h3>
            { loadingLeimaukset ?
                <p>Ladataan leimauksia...</p> :
                <form className="leimausform" onSubmit={onSubmitForm} noValidate>
                    {leimausElems}
                    {statusMsg ?
                        <div className={`message ${statusMsg[0]}`}>{statusMsg[1]}</div> :
                        null}
                    <button type="submit">Tallenna</button>
                </form>}
        </section>
    )
}

export default LeimausTab