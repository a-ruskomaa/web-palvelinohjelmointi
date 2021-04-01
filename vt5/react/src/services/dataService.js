import { auth, db } from './firebase'

const PORT = window.location.hostname === 'localhost' ? ":5000" : ""
const BASE_URL = `${window.location.protocol}//${window.location.hostname}${PORT}/api`

async function haeSarjat(kilpailuId) {
    console.log(`haetaan kilpailun ${kilpailuId} sarjat`);
    try {
        const idToken = await auth.currentUser.getIdToken();

        const res = await fetch(`${BASE_URL}/kilpailut/${kilpailuId}/sarjat`, {
            method: "GET",
            headers: {
                Authorization: "Bearer " + idToken,
            },
        });
        const sarjat = await res.json();
        console.log("sarjat json", sarjat)
        const sarja_arr = Object.entries(sarjat).map(([id, sarja]) => {
            sarja.id = id
            sarja.joukkueet = Object.entries(sarja.joukkueet).map(([id, joukkue]) => {
                joukkue.id = id;
                return joukkue
            })
            return sarja
        })
        console.log("sarja_arr", sarja_arr)
        return sarja_arr
    } catch (err) {
        console.log(err);
        return []
    }
}


async function haeRastit(kilpailuId) {
    console.log(`haetaan kilpailun ${kilpailuId} rastit`);
    try {
        const idToken = await auth.currentUser.getIdToken();

        const res = await fetch(`${BASE_URL}/kilpailut/${kilpailuId}/rastit`, {
            method: "GET",
            headers: {
                Authorization: "Bearer " + idToken,
            },
        });
        const rastit = await res.text();
        const parser = new DOMParser();
        const xmlDoc = parser.parseFromString(rastit, "application/xml");
        
        const rasti_arr = Array.from(xmlDoc.getElementsByTagName('rasti'))
            .map(rasti => {
                const [id,koodi,lat,lon] = Array.from(rasti.childNodes)
                                            .map(n => n.textContent);
                return {
                    id,
                    koodi,
                    lat,
                    lon
                }
        });
        
        console.log("rasti_arr",rasti_arr);
        return rasti_arr
    } catch (err) {
        console.log(err);
        return []
    }
}

// async function haeRastit(kilpailuId) {
//     console.log(`haetaan kilpailun ${kilpailuId} rastit`);
//     const fsRastit = await db
//         .collection(`kilpailut/${kilpailuId}/rastit`)
//         .get();
//     return luoTaulukko(fsRastit);
// }

async function lisaaJoukkue(joukkue) {
    console.log("lisataan uusi", joukkue);
    return await db.collection("joukkueet").add(joukkue);
}

async function tallennaMuokattuJoukkue(joukkueId, joukkue) {
    console.log("tallennetaan muokattu", joukkue);
    return await db.doc(`joukkueet/${joukkueId}`).set(joukkue);
}

async function poistaJoukkue(joukkueId) {
    console.log("poistetaan joukkue", joukkueId);
    return await db.doc(`joukkueet/${joukkueId}`).delete();
}

/**
 * Etsii tietokannasta rajausehtoja vastaavat joukkueet ja palauttaa ne taulukossa.
 * 
 * Esim. haeJoukkueetRajauksilla(['nimi','!=','mallijoukkue],['kilpailu','==','pikakisa'])
 * etsii kaikki kilpailun 'pikakisa' joukkueet joiden nimi ei ole mallijoukkue.
 * 
 * @param {Array} rajausehdot taulukossa muodossa ['ehto','operaattori','arvo']
 * @returns {Array} palauttaa rajausehtojen mukaiset joukkueet taulukossa
 */
async function haeJoukkueetRajauksilla(rajausehdot) {
    console.log(`haetaan joukkuetta rajauksilla: `, rajausehdot);
    const query = rajausehdot.reduce((acc, [ehto, op, arvo]) => {
        return acc.where(ehto, op, arvo);
    }, db.collection("joukkueet"));

    const fsJoukkueet = await query.get();

    return luoTaulukko(fsJoukkueet);
}

async function haeJoukkueIdlla(joukkueId) {
    console.log(`haetaan joukkuetta id: ${joukkueId}`);
    const fsJoukkue = await db.doc(`joukkueet/${joukkueId}`).get();

    const joukkue = fsJoukkue.data();
    joukkue.id = fsJoukkue.id;

    return joukkue;
}

async function haeKaikkiKilpailut() {
    console.log("haetaan kaikki kilpailut");
    const fsKilpailut = await db.collection("kilpailut").get();
    return luoTaulukko(fsKilpailut);
}

async function haeJoukkueenLeimaukset(joukkueId) {
    console.log(`haetaan joukkueen ${joukkueId} leimaukset`);
    const fsLeimaukset = await db
        .collection(`joukkueet/${joukkueId}/leimaukset`)
        .get();
    console.log("fsLeimaukset", joukkueId, fsLeimaukset);
    return luoTaulukko(fsLeimaukset);
}

async function tallennaJoukkueenLeimaukset(joukkueId, leimaukset) {
    const collectionRef = db.collection(`joukkueet/${joukkueId}/leimaukset`);

    const batch = db.batch();

    leimaukset.forEach((leimaus) => {
        const docRef = collectionRef.doc(leimaus.id)
        console.log("docRef", docRef);
        if (leimaus.poista) {
            batch.delete(docRef);
        } else {
            batch.set(docRef, {'aika': leimaus.aika, 'rasti': leimaus.rasti})
        }
    })

    return await batch.commit();

}

function luoTaulukko(fsTaulukko) {
    const taulukko = [];

    fsTaulukko.forEach((e) => {
        const element = e.data();
        element.id = e.id;
        taulukko.push(element);
    });

    return taulukko;
}

const dataService = {
    haeKaikkiKilpailut,
    haeSarjat,
    haeRastit,
    haeJoukkueIdlla,
    haeJoukkueetRajauksilla,
    haeJoukkueenLeimaukset,
    tallennaJoukkueenLeimaukset,
    lisaaJoukkue,
    tallennaMuokattuJoukkue,
    poistaJoukkue
}

export default dataService