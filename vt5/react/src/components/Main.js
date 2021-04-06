import React, { useEffect, useState } from "react";
import dataService from "services/dataService";
import JoukkueTab from "./tabs/joukkue/JoukkueTab";
import LeimausTab from "./tabs/leimaus/LeimausTab";
import ListausTab from "./tabs/listaus/ListausTab";
import RastiTab from "./tabs/rasti/RastiTab";
import { Tab, Tabs, TabList, TabPanel } from "react-tabs";
import { auth } from 'services/firebase'
import { useAuthState } from 'react-firebase-hooks/auth';
import "react-tabs/style/react-tabs.css";
import "./Main.css";
import DummyTab from "./tabs/DummyTab";

// keskeisin tilaa ylläpitävä komponentti, jonka osina
// renderöidään mm. sovelluksen välilehdet
const Main = ({ valittuKilpailu }) => {
    const [user, loading, error] = useAuthState(auth);
    // valittu välilehti
    const [tabIndex, setTabIndex] = useState(0);
    // onko sisällön lataus kesken
    const [loadingSarjat, setLoadingSarjat] = useState(false)
    const [loadingRastit, setLoadingRastit] = useState(false)
    // kilpailun sarjat, rastit, joukkueet yms.
    const [kilpailunSarjat, setKilpailunSarjat] = useState([]);
    const [kilpailunRastit, setKilpailunRastit] = useState([]);
    const [kilpailunJoukkueet, setKilpailunJoukkueet] = useState([]);
    const [valittuJoukkue, setValittuJoukkue] = useState();
    const [kayttajanJoukkue, setKayttajanJoukkue] = useState();

    // jos valittu kilpailu vaihtuu, alustetaan komponentin tila
    useEffect(() => {
        if (valittuKilpailu) {
            paivitaTila();
        }
        // tätä kutsutaan kun komponentti "unmountataan"
        return (() => {
            setLoadingSarjat(false);
            setLoadingRastit(false);
            setKayttajanJoukkue();
        })
    }, [valittuKilpailu]);

    // kutsutaan kun joukkuelistauksesta valitaan joukkue muokattavaksi
    const handleJoukkueSelect = (id) => {
        if (id) {
            // valitaan id:tä vastaava joukkue ja avataan muokkausvälilehti
            setValittuJoukkue(kilpailunJoukkueet.find(j => j.id === id));
            setTabIndex(0);
        } else {
            setValittuJoukkue();
        }
    };

    // kutsutaan kun on muokattu tietokannassa olevaa dataa
    const dataUpdated = () => {
        paivitaTila();
    }

    // alustaa komponentin tilan hakemalla valittuun kilpailuun kuuluvat
    // sarjat, rastit ja joukkueet
    const paivitaTila = () => {
        setLoadingSarjat(true)
        setLoadingRastit(true)
        // haetaan sarjat
        dataService.haeSarjat(valittuKilpailu.id).then((sarjat) => {
            setKilpailunSarjat(sarjat);
            // erotetaan sarjojen joukkueet omaan taulukkoonsa
            const kaikkiJoukkueet = sarjat.flatMap(sarja => sarja.joukkueet)
            setKilpailunJoukkueet(kaikkiJoukkueet);
            // etsitään kilpailun joukkueista käyttäjän lisäämää joukkuetta
            const kayttajanJoukkue = kaikkiJoukkueet.find(joukkue => joukkue.lisaaja === user.email)
            setKayttajanJoukkue(kayttajanJoukkue);
            // nollataan valittu joukkue
            setValittuJoukkue();
            
            setLoadingSarjat(false)
        });
        // haetaan kilpailuun kuuluvat rastit
        dataService.haeRastit(valittuKilpailu.id).then((rastit) => {
            setKilpailunRastit(rastit)
            setLoadingRastit(false)
        })
    }

    return (
        <main id="tabs-content">
            {/* Renderöidään myös avaamattomat tabit jotta tilaa ei nollata välilehteä vaihtaessa */}
            <Tabs forceRenderTabPanel={true} selectedIndex={tabIndex} onSelect={index => setTabIndex(index)}>
                <TabList>
                    <Tab>Joukkue</Tab>
                    <Tab>Joukkueet</Tab>
                    <Tab disabled={!kayttajanJoukkue}>Rastileimaukset</Tab>
                    <Tab>Rastit</Tab>
                </TabList>

                <TabPanel>
                    { loadingSarjat ?
                        // näytetään latauksen ajan viesti
                        <DummyTab viesti="Ladataan tietoja..."/> :
                        !valittuKilpailu ?
                            // näytetään jos ei kilpailua valittuna
                            <DummyTab viesti="Valitse kilpailu!"/> :
                            kayttajanJoukkue && !valittuJoukkue ?
                                // jos käyttäjällä on jo joukkue eikä sitä ole valittu muokattavaksi
                                <DummyTab viesti="Voit lisätä vain yhden joukkueen!"/> :
                                // renderöidään lomake uuden joukkuen lisäämiseksi tai vanhan muokkaamiseksi
                                <JoukkueTab
                                kilpailuId={valittuKilpailu.id}
                                sarjat={kilpailunSarjat}
                                valittuJoukkue={valittuJoukkue}
                                kayttajanJoukkue={kayttajanJoukkue}
                                dataUpdated={dataUpdated}
                                handleJoukkueSelect={handleJoukkueSelect}
                                /> }
                </TabPanel>
                <TabPanel>
                    { loadingSarjat ?
                        // näytetään latauksen ajan viesti
                        <DummyTab viesti="Ladataan tietoja..."/> :
                         !valittuKilpailu ?
                            // näytetään jos ei kilpailua valittuna
                            <DummyTab viesti="Valitse kilpailu!"/> :
                            // renderöidään sarjalistaus
                            <ListausTab
                                sarjat={kilpailunSarjat}
                                handleJoukkueSelect={handleJoukkueSelect}
                            /> }
                </TabPanel>
                <TabPanel>
                    { loadingRastit ?
                        // näytetään latauksen ajan viesti
                        <DummyTab viesti="Ladataan tietoja..."/> :
                         !valittuKilpailu ?
                            // näytetään jos ei kilpailua valittuna
                            <DummyTab viesti="Valitse kilpailu!"/> :
                            kilpailunRastit.length === 0 ?
                                // näytetään jos kilpailussa ei ole rasteja
                                <DummyTab viesti="Kilpailussa ei ole rasteja!"/> :
                                !kayttajanJoukkue ?
                                    // näytetään jos käyttäjällä ei ole joukkuetta kilpailussa
                                    <DummyTab viesti="Ei joukkuetta kilpailussa!"/> :
                                    // renderöidään välilehti leimausten muokkaamiseksi
                                    <LeimausTab
                                        kayttajanJoukkue={kayttajanJoukkue}
                                        kilpailunRastit={kilpailunRastit}
                                        valittuKilpailu={valittuKilpailu}
                                        dataUpdated={dataUpdated}/> }
                </TabPanel>
                <TabPanel>
                    { loadingRastit ?
                        // näytetään latauksen ajan viesti
                        <DummyTab viesti="Ladataan tietoja..."/> :
                         !valittuKilpailu ?
                            // näytetään jos ei kilpailua valittuna
                            <DummyTab viesti="Valitse kilpailu!"/> :
                                // renderöidään välilehti rastien muokkaamiseksi
                                <RastiTab
                                    kilpailunRastit={kilpailunRastit}
                                    valittuKilpailu={valittuKilpailu}
                                    dataUpdated={dataUpdated}/> }
                </TabPanel>
            </Tabs>
        </main>
    );
};

export default Main;
