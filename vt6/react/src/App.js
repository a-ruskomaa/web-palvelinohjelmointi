import "./App.css";
import Main from "./components/Main";
import Button from "./components/Button";
import { signIn, signOut } from "./services/authService";
import { useAuthState } from "react-firebase-hooks/auth";
import { auth } from "./services/firebase";

function App() {
  const [user, loading, error] = useAuthState(auth);
  
    // Näytetään sovellus vain kirjautuneelle käyttäjälle
    return user ? (
        <div className="App">
            <h1>Sääsovellus</h1>
            <Button className="signInOutButton" onClickHandler={signOut} text="Kirjaudu ulos" />
            <Main user={user}/>
        </div>
    ) : (
        <div className="App">
            <h1>Sääsovellus</h1>
            <Button className="signInOutButton" onClickHandler={signIn} text="Kirjaudu sisään" />
        </div>
    );
}

export default App;
