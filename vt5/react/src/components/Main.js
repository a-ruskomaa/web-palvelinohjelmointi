import React, { useEffect, useState } from "react";
import dataService from "services/dataService";
import JoukkueTab from "./tabs/joukkue/JoukkueTab";
import LeimausTab from "./tabs/leimaus/LeimausTab";
import ListausTab from "./tabs/listaus/ListausTab";
import { Tab, Tabs, TabList, TabPanel } from "react-tabs";
import { auth } from 'services/firebase'
import { useAuthState } from 'react-firebase-hooks/auth';
import "react-tabs/style/react-tabs.css";
import "./Main.css";
import DummyTab from "./tabs/DummyTab";

const Main = ({ kilpailuId }) => {
    const [user, loading, error] = useAuthState(auth);
    const [loadingSarjat, setLoadingSarjat] = useState(false)
    const [loadingRastit, setLoadingRastit] = useState(false)
    const [kilpailunSarjat, setKilpailunSarjat] = useState([]);
    const [valittuJoukkue, setValittuJoukkue] = useState();
    const [kayttajanJoukkue, setKayttajanJoukkue] = useState();
    const [kilpailunJoukkueet, setKilpailunJoukkueet] = useState([]);
    const [kilpailunRastit, setKilpailunRastit] = useState([]);
    const [tabIndex, setTabIndex] = useState(0);

    useEffect(() => {
        if (kilpailuId) {
            paivitaTila();
        }
        return (() => {
            setLoadingSarjat(false);
            setLoadingRastit(false);
            setKayttajanJoukkue();
            console.log("Main cleanup");
        })
    }, [kilpailuId]);

    const handleJoukkueSelect = (id) => {
        if (id) {
            setValittuJoukkue(kilpailunJoukkueet.find(j => j.id === id));
            setTabIndex(0);
        } else {
            setValittuJoukkue();
        }
    };

    const dataUpdated = () => {
        paivitaTila();
    }

    const paivitaTila = () => {
        setLoadingSarjat(true)
        setLoadingRastit(true)
        dataService.haeSarjat(kilpailuId).then((sarjat) => {
            setKilpailunSarjat(sarjat);
            const kaikkiJoukkueet = sarjat.flatMap(sarja => sarja.joukkueet)
            const kayttajanJoukkue = kaikkiJoukkueet.find(joukkue => joukkue.lisaaja === user.email)
            setKilpailunJoukkueet(kaikkiJoukkueet);
            setValittuJoukkue();
            setKayttajanJoukkue(kayttajanJoukkue);
            
            console.log(`${kilpailuId} sarjat:`, sarjat)
            console.log('kilpailun joukkueet:', kaikkiJoukkueet)
            console.log('kayttajan joukkue:', kayttajanJoukkue)
            setLoadingSarjat(false)
        });
        dataService.haeRastit(kilpailuId).then((rastit) => {
            setKilpailunRastit(rastit)
            setLoadingRastit(false)
        })
    }

    // console.log("valittuJoukkue", valittuJoukkue);

    return (
        <main id="tabs-content">
            <Tabs forceRenderTabPanel={true} selectedIndex={tabIndex} onSelect={index => setTabIndex(index)}>
                <TabList>
                    <Tab>Joukkue</Tab>
                    <Tab>Joukkueet</Tab>
                    <Tab>Rastileimaukset</Tab>
                </TabList>

                <TabPanel>
                    { loadingSarjat ?
                        <DummyTab viesti="Ladataan tietoja..."/> :
                        !kilpailuId ?
                            <DummyTab viesti="Valitse kilpailu!"/> :
                            kayttajanJoukkue && !valittuJoukkue ?
                                <DummyTab viesti="Voit lisätä vain yhden joukkueen!"/> :
                                <JoukkueTab
                                kilpailuId={kilpailuId}
                                sarjat={kilpailunSarjat}
                                valittuJoukkue={valittuJoukkue}
                                kayttajanJoukkue={kayttajanJoukkue}
                                dataUpdated={dataUpdated}
                                handleJoukkueSelect={handleJoukkueSelect}
                                /> }
                </TabPanel>
                <TabPanel>
                    { loadingSarjat ?
                        <DummyTab viesti="Ladataan tietoja..."/> :
                         !kilpailuId ?
                            <DummyTab viesti="Valitse kilpailu!"/> :
                            <ListausTab
                                sarjat={kilpailunSarjat}
                                handleJoukkueSelect={handleJoukkueSelect}
                            /> }
                </TabPanel>
                <TabPanel>
                    { loadingRastit ?
                        <DummyTab viesti="Ladataan tietoja..."/> :
                         !kilpailuId ?
                        <DummyTab viesti="Valitse kilpailu!"/> :
                        kilpailunRastit.length === 0 ?
                            <DummyTab viesti="Kilpailussa ei ole rasteja!"/> :
                            !kayttajanJoukkue ?
                                <DummyTab viesti="Ei joukkuetta kilpailussa!"/> :
                                <LeimausTab
                                    kayttajanJoukkue={kayttajanJoukkue}
                                    kilpailunRastit={kilpailunRastit}/> }
                </TabPanel>
            </Tabs>
        </main>
    );
};

export default Main;
