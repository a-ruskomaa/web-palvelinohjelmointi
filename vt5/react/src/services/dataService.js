import { auth, db } from './firebase'

const PORT = window.location.hostname === 'localhost' ? ":5000" : ""
const BASE_URL = `${window.location.protocol}//${window.location.hostname}${PORT}/api`

// Hakee kilpailun sarjat palvelimelta. Palvelin palauttaa sarjat tehtävänannon mukaisesti json-muodossa.
async function haeSarjat(kilpailuId) {
    try {
        // liitetään pyyntöön id-tokeni jolla käyttäjä tunnistetaan palvelimella
        const idToken = await auth.currentUser.getIdToken();

        // tehdään pyyntö
        const res = await fetch(`${BASE_URL}/kilpailut/${kilpailuId}/sarjat`, {
            method: "GET",
            headers: {
                Authorization: "Bearer " + idToken,
            },
        });
        const sarjat = await res.json();
        // luodaan sarjoista taulukko, jossa jokainen sarja sisältää joukkueet niin ikään taulukossa
        const sarja_arr = Object.entries(sarjat).map(([id, sarja]) => {
            sarja.id = id
            sarja.joukkueet = Object.entries(sarja.joukkueet).map(([id, joukkue]) => {
                joukkue.id = id;
                return joukkue
            })
            return sarja
        })
        return sarja_arr
    } catch (err) {
        console.log(err);
        return []
    }
}


// Hakee kilpailun rastit palvelimelta. Palvelin palauttaa rastit tehtävänannon mukaisesti xml-muodossa.
async function haeRastit(kilpailuId) {
    try {
        // liitetään pyyntöön id-tokeni jolla käyttäjä tunnistetaan palvelimella
        const idToken = await auth.currentUser.getIdToken();

        // tehdään pyyntö
        const res = await fetch(`${BASE_URL}/kilpailut/${kilpailuId}/rastit`, {
            method: "GET",
            headers: {
                Authorization: "Bearer " + idToken,
            },
        });
        const rastit = await res.text();
        const parser = new DOMParser();
        const xmlDoc = parser.parseFromString(rastit, "application/xml");

        // luodaan rasteista taulukko
        const rasti_arr = Array.from(xmlDoc.getElementsByTagName('rasti'))
            .map(rasti => {
                // kopataan rastin data rasti-elementtien lapsielementeistä
                // tässä vähän oikaistaan ja luotetaan siihen että palvelin lähettää datan halutussa järjestyksessä
                const [id, koodi, lat, lon] = Array.from(rasti.childNodes)
                                                    .map(n => n.textContent);
                return {
                    id,
                    koodi,
                    lat,
                    lon
                }
            });

        return rasti_arr
    } catch (err) {
        console.log(err);
        return []
    }
}

/**
 * Lisää annetun joukkueen tietokantaan.
 * 
 * @param {object} joukkue lisättävä joukkue
 */
async function lisaaJoukkue(joukkue) {
    return await db.collection("joukkueet").add(joukkue);
}

/**
 * Lisää annetun joukkueen tietokantaan.
 * 
 * @param {string} joukkueId lisättävän joukkueen id
 * @param {object} joukkue lisättävä joukkue
 */
async function tallennaMuokattuJoukkue(joukkueId, joukkue) {
    // data olisi ehkä fiksumpi denormalisoida ja tallentaa id myös joukkueen attribuutiksi?
    return await db.doc(`joukkueet/${joukkueId}`).set(joukkue);
}

/**
 * Poistaa id:n mukaisen joukkueen
 * 
 * @param {string} Poistettavan joukkueen id
 */
async function poistaJoukkue(joukkueId) {
    return await db.doc(`joukkueet/${joukkueId}`).delete();
}

/**
 * Etsii tietokannasta rajausehtoja vastaavat joukkueet ja palauttaa ne taulukossa.
 * 
 * Esim. haeJoukkueetRajauksilla([['nimi','!=','mallijoukkue],['kilpailu','==','pikakisa']])
 * etsii kaikki kilpailun 'pikakisa' joukkueet joiden nimi ei ole mallijoukkue.
 * 
 * @param {string[][]} rajausehdot taulukossa muodossa [['ehto','operaattori','arvo'],...]
 * @returns {object[]} palauttaa rajausehtojen mukaiset joukkueet taulukossa
 */
async function haeJoukkueetRajauksilla(rajausehdot) {
    // lisätään kaikki halutut rajaukset queryyn
    const query = rajausehdot.reduce((acc, [ehto, op, arvo]) => {
        return acc.where(ehto, op, arvo);
    }, db.collection("joukkueet"));

    const fsJoukkueet = await query.get();

    return luoTaulukko(fsJoukkueet);
}

/**
 * Hakee id:n mukaisen joukkueen tietokannasta.
 * 
 * @param {string} joukkueId 
 * @returns {object}
 */
async function haeJoukkueIdlla(joukkueId) {
    const fsJoukkue = await db.doc(`joukkueet/${joukkueId}`).get();

    const joukkue = fsJoukkue.data();
    joukkue.id = fsJoukkue.id;

    return joukkue;
}

/**
 * Hakee kaikki tietokantaan tallennetut kilpailut.
 * @returns 
 */
async function haeKaikkiKilpailut() {
    const fsKilpailut = await db.collection("kilpailut").get();
    return luoTaulukko(fsKilpailut);
}

/**
 * Hakee id:n mukaisen joukkueen leimaukset
 * 
 * @param {string} joukkueId 
 * @returns {object[]} Leimaukset palautetaan taulukollisina objekteja
 */
async function haeJoukkueenLeimaukset(joukkueId) {
    const fsLeimaukset = await db
        .collection(`joukkueet/${joukkueId}/leimaukset`)
        .get();
    return luoTaulukko(fsLeimaukset);
}

/**
 * Tallentaa joukkueen leimaukset tietokantaan.
 * 
 * @param {string} joukkueId 
 * @param {object[]} leimaukset 
 * @returns 
 */
async function tallennaJoukkueenLeimaukset(joukkueId, leimaukset) {
    const collectionRef = db.collection(`joukkueet/${joukkueId}/leimaukset`);

    // tallennetaan leimaukset batchina
    const batch = db.batch();

    // Lasketaan tallennettujen leimausten määrä ja tallennetaan luku joukkueen tietoihin.
    // Tämä on tehokkaampaa tehdä näin, kuin laskea tieto erillisillä kyselyillä, koska fs ei
    // tarjoa järkeviä count() tai sum()-funktioita
    let leimauksia = 0;
    leimaukset.forEach((leimaus) => {
        const docRef = collectionRef.doc(leimaus.id);
        // poistetaan poistettavat
        if (leimaus.poista) {
            batch.delete(docRef);
            if (!leimaus.uusi) {
                // vähennetään leimausten lukumäärästä yksi (vain jos leimaus on tallennettu aiemmin)
                leimauksia -= 1;
            }
        // tallennetaan uudet ja muokatut leimaukset
        } else if (leimaus.uusi || leimaus.muokattu) {
            batch.set(docRef, { aika: leimaus.aika, rasti: leimaus.rasti, joukkue: joukkueId })
            if (leimaus.uusi) {
                // Kasvatetaan leimausten lukumäärää
                leimauksia += 1;
            }
        }
    })

    // tallennetaan tieto leimausten määrästä 
    const joukkueRef = db.doc(`joukkueet/${joukkueId}`)

    // päivitetään joukkueen leimausten lukumäärää erillisessä transaktiossa
    db.runTransaction((transaction) => {
        return transaction.get(joukkueRef).then((joukkue) => {
            const leimauksiaUusi = joukkue.data().leimauksia + leimauksia;

            transaction.update(joukkueRef, { leimauksia: leimauksiaUusi }, { merge: true })
        })
    });

    // todo poista await?
    return await batch.commit();

}

/**
 * Tallenetaan kilpailun rastit.
 * 
 * @param {string} kilpailuId Id kilpailulle, johon rasit kuuluvat.
 * @param {array} rastit Tallennettavat rastit
 * @param {boolean} poistaLeimaukset Jos rasteja on merkitty poistettaviksi, poistetaanko myös niihin liittyvät leimaukset.
 * @returns 
 */
async function tallennaKilpailunRastit(kilpailuId, rastit, poistaLeimaukset) {
    const collectionRef = db.collection(`kilpailut/${kilpailuId}/rastit`);

    const batch = db.batch();

    rastit.forEach((rasti) => {
        const docRef = collectionRef.doc(rasti.id);
        if (rasti.poista) {
            batch.delete(docRef);
            // poistetaan rastiin liittyvät leimaukset
            poistaLeimauksetRajauksilla([['rasti', '==', rasti.id]], poistaLeimaukset, kilpailuId);
        } else if (rasti.uusi || rasti.muokattu) {
            batch.set(docRef, { koodi: rasti.koodi.trim(), lat: rasti.lat, lon: rasti.lon })
        }
    })

    return batch.commit();
}

/**
 * Poistaa rajausehtojen mukaiset leimaukset.
 * 
 * Esim. poistaLeimauksetRajauksilla([['rasti','==','6D']], false, kilpailuId)
 * 
 * @param {string[][]} rajausehdot taulukossa muodossa [['ehto','operaattori','arvo'],...]
 * @param {boolean} poistaLeimaukset jos false, leimaukset kohdistetaan rastiin 'Tuntematon'
 * @param {string} kilpailuId 
 */
async function poistaLeimauksetRajauksilla(rajausehdot, poistaLeimaukset, kilpailuId) {
    let tuntematonRasti;

    if (!poistaLeimaukset) {
        // jos leimauksia ei poisteta kokonaan, etsitään rasti jonka koodi on 'Tuntematon'
        db.collection(`kilpailut/${kilpailuId}/rastit`).where('koodi', '==', 'Tuntematon').get().then((snapShot) => {
            if (!snapShot.empty) {
                tuntematonRasti = snapShot.docs[0].id;
            }
        })
    }

    // luodaan kysely joka hakee rajausehtoja vastaavat leimaukset
    const query = rajausehdot.reduce((acc, [ehto, op, arvo]) => {
        return acc.where(ehto, op, arvo);
    }, db.collectionGroup("leimaukset"));

    // suoritetaan hakukysely
    query.get().then((snapshot) => {
        // luodaan batchi
        const batch = db.batch();

        snapshot.forEach(doc => {
            if (!poistaLeimaukset) {
                // jos ei poisteta kokonaan, merkataan rastiksi rastin 'Tuntematon' id (tai undefined jos rastia ei ole)
                batch.set(doc.ref, { rasti: tuntematonRasti }, { merge: true })
            } else {
                const joukkueRef = db.doc(`joukkueet/${doc.get('joukkue')}`);
                
                // poistetaan leimaus
                batch.delete(doc.ref)

                // päivitetään joukkueen leimausten lukumäärää erillisessä transaktiossa
                db.runTransaction((transaction) => {
                    return transaction.get(joukkueRef).then((joukkue) => {
                        const leimauksia = joukkue.data().leimauksia - 1;

                        transaction.update(joukkueRef, { leimauksia: leimauksia }, { merge: true })
                    })
                });

            }
        })
        return batch.commit();
    })
}

async function muokkaaLeimauksetRajauksilla(rajausehdot, rasti) {
    const batch = db.batch();

    const query = rajausehdot.reduce((acc, [ehto, op, arvo]) => {
        return acc.where(ehto, op, arvo);
    }, db.collectionGroup("leimaukset"));

    query.get().then((snapshot) => {
        snapshot.forEach(doc => {
            const leimaus = doc.data()
            batch.set(doc.ref, {})
        })
    })

    return batch.commit();
}

/**
 * Apufunktio, joka luo taulukollisesta firestoren doc-objekteja tavallisia js-objekteja
 * @param {*} fsTaulukko 
 * @returns 
 */
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
    tallennaKilpailunRastit,
    haeJoukkueIdlla,
    haeJoukkueetRajauksilla,
    haeJoukkueenLeimaukset,
    tallennaJoukkueenLeimaukset,
    lisaaJoukkue,
    tallennaMuokattuJoukkue,
    poistaJoukkue
}

export default dataService