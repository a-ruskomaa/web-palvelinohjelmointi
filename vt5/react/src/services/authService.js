import { auth, provider } from './firebase'

function signIn() {
    auth.signInWithPopup(provider)
        .then((result) => {
            /** @type {firebase.auth.OAuthCredential} */
            var user = result.user;
            console.log(user);
        })
        .catch((error) => {
            console.log(error);
        });
}

function signOut() {
    auth.signOut();
}

export {
    signIn,
    signOut
}