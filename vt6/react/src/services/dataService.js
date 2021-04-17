import { auth, db } from './firebase'

const PORT = window.location.hostname === 'localhost' ? ":5000" : ""
const BASE_URL = `${window.location.protocol}//${window.location.hostname}${PORT}/api`

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

async function haeSaatiedotKoordinaateilla(lat, lon) {
    // const params = new URLSearchParams(["lat", lat], ["lon", lon])
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


async function haeKayttajanHistoria(user) {
    return await db.doc(`kayttajat/${user.uid}`).get()
}


async function tallennaKayttajanHistoria(user, historia) {
    return await db.doc(`kayttajat/${user.uid}`).set(historia)
}



const dataService = {
    haePaikkakunnat,
    haeSaatiedotKoordinaateilla,
    haeSaatiedotNimella,
    haeKayttajanHistoria,
    tallennaKayttajanHistoria
}

export default dataService