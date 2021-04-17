import firebase from 'firebase/app';
import 'firebase/auth'
import 'firebase/firestore'

const firebaseConfig = {
  apiKey: "AIzaSyCxsJpLkQpnauJ5w9gGostlAOVlKaIIIaE",
  authDomain: "ties4080-vt6-310509.firebaseapp.com",
  projectId: "ties4080-vt6-310509",
  storageBucket: "ties4080-vt6-310509.appspot.com",
  messagingSenderId: "365290023294",
  appId: "1:365290023294:web:3dcce74827ef5813c0ab2f"
};

firebase.initializeApp(firebaseConfig);

var db = firebase.firestore();
// if (window.location.hostname === "localhost") {
//   console.log("using emulator")
//   db.useEmulator("localhost", 8888);
// }
const provider = new firebase.auth.GoogleAuthProvider();
const auth = firebase.auth();

export {
    db,
    provider,
    auth
}
