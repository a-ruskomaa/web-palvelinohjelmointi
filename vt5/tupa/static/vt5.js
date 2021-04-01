// Your web app's Firebase configuration
// For Firebase JS SDK v7.20.0 and later, measurementId is optional
var firebaseConfig = {
    apiKey: "AIzaSyASHEBQiWcYe1cwX2MLQCn9jvWo61NQvPs",
    authDomain: "ties4080-vt5.firebaseapp.com",
    projectId: "ties4080-vt5",
    storageBucket: "ties4080-vt5.appspot.com",
    messagingSenderId: "168618867241",
    appId: "1:168618867241:web:955d43a781be2ff370ba38",
    measurementId: "G-3C3P959FCR",
};

// Initialize Firebase
firebase.initializeApp(firebaseConfig);
firebase.analytics();

const BASE_URL = window.location.href;
const db = firebase.firestore();
const provider = new firebase.auth.GoogleAuthProvider();

function signIn() {
    firebase
        .auth()
        .signInWithPopup(provider)
        .then((result) => {
            /** @type {firebase.auth.OAuthCredential} */
            var credential = result.credential;
            console.log(credential);

            // This gives you a Google Access Token. You can use it to access the Google API.
            var token = credential.accessToken;
            // The signed-in user info.
            var user = result.user;
            console.log(user);
            // ...
        })
        .catch((error) => {
            console.log(error);
            // Handle Errors here.
            var errorCode = error.code;
            var errorMessage = error.message;
            // The email of the user's account used.
            var email = error.email;
            // The firebase.auth.AuthCredential type that was used.
            var credential = error.credential;
            // ...
        });
}

// tila
var valittuKilpailu = null;

// Tapahtumankäsittelijät
function handleAuthStateChanged(user) {
    if (user) {
        console.log(`user ${user.email} is signed in`);
        naytaKilpailut();
        naytaTabit();
        loginButton.setAttribute("hidden", "hidden");
        logoutButton.removeAttribute("hidden");
    } else {
        console.log("user logged out");
        piilotaKilpailut();
        piilotaTabit();
        logoutButton.setAttribute("hidden", "hidden");
        loginButton.removeAttribute("hidden");
    }
}

async function handleJoukkueSelect(event) {
    const joukkueId = event.target.joukkueId;
    const joukkue = await haeJoukkueIdlla(joukkueId);

    console.log(joukkue);

    alustaJoukkueLomake();
    taytaJoukkueLomake(joukkue);
    naytaPoistoNappi();

    const tabJoukkue = document.getElementById("joukkue");
    tabJoukkue.checked = true;
}

async function handleKilpailunVaihto(event) {
    const kilpailu = event.target.value;
    window.valittuKilpailu = kilpailu;
    vaihdaOtsikko(kilpailu);
    const sarjat = await haeSarjat(kilpailu);
    luoJoukkuelista(sarjat);
    lisaaSarjatLomakkeelle(sarjat);

    esitaytaLomakkeet(kilpailu);
}

async function esitaytaLomakkeet(kilpailu) {
    const kayttajanJoukkueet = await haeJoukkueetRajauksilla({
        lisaaja: firebase.auth().currentUser.email,
    });

    alustaJoukkueLomake();

    if (kayttajanJoukkueet.some((j) => j.kilpailu == kilpailu)) {
        naytaLeimaukset();
        lisaaLeimausInputit();
    } else {
        piilotaLeimaukset();

        if (kayttajanJoukkueet.length > 0) {
            console.log("ei joukkueita kilpailussa");
            const joukkue = kayttajanJoukkueet[0];
            joukkue.id = -1;
            taytaJoukkueLomake(joukkue);
        }
    }
}

function vaihdaOtsikko(kilpailu) {
    const heading = document.querySelector("h1");
    heading.textContent = kilpailu;
}

// Tietojen lisääminen sivulle
function luoJoukkuelista(sarjat) {
    console.log(sarjat);
    const joukkuelista = document.getElementById("joukkuelista");
    const vanhalista = joukkuelista.querySelector("ul");
    if (vanhalista) {
        joukkuelista.removeChild(vanhalista);
    }

    const ulSarjat = document.createElement("ul");

    Object.entries(sarjat).forEach(([nimi, sarja]) => {
        console.log("sarja", nimi, sarja);
        const li = document.createElement("li");
        li.textContent = nimi;

        const joukkueet = sarja.joukkueet;
        console.log("joukkueet", joukkueet);

        if (joukkueet) {
            const ulJoukkueet = document.createElement("ul");
            Object.entries(joukkueet).forEach(([joukkueId, joukkue]) => {
                const li = document.createElement("li");
                const span = document.createElement("span");
                span.textContent = joukkue.nimi;
                span.classList.add("joukkue-nimi");
                span.joukkueId = joukkueId;
                span.addEventListener("click", handleJoukkueSelect);
                li.appendChild(span);

                const jasenet = joukkue.jasenet;
                if (jasenet) {
                    const ulJasenet = document.createElement("ul");
                    jasenet.forEach((jasen) => {
                        const li = document.createElement("li");
                        li.textContent = jasen;
                        ulJasenet.appendChild(li);
                    });
                    li.appendChild(ulJasenet);
                }
                ulJoukkueet.appendChild(li);
            });
            li.appendChild(ulJoukkueet);
        }

        ulSarjat.appendChild(li);
    });

    joukkuelista.appendChild(ulSarjat);
}

function lisaaSarjatLomakkeelle(sarjat) {
    const joukkueformSarjat = document.getElementById("joukkueform-sarjat");

    joukkueformSarjat.querySelectorAll("input, label").forEach((sarja) => {
        joukkueformSarjat.removeChild(sarja);
    });

    Object.entries(sarjat).forEach(([id, _], i) => {
        const radio = document.createElement("input");
        radio.type = "radio";
        radio.name = "sarja";
        radio.value = id;
        radio.id = `joukkueform-sarjat-${id}`;
        radio.setAttribute("required", "required");
        if (i === 0) {
            radio.checked = true;
        }
        const label = document.createElement("label");
        label.setAttribute("for", radio.id);
        label.textContent = id;
        joukkueformSarjat.appendChild(radio);
        joukkueformSarjat.appendChild(label);
    });
}

async function kasitteleJoukkuelomakkeenLahetys(event) {
    event.preventDefault();
    const lomake = event.target;
    const formdata = new FormData(lomake);
    console.log("formdata", formdata);
    const errorMsg = document.getElementById("joukkueform-error-msg");
    errorMsg.textContent = "";

    try {
        const joukkue = muodostaJoukkue(formdata);
        if (
            formdata.get("poista") &&
            window.confirm(
                `Haluatko varmasti poistaa joukkueen ${formdata.get("nimi")}?`
            )
        ) {
            await poistaJoukkue(formdata.get("id"));
        } else {
            await tarkistaLomake(lomake, joukkue);

            if (!lomake.reportValidity()) {
                return;
            }

            if (joukkue.id == -1) {
                const kayttajanJoukkueet = await haeJoukkueetRajauksilla({
                    kilpailu: joukkue.kilpailu,
                    lisaaja: firebase.auth().currentUser.email,
                });

                if (kayttajanJoukkueet.length > 0) {
                    throw new Error("Voit lisätä vain yhden joukkueen!");
                }

                console.log("kayttajan joukkueet", kayttajanJoukkueet);

                await lisaaJoukkue(joukkue);
            } else {
                await tallennaMuokattuJoukkue(joukkue);
            }
        }

        const sarjat = await haeSarjat(joukkue.kilpailu);
        luoJoukkuelista(sarjat);
        esitaytaLomakkeet(joukkue.kilpailu);
    } catch (error) {
        console.log(error.message);
        errorMsg.textContent = `Tallennuksessa tapahtui virhe:\n${error.message}`;
    }
}

async function lisaaLeimausInputit() {
    const rastit = await haeRastit(window.valittuKilpailu);
    const leimausForm = document.getElementById("leimausform");
    console.log("rastit", rastit);

    const kayttajanJoukkueet = await haeJoukkueetRajauksilla({
        kilpailu: window.valittuKilpailu,
        lisaaja: firebase.auth().currentUser.email,
    });

    const joukkueKilpailussa =
        kayttajanJoukkueet.length > 0 ? kayttajanJoukkueet[0] : null;

    const joukkueenLeimaukset = await haeJoukkueenLeimaukset(
        joukkueKilpailussa.id
    );

    joukkueenLeimaukset.forEach((leimaus) => {
        const leimausDiv = luoLeimausInput(luoRastiOptiot());
        leimausDiv.leimausId = leimaus.id;
        leimausDiv.aikaleima.value = leimaus.aika;
        leimausDiv.rastiSelect.value = leimaus.rasti;
        leimausDiv.muokattu = false;
        leimausDiv.uusi = false;
        leimausDiv.addEventListener("change", handleLeimausChange);
        leimausForm.appendChild(leimausDiv);
    });

    const uusiKentta = luoUusiLeimausInput();
    leimausForm.appendChild(uusiKentta);

    function luoRastiOptiot() {
        return rastit.map((rasti) => {
            const option = document.createElement("option");
            option.value = rasti.id;
            option.text = rasti.koodi;
            return option;
        });
    }

    function luoUusiLeimausInput() {
        const leimausDiv = luoLeimausInput(luoRastiOptiot());
        leimausDiv.uusi = true;
        leimausDiv.muokattu = false;
        leimausDiv.addEventListener("change", handleLeimausChange);
        return leimausDiv;
    }

    function handleLeimausChange(event) {
        const leimausDiv = event.currentTarget;

        if (leimausDiv.uusi && !leimausDiv.muokattu) {
            const uusiKentta = luoUusiLeimausInput();
            leimausForm.appendChild(uusiKentta);
        }
        leimausDiv.muokattu = true;
    }

    function luoLeimausInput(rastiOptiot) {
        const div = document.createElement("div");
        const aikaleima = document.createElement("input");
        aikaleima.type = "text";

        const rastiSelect = document.createElement("select");

        rastiOptiot.forEach((option) => {
            rastiSelect.add(option);
        });

        const poistoCheckbox = document.createElement("input");
        poistoCheckbox.type = "checkbox";

        div.appendChild(aikaleima);
        div.aikaleima = aikaleima;
        div.appendChild(rastiSelect);
        div.rastiSelect = rastiSelect;
        div.appendChild(poistoCheckbox);
        div.poistoCheckbox = poistoCheckbox;

        return div;
    }
}

function kasitteleLeimausLomakkeenLahetys(event) {
    event.preventDefault();
    const leimausForm = event.target;

    const leimausInputit = leimausForm.childNodes

    const muokatutLeimaukset = []
    const uudetLeimaukset = []

}

function tarkistaAikaleima(event) {
    
}

function taytaJoukkueLomake(joukkue) {
    const lomake = document.getElementById("joukkueform");
    const idInput = lomake.querySelector('input[name="id"]');
    const nimiInput = lomake.querySelector('input[name="nimi"]');
    const sarjaInput = lomake.querySelectorAll('input[name="sarja"]');
    const jasenInputs = lomake.querySelectorAll('input[name="jasen"]');

    idInput.value = joukkue.id;
    nimiInput.value = joukkue.nimi;

    sarjaInput.forEach((sarjaInput) => {
        if (joukkue.sarja == sarjaInput.value) {
            sarjaInput.checked = true;
        }
    });

    joukkue.jasenet.forEach((jasen, i) => {
        jasenInputs[i].value = jasen;
    });
}

function alustaJoukkueLomake() {
    const lomake = document.getElementById("joukkueform");
    const errorMsg = document.getElementById("joukkueform-error-msg");
    errorMsg.textContent = "";
    lomake.reset();
    const sarjaInput = lomake.querySelectorAll('input[name="sarja"]');
    if (sarjaInput.length > 0) {
        sarjaInput[0].checked = true;
    }
}

/**
 *
 * @param {FormData} formdata
 * @returns
 */
function muodostaJoukkue(formdata) {
    const id = formdata.get("id");
    const nimi = formdata.get("nimi").trim();
    const sarja = formdata.get("sarja");
    const kilpailu = window.valittuKilpailu;
    const jasenet = formdata
        .getAll("jasen")
        .filter((j) => j.trim() !== "")
        .map((j) => j.trim())
        .sort((a, b) => a.localeCompare(b));
    const lisaaja = firebase.auth().currentUser.email;

    return {
        id,
        nimi,
        sarja,
        kilpailu,
        jasenet,
        lisaaja,
    };
}

function tarkistaNimi(event) {
    if (event.target.value != "") {
        nimiInput.setCustomValidity("");
    }
}

function tarkistaJasenenNimi(event) {
    const jasenInput = event.target;

    jasenInput.setCustomValidity("");

    if (jasenInput.value.match(/\d/)) {
        jasenInput.setCustomValidity("Jäsenen nimessä ei saa olla numeroita");
    } else if (jasenInput.value != "" && jasenInput.value.trim() == "") {
        jasenInput.setCustomValidity("Jäsenen nimi ei voi olla tyhjä");
    }
}

async function tarkistaLomake(lomake, joukkue) {
    console.log("tarkistetaan lomake...");
    const idInput = lomake.querySelector('input[name="id"]');
    const nimiInput = lomake.querySelector('input[name="nimi"]');
    const sarjaInput = lomake.querySelectorAll('input[name="sarja"]');
    const jasenInputs = lomake.querySelectorAll('input[name="jasen"]');
    console.log("jaseninputs", jasenInputs);
    const nimi = "nimi";

    try {
        const kilpailunJoukkueet = await haeJoukkueetRajauksilla({
            kilpailu: window.valittuKilpailu,
        });

        console.log("kilpailun joukkueet", kilpailunJoukkueet);
        console.log(nimiInput.value.trim().toLowerCase());

        nimiInput.setCustomValidity("");
        if (
            kilpailunJoukkueet.some((joukkue) => {
                return (
                    joukkue.nimi.toLowerCase() ==
                        nimiInput.value.trim().toLowerCase() &&
                    joukkue.id != idInput.value
                );
            })
        ) {
            nimiInput.setCustomValidity(
                "Kilpailussa on jo samanniminen joukkue!"
            );
        }
    } catch (e) {
        console.log(e);
    }

    if (joukkue.jasenet.length < 2 || joukkue.jasenet.length > 5) {
        const ekaTyhja = Array.from(jasenInputs).find((jasenInput) => {
            console.log(jasenInput);

            return jasenInput.value.trim() == "";
        });
        ekaTyhja.setCustomValidity("Anna 2-5 jäsentä!");
    }
}

// Sivun osien näyttäminen
function naytaPoistoNappi() {
    const poistoNappi = document.getElementById("joukkueform-poista-container");
    poistoNappi.removeAttribute("hidden");
}

function piilotaPoistoNappi() {
    const poistoNappi = document.getElementById("joukkueform-poista-container");
    poistoNappi.setAttribute("hidden", "hidden");
}

async function naytaLeimaukset() {
    const leimausInput = document.getElementById("leimaukset");
    const leimausSection = leimausInput.parentElement;

    leimausSection.removeAttribute("hidden");
}

function piilotaLeimaukset() {
    const leimausInput = document.getElementById("leimaukset");
    const leimausSection = leimausInput.parentElement;

    leimausSection.setAttribute("hidden", "hidden");
}

async function naytaKilpailut() {
    const sectionKilpailu = document.getElementById("section-kilpailu");
    const kilpailuSelect = sectionKilpailu.querySelector(
        'select[name="kilpailu"]'
    );

    const kilpailut = await haeKaikkiKilpailut();

    let lahin = null;
    let timedelta = null;
    kilpailut.forEach((kilpailu) => {
        const currentTimedelta = Math.abs(
            Date.parse(kilpailu.alkuaika) - Date.now()
        );
        console.log(currentTimedelta);
        if (!lahin || currentTimedelta < timedelta) {
            lahin = kilpailu;
            timedelta = currentTimedelta;
        }
        const option = document.createElement("option");
        option.value = kilpailu.id;
        option.text = kilpailu.id;
        kilpailuSelect.add(option);
    });

    console.log("lähin", lahin);
    kilpailuSelect.value = lahin.id;
    kilpailuSelect.dispatchEvent(new Event("change"));
    sectionKilpailu.removeAttribute("hidden");
}

function piilotaKilpailut() {
    const sectionKilpailu = document.getElementById("section-kilpailu");
    const kilpailuSelect = sectionKilpailu.querySelector(
        'select[name="kilpailu"]'
    );

    while (kilpailuSelect.childElementCount > 0) {
        kilpailuSelect.removeChild(kilpailuSelect.firstChild);
    }

    sectionKilpailu.setAttribute("hidden", "hidden");
}

function naytaTabit() {
    const sectionTabs = document.getElementById("section-tabs");

    sectionTabs.removeAttribute("hidden");
}

function piilotaTabit() {
    const sectionTabs = document.getElementById("section-tabs");
    const lomake = document.getElementById("joukkueform");
    alustaJoukkueLomake();
    piilotaPoistoNappi();
    sectionTabs.setAttribute("hidden", "hidden");
}

// Tietokantakutsut
async function haeSarjat(kilpailuId) {
    try {
        const idToken = await firebase.auth().currentUser.getIdToken();

        const res = await fetch(`${BASE_URL}/kilpailut/${kilpailuId}/sarjat`, {
            method: "GET",
            headers: {
                Authorization: "Bearer " + idToken,
            },
        });
        return await res.json();
    } catch (err) {
        console.log(err);
    }
}

async function lisaaJoukkue(joukkue) {
    await db.collection("joukkueet").add(joukkue);
}

async function tallennaMuokattuJoukkue(joukkue) {
    console.log("tallennetaan muokattu", joukkue);
    await db.doc(`joukkueet/${joukkue.id}`).set(joukkue);
}

async function poistaJoukkue(joukkueId) {
    await db.doc(`joukkueet/${joukkueId}`).delete();
}

/**
 *
 * @param {object} rajausehdot
 * @returns
 */
async function haeJoukkueetRajauksilla(rajausehdot) {
    const query = Object.entries(rajausehdot).reduce((acc, [ehto, arvo]) => {
        return acc.where(ehto, "==", arvo);
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
    const fsKilpailut = await db.collection("kilpailut").get();
    return luoTaulukko(fsKilpailut);
}

async function haeRastit(kilpailuId) {
    const fsRastit = await db
        .collection(`kilpailut/${kilpailuId}/rastit`)
        .get();
    return luoTaulukko(fsRastit);
}

async function haeJoukkueenLeimaukset(joukkueId) {
    const fsLeimaukset = await db
        .collection(`joukkue/${joukkueId}/leimaukset`)
        .get();
    return luoTaulukko(fsLeimaukset);
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

firebase.auth().onAuthStateChanged(handleAuthStateChanged);

const kilpailuSelect = document.getElementById("kilpailu-select");
kilpailuSelect.addEventListener("change", handleKilpailunVaihto);

let loginButton = document.getElementById("login-button");
let logoutButton = document.getElementById("logout-button");

const joukkueForm = document.getElementById("joukkueform");
const nimiInput = joukkueForm.querySelector('input[name="nimi"]');
const jasenInputs = joukkueForm.querySelectorAll('input[name="jasen"]');

joukkueForm.onsubmit = kasitteleJoukkuelomakkeenLahetys;
nimiInput.addEventListener("input", tarkistaNimi);
jasenInputs.forEach((j) => {
    j.addEventListener("input", tarkistaJasenenNimi);
});

loginButton.onclick = () => {
    signIn();
};

logoutButton.onclick = () => {
    firebase.auth().signOut();
};

// const sarjat

if (firebase.auth().currentUser) {
    console.log("Showing hidden content");
    naytaKilpailut();
    naytaTabit();
}
