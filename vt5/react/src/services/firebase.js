import firebase from 'firebase';

const firebaseConfig = {
    apiKey: "AIzaSyASHEBQiWcYe1cwX2MLQCn9jvWo61NQvPs",
    authDomain: "ties4080-vt5.firebaseapp.com",
    projectId: "ties4080-vt5",
    storageBucket: "ties4080-vt5.appspot.com",
    messagingSenderId: "168618867241",
    appId: "1:168618867241:web:955d43a781be2ff370ba38",
    measurementId: "G-3C3P959FCR",
};

firebase.initializeApp(firebaseConfig);
firebase.analytics();

const db = firebase.firestore();
const provider = new firebase.auth.GoogleAuthProvider();
const auth = firebase.auth();

export {
    db,
    provider,
    auth
}
