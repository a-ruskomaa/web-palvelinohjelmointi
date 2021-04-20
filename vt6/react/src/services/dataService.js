import { auth, db } from './firebase'

const PORT = window.location.hostname === 'localhost' ? ":5000" : ""
const BASE_URL = `${window.location.protocol}//${window.location.hostname}${PORT}/api`

/**
 * Hakee palvelimelta listauksen paikkakunnista.
 * @returns Palauttaa paikkakunnat taulukossa
 */
async function haePaikkakunnat() {
    try {
        // liitetään pyyntöön id-tokeni jolla käyttäjä tunnistetaan palvelimella
        const idToken = await auth.currentUser.getIdToken();

        // tehdään pyyntö
        const res = await fetch(`${BASE_URL}/paikkakunnat`, {
            method: "GET",
            headers: {
                Authorization: "Bearer " + idToken,
            },
        });
        const haePaikkakunnat = await res.json();
        return haePaikkakunnat
    } catch (err) {
        console.log(err);
        return []
    }
}

/**
 * Hakee nimeä vastaavan paikkakunnan säätiedot ja palauttaa ne taulukossa
 * @param {String} paikkakunta 
 * @returns Palauttaa objektin muodossa:
 * 
 * {
        'havainnot': {
            'ILMA': Number,
            'MAA_1': Number,
            'TIE_1': Number,
            'TUULENSUUNTA': Number,
            'KESKITUULI': Number,
            'ILMAN_KOSTEUS': Number,
            'NAKYVYYS': Number,
        },
        'ennuste': [
            {
                'aika' : String[yyyy-MM-dd hh:mm:ss],
                'lampotila: Number
            },
            {
                ...
            }
        ],
        'ennuste_pk': String,
        'havainnot_pk': String
    }
 */
async function haeSaatiedotNimella(paikkakunta) {
    try {
        // liitetään pyyntöön id-tokeni jolla käyttäjä tunnistetaan palvelimella
        const idToken = await auth.currentUser.getIdToken();

        // tehdään pyyntö
        const res = await fetch(`${BASE_URL}/paikkakunnat/${paikkakunta}`, {
            method: "GET",
            headers: {
                Authorization: "Bearer " + idToken,
            },
        });
        const saatiedot = await res.json();

        return saatiedot
    } catch (err) {
        console.log(err);
        return []
    }
}

/**
 * Hakee nimeä vastaavan paikkakunnan säätiedot ja palauttaa ne taulukossa
 * @param {String} paikkakunta 
 * @returns Palauttaa objektin muodossa:
 * 
 * {
        'havainnot': {
            'ILMA': Number,
            'MAA_1': Number,
            'TIE_1': Number,
            'TUULENSUUNTA': Number,
            'KESKITUULI': Number,
            'ILMAN_KOSTEUS': Number,
            'NAKYVYYS': Number,
        },
        'ennuste': [
            {
                'aika' : String[yyyy-MM-dd hh:mm:ss],
                'lampotila: Number
            },
            {
                ...
            }
        ],
        'ennuste_pk': String,
        'havainnot_pk': String
    }
 */
async function haeSaatiedotKoordinaateilla(lat, lon) {
    try {
        // liitetään pyyntöön id-tokeni jolla käyttäjä tunnistetaan palvelimella
        const idToken = await auth.currentUser.getIdToken();

        // tehdään pyyntö
        const res = await fetch(`${BASE_URL}/koordinaatit?lon=${lon}&lat=${lat}`, {
            method: "GET",
            headers: {
                Authorization: "Bearer " + idToken,
            },
        });
        const saatiedot = await res.json();

        return saatiedot
    } catch (err) {
        console.log(err);
        return []
    }
}


/**
 * Hakee käyttäjän hakuhistorian
 * @param {String} uid Käyttäjän yksilöivä tunniste
 * @returns Palauttaa objektin, jonka sisältämä data on muodossa:
 * 
 * {
 *      viimeksiValitut: [String, String, String],
        suosikit: {
            String: Number,
            String: Number,
            ...
        },
        karttahistoria: [
            {
                lat: Number,
                lon: Number
            },
            {
                ...
            },
            {
                ...
            }
        ],
 * }
 */
async function haeKayttajanHistoria(uid) {
    const doc = await db.doc(`kayttajat/${uid}`).get();
    if (doc.exists) {
        return doc.data();
    }
    return undefined
}

/**
 * Tallentaa käyttäjän hakuhistorian
 * @param {String} uid Käyttäjän yksilöivä tunniste
 * @param {Object} historia Objekti, joka on annettava muodossa:
 * 
 * {
 *      viimeksiValitut: [String, String, String],
        suosikit: {
            String: Number,
            String: Number,
            ...
        },
        karttahistoria: [
            {
                lat: Number,
                lon: Number
            },
            {
                ...
            },
            {
                ...
            }
        ],
 * }
 */
async function tallennaKayttajanHistoria(uid, historia) {
    console.log("historia ennen", historia);
    const filteredHistoria = JSON.parse(JSON.stringify(historia))
    console.log("historia jalkeen", filteredHistoria);
    return await db.doc(`kayttajat/${uid}`).set(filteredHistoria, {merge: true})
}

/** Funktio tekee argumenttina annetusta objektista syväkopion,
 * johon on kopioitu vain propertyt, joilla on arvo
 */
function _deepCopy(object) {
    const newObject = Object.create(Object.getPrototypeOf(object));
    Object.entries(object).forEach(([key, value]) => {
        // console.log(key, value);
        if (typeof value === "object") {
            const newProp = _deepCopy(value);
            if (newProp) {
                newObject[key] = newProp;
            }
        } else if (value !== undefined) {
            newObject[key] = value;
        }
    });
    return Object.entries(newObject).length > 0 ? newObject : undefined;
}



const dataService = {
    haePaikkakunnat,
    haeSaatiedotKoordinaateilla,
    haeSaatiedotNimella,
    haeKayttajanHistoria,
    tallennaKayttajanHistoria
}

export default dataService