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

const db = firebase.firestore();
const provider = new firebase.auth.GoogleAuthProvider();

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

async function showKilpailut() {
    const section_kilpailu = document.getElementById("section-kilpailu");
    const kilpailu_select = section_kilpailu.querySelector(
        'select[name="kilpailu"]'
    );

    let kilpailut_ref = await db.collection("kilpailut");
    let kilpailut = await kilpailut_ref.get();

    kilpailut.forEach((kilpailu) => {
        // console.log('kilpailu', kilpailu);
        // console.log('kilpailu', kilpailu.data());
        // console.log('sarjat', kilpailu.ref.collection('sarjat').get());
        const option = document.createElement("option");
        option.value = kilpailu.id;
        option.text = kilpailu.id;
        kilpailu_select.add(option);
    });

    kilpailu_select.addEventListener("input", handleKilpailuChange);
    section_kilpailu.removeAttribute("hidden");
}

function hideKilpailut() {
    const section_kilpailu = document.getElementById("section-kilpailu");
    const kilpailu_select = section.querySelector('select[name="kilpailu"]');

    while (kilpailu_select.childElementCount > 0) {
        kilpailu_select.removeChild(kilpailu_select.firstChild);
    }

    section_kilpailu.setAttribute("hidden", "hidden");
}

function showTabs() {
    const section_tabs = document.getElementById("section-tabs");

    section_tabs.removeAttribute("hidden");
}

function hideTabs() {
    const section_tabs = document.getElementById("section-tabs");

    section_tabs.setAttribute("hidden", "hidden");
}

function populateJoukkuelista(snapshot) {
    const joukkuelista = document.getElementById("joukkuelista");
    const vanhalista = joukkuelista.querySelector("ul");
    if (vanhalista) {
        joukkuelista.removeChild(vanhalista);
    }

    const uusilista = document.createElement("ul");

    snapshot.forEach(async (sarja) => {
        console.log("sarja", sarja);
        const li = document.createElement("li");
        li.textContent = sarja.id;

        const ul = document.createElement("ul");
        const joukkueet = await sarja.ref.collection("joukkueet").get();
        console.log("joukkueet", joukkueet);
        joukkueet.forEach((joukkue) => {
            const li = document.createElement("li");
            li.textContent = joukkue.data().nimi;
            // TODO tähän joukkueen jäsenet
            ul.appendChild(li);
        });
        uusilista.appendChild(li);
    });

    joukkuelista.appendChild(uusilista);
}

function handleKilpailuChange() {
    const section_kilpailu = document.getElementById("section-kilpailu");
    const kilpailu_select = section_kilpailu.querySelector(
        'select[name="kilpailu"]'
    );
    const valittu_kilpailu = kilpailu_select.value;

    db.collection("kilpailut")
        .doc(valittu_kilpailu)
        .collection("sarjat")
        .onSnapshot(populateJoukkuelista);
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

window.onload = () => {
    console.log("Window loaded");

    let login_button = document.getElementById("login-button");
    let logout_button = document.getElementById("logout-button");
    let server_button = document.getElementById("server-button");

    login_button.onclick = signIn;

    logout_button.onclick = () => {
        firebase.auth().signOut();
    };

    server_button.onclick = async () => {
        let user = firebase.auth().currentUser;
        let id_token = await user.getIdToken();
        console.log(id_token);

        fetch("http://localhost:5000/auth_test", {
            method: "GET",
            headers: {
                Authorization: "Bearer " + id_token,
            },
        })
            .then((res) => res.json())
            .then((data) => {
                console.log(data);
            })
            .catch((err) => {
                console.log(err);
            });
    };

    firebase.auth().onAuthStateChanged(handleAuthStateChanged);

    if (firebase.auth().currentUser) {
        console.log("Showing hidden content");
        showKilpailut();
        showTabs();
    }
};
