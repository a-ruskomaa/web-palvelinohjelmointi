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

// Tapahtumankäsittelijät
function handleAuthStateChanged(user) {
    if (user) {
        console.log(`user ${user.email} is signed in`);
        naytaKilpailut();
        naytaTabit();
    } else {
        console.log("user logged out");
        piilotaKilpailut();
        piilotaTabit();
    }
}

function handleKilpailunVaihto(event) {
    const valittuKilpailu = event.target.value;
    paivitaKilpailunTiedot(valittuKilpailu);
}

async function handleJoukkueFormSubmit(event) {
    event.preventDefault();
    const lomake = event.target;
    const formdata = new FormData(lomake);
    const joukkue = muodostaJoukkue(formdata);
    console.log(joukkue);
    await tarkistaLomake(lomake, joukkue);

    if (!lomake.reportValidity()) {
        console.log("not valid")
        return;
    }

    try {
        await lisaaJoukkue(joukkue);
        lomake.reset();
        const sarjat = await haeSarjat(joukkue.kilpailu);
        luoJoukkuelista(sarjat);
    } catch (error) {
        console.log(error);
    }
}

function muodostaJoukkue(formdata) {
    const nimi = formdata.get("nimi").trim();
    const sarja = formdata.get("sarja");
    const kilpailu = valittuKilpailu();
    const jasenet = formdata.getAll("jasen").filter((j) => j.trim() !== "").map((j) => j.trim());
    const lisaaja = firebase.auth().currentUser.email;

    return {
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
    } else if (jasenInput.value != '' && jasenInput.value.trim() == '') {
        jasenInput.setCustomValidity("Jäsenen nimi ei voi olla tyhjä");
    }
}

async function tarkistaLomake(lomake, joukkue) {
    console.log("tarkistetaan lomake...");
    const idInput = lomake.querySelector('input[name="id"]');
    const nimiInput = lomake.querySelector('input[name="nimi"]');
    const sarjaInput = lomake.querySelector('input[name="sarja"]');
    const jasenInputs = lomake.querySelectorAll('input[name="jasen"]');
    console.log(jasenInputs)
    const nimi = "nimi"
    
    try {
        const joukkueet = await haeJoukkueetRajauksella('kilpailu', valittuKilpailu())
    
        nimiInput.setCustomValidity("");
        joukkueet.forEach((joukkue) => {
            console.log(joukkue.data().nimi.trim())
            if (joukkue.data().nimi.toLowerCase() == nimiInput.value.trim().toLowerCase() && joukkue.id != idInput.value) {
                nimiInput.setCustomValidity("Kilpailussa on jo samanniminen joukkue!");
            }
        })
    } catch (e) {
        console.log(e)
    }

    if (joukkue.jasenet.length < 2 || joukkue.jasenet.length > 5) {
        const ekaTyhja = Array.from(jasenInputs).find((jasenInput) => {
            console.log(jasenInput);
            
            return jasenInput.value.trim() == ''
        })
        ekaTyhja.setCustomValidity("Anna 2-5 jäsentä!");
    }
}

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

// Sivun osien näyttäminen
async function naytaKilpailut() {
    const sectionKilpailu = document.getElementById("section-kilpailu");
    const kilpailuSelect = sectionKilpailu.querySelector(
        'select[name="kilpailu"]'
    );

    let kilpailutRef = await db.collection("kilpailut");
    let kilpailut = await kilpailutRef.get();

    let lahin = null
    let timedelta = null
    kilpailut.forEach((kilpailu) => {
        const currentTimedelta = Math.abs(Date.parse(kilpailu.data().alkuaika) - Date.now())
        console.log(currentTimedelta)
        if (!lahin || currentTimedelta < timedelta) {
            lahin = kilpailu;
            timedelta = currentTimedelta;
        }
        const option = document.createElement("option");
        option.value = kilpailu.id;
        option.text = kilpailu.id;
        kilpailuSelect.add(option);
    });

    //TODO valitse lähin

    kilpailuSelect.addEventListener("input", handleKilpailunVaihto);
    paivitaKilpailunTiedot(valittuKilpailu());
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

    sectionTabs.setAttribute("hidden", "hidden");
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
                span.addEventListener("click", (e) => {
                    console.log(e.target.joukkueId);
                    const tabJoukkue = document.getElementById("joukkue");
                    tabJoukkue.checked = true;
                });
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
        radio.setAttribute('required', 'required')
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

function paivitaKilpailunTiedot(kilpailu) {
    const sarjat = haeSarjat(kilpailu)
        .then((sarjat) => {
            lisaaSarjatLomakkeelle(sarjat);
            luoJoukkuelista(sarjat);
        })
        .catch((error) => console.log(error));
}

function valittuKilpailu() {
    const sectionKilpailu = document.getElementById("section-kilpailu");
    const kilpailuSelect = sectionKilpailu.querySelector(
        'select[name="kilpailu"]'
    );
    return kilpailuSelect.value;
}

// Tietokantakutsut
async function haeSarjat(kilpailuId) {
    try {
        let user = firebase.auth().currentUser;
        let idToken = await user.getIdToken();

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
    await db.collection('joukkueet').add(joukkue);
}

async function haeJoukkueetRajauksella(rajausehto, arvo) {
    return await db.collection('joukkueet')
        .where(rajausehto, "==", arvo)
        .get();
}

let loginButton = document.getElementById("login-button");
let logoutButton = document.getElementById("logout-button");

const joukkueForm = document.getElementById("joukkueform");
const nimiInput = joukkueForm.querySelector('input[name="nimi"]');
const jasenInputs = joukkueForm.querySelectorAll('input[name="jasen"]');

joukkueForm.onsubmit = handleJoukkueFormSubmit;
nimiInput.addEventListener('input', tarkistaNimi)
jasenInputs.forEach((j => {
    j.addEventListener('input', tarkistaJasenenNimi)
}))

loginButton.onclick = signIn;

logoutButton.onclick = () => {
    firebase.auth().signOut();
};

firebase.auth().onAuthStateChanged(handleAuthStateChanged);

// const sarjat

if (firebase.auth().currentUser) {
    console.log("Showing hidden content");
    naytaKilpailut();
    naytaTabit();
}
