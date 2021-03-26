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
        showKilpailut();
        showTabs();
    } else {
        console.log("user logged out");
        hideKilpailut();
        hideTabs();
    }
}

function handleKilpailunVaihto(event) {
    const valittuKilpailu = event.target.value
    paivitaKilpailunTiedot(valittuKilpailu)
}

async function handleJoukkueFormSubmit(event) {
    event.preventDefault();
    let formdata = new FormData(event.target);
    const nimi = formdata.get('nimi')
    const sarja = formdata.get('sarja')
    const jasenet = formdata.getAll('jasen').filter(jasen => jasen !== '')
    const lisaaja = firebase.auth().currentUser.email

    const joukkue = {
        nimi,
        sarja,
        jasenet,
        lisaaja
    }

    const valittuKilpailu = haeValittuKilpailu()

    console.log(joukkue)
    try{
        await lisaaJoukkue(joukkue)
        const sarjat = await haeSarjat(valittuKilpailu)
        luoJoukkuelista(sarjat)
    } catch(error) {
        console.log(error)
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
async function showKilpailut() {
    const sectionKilpailu = document.getElementById("section-kilpailu");
    const kilpailuSelect = sectionKilpailu.querySelector(
        'select[name="kilpailu"]'
    );

    let kilpailutRef = await db.collection("kilpailut");
    let kilpailut = await kilpailutRef.get();

    kilpailut.forEach((kilpailu) => {
        const option = document.createElement("option");
        option.value = kilpailu.id;
        option.text = kilpailu.id;
        kilpailuSelect.add(option);
    });

    kilpailuSelect.addEventListener("input", handleKilpailunVaihto);
    paivitaKilpailunTiedot(haeValittuKilpailu())
    sectionKilpailu.removeAttribute("hidden");
}

function hideKilpailut() {
    const sectionKilpailu = document.getElementById("section-kilpailu");
    const kilpailuSelect = sectionKilpailu.querySelector('select[name="kilpailu"]');

    while (kilpailuSelect.childElementCount > 0) {
        kilpailuSelect.removeChild(kilpailuSelect.firstChild);
    }

    sectionKilpailu.setAttribute("hidden", "hidden");
}

function showTabs() {
    const sectionTabs = document.getElementById("section-tabs");

    sectionTabs.removeAttribute("hidden");
}

function hideTabs() {
    const sectionTabs = document.getElementById("section-tabs");

    sectionTabs.setAttribute("hidden", "hidden");
}

// Tietojen lisääminen sivulle
function luoJoukkuelista(sarjat) {
    console.log(sarjat)
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
                li.textContent = joukkue.nimi;

                const jasenet = joukkue.jasenet
                if (jasenet) {
                    const ulJasenet = document.createElement("ul");
                    jasenet.forEach((jasen) => {
                        console.log('jasen', jasen)
                        const li = document.createElement("li");
                        li.textContent = jasen;
                        ulJasenet.appendChild(li)
                    })
                    li.appendChild(ulJasenet)
                }
                ulJoukkueet.appendChild(li);
            });
            li.appendChild(ulJoukkueet)
        }

        ulSarjat.appendChild(li);
    });

    joukkuelista.appendChild(ulSarjat);
}

function lisaaSarjatLomakkeelle(sarjat) {
    const joukkueformSarjat = document.getElementById("joukkueform-sarjat");

    joukkueformSarjat.querySelectorAll("input, label")
                        .forEach((sarja) => {
        joukkueformSarjat.removeChild(sarja)
    })

    Object.entries(sarjat).forEach(([id, _]) => {
        const radio = document.createElement("input");
        radio.type = "radio";
        radio.name = "sarja";
        radio.value = id
        radio.id = `joukkueform-sarjat-${id}`
        const label = document.createElement('label')
        label.setAttribute('for', radio.id)
        label.textContent = id
        joukkueformSarjat.appendChild(radio);
        joukkueformSarjat.appendChild(label)
    })
}

function paivitaKilpailunTiedot(kilpailu) {

    const sarjat = haeSarjat(kilpailu).then((sarjat) =>
    {
        lisaaSarjatLomakkeelle(sarjat)
        luoJoukkuelista(sarjat)
    }).catch((error) => console.log(error))
}

function haeValittuKilpailu() {
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
    await db.collection(`kilpailut/${valittuKilpailu}/sarjat/${sarja}/joukkueet`).add(joukkue)
}

window.onload = () => {
    console.log("Window loaded");

    let loginButton = document.getElementById("login-button");
    let logoutButton = document.getElementById("logout-button");

    let joukkueForm = document.getElementById("joukkueform");

    joukkueForm.onsubmit = handleJoukkueFormSubmit;

    loginButton.onclick = signIn;

    logoutButton.onclick = () => {
        firebase.auth().signOut();
    };

    firebase.auth().onAuthStateChanged(handleAuthStateChanged);

    // const sarjat 
    
    if (firebase.auth().currentUser) {
        console.log("Showing hidden content");
        showKilpailut();
        showTabs();
    }
};
