import React, { useEffect, useState } from "react";
import LeimausInput from './LeimausInput'
import dataService from "services/dataService";

const LeimausTab = ({kayttajanJoukkue, kilpailunRastit}) => {
    const [leimaukset, setLeimaukset ] = useState([]);
    const [loadingLeimaukset, setLoadingLeimaukset] = useState(false);
    const [statusMsg, setStatusMsg] = useState();
    
    useEffect(() => {
        setLoadingLeimaukset(true);
        dataService.haeJoukkueenLeimaukset(kayttajanJoukkue.id).then(leimaukset => {
            console.log("haettu leimaukset", leimaukset);
            leimaukset.push({aika: "", rasti: ""});
            setLeimaukset(leimaukset);
            setLoadingLeimaukset(false);
        })
        return (() => {
            setLoadingLeimaukset(false);
        })
    }, [kayttajanJoukkue])

    const onSubmitForm = (event) => {
        event.preventDefault();
        setStatusMsg();
        const leimausForm = event.target;
        
        if (leimausForm.reportValidity()) {
            console.log("tallennetaan leimaukset", leimaukset.slice(0, -1))
            dataService.tallennaJoukkueenLeimaukset(kayttajanJoukkue.id, leimaukset.slice(0, -1))
            .then(() => {
                setStatusMsg(['info','Tiedot tallennettu!']);
            })
            .catch((e) =>
                setStatusMsg(['error',`Virhe tietojen tallennuksessa: ${e.message}`])
            );
        }
    };

    const onAikaInputChange = (event, i) => {
        const updatedLeimaukset = [...leimaukset]
        updatedLeimaukset[i].aika = event.target.value;
        if (i === leimaukset.length - 1) {
            updatedLeimaukset.push({aika: "", rasti: ""})
        }
        setLeimaukset(updatedLeimaukset);
    };

    const onAikaInputBlur = (event, i) => {
        const aikaInput = event.target
        const aika = aikaInput.value;

        if (i !== leimaukset.length - 1 && !leimaukset[i].poista) {
            aikaInput.setCustomValidity("")
            const ajat = aika.split(/\D+/).map(t => parseInt(t));
            ajat[1]--;
            if (isNaN(Date.parse(...ajat))) {
                aikaInput.setCustomValidity("Virheellinen aika!")
            }
        }
    }

    const onRastiSelectChange = (event, i) => {
        const updatedLeimaukset = [...leimaukset]
        updatedLeimaukset[i].rasti = event.target.value;
        setLeimaukset(updatedLeimaukset)
    };

    const onPoistaInputChange = (event, i) => {
        const updatedLeimaukset = [...leimaukset]
        updatedLeimaukset[i].poista = event.target.value;
        setLeimaukset(updatedLeimaukset)
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
                { leimausElems}
                { statusMsg ? 
                <div className={statusMsg[0]}>{statusMsg[1]}</div> :
                null }
                <button type="submit">Tallenna</button>
            </form> }
        </section>
    )
}

export default LeimausTab