import React, { PureComponent } from "react";
import dataService from "../services/dataService";
import Suosikit from "./suosikit/Suosikit";
import Ennustetaulukko from "./saatiedot/Ennustetaulukko";
import Havaintotaulukko from "./saatiedot/Havaintotaulukko";
import Valitsinpalkki from "./Valitsinpalkki";
import "./Main.css";
import Kartta from "./kartta/Kartta";
import Kaavio from "./saatiedot/Kaavio";

const jkl_koordinaatit = [62.23333, 25.73333]

class Main extends PureComponent {
    constructor(props) {
        super(props);

        /*
        * Luodaan oletustila. Tuhlaileva lähestymistapa, mutta tämä helpotti komponentin suunnittelussa
        * sekä monissa tapahtumankäsittelijöiden ehdollisissa tilanteissa, joten en katso tarpeelliseksi muuttaa.
        */
        this.state = {
            suosikit: {},
            kartallaNaytetaan: 1,
            karttaValinnat: [{
                lat: undefined,
                lon: undefined
            }, {
                lat: undefined,
                lon: undefined
            }, {
                lat: undefined,
                lon: undefined
            }],
            karttaCenter: jkl_koordinaatit,
            paikkakuntaValinnat: ["", "", ""],
            saatiedot1: {
                paikkakunta: undefined,
                havainnot: undefined,
                ennuste: undefined,
            },
            saatiedot2: {
                paikkakunta: undefined,
                havainnot: undefined,
                ennuste: undefined,
            },
            saatiedot3: {
                paikkakunta: undefined,
                havainnot: undefined,
                ennuste: undefined,
            },
            paikkakunnat: [],
        };
    }

    // Luodaan AbortController API:n käytön mahdollistava objekti, jolla saadaan keskeytettyä asynkroniset
    // kutsut jos komponentti unmountataan ennen niiden valmistumista. https://caniuse.com/abortcontroller
    controller = new AbortController();

    /**
     * Käsittelee paikkakunnan valinnan. Sama tapahtumankäsittelijä toimii sekä suosikkilistassa
     * että alasvetovalikoissa. Tapahtuma saa aikaan säätietojen haun kyseiselle paikkakunnalle.
     */
    handlePaikkakuntaSelect = (paikkakunta, numero, event) => {
        const index = numero - 1;

        // Poistetaan mahdollisesti valitut koordinaatit karttavalinnoista, jonka seurauksena markeri poistetaan kartalta
        const uudetKarttaValinnat = [...this.state.karttaValinnat];
        uudetKarttaValinnat[index] = {
            lat: undefined,
            lon: undefined
        }

        // Korvataan valittuna oleva paikkakunta uudella valinnalla
        const uudetPaikkakuntaValinnat = [...this.state.paikkakuntaValinnat];
        uudetPaikkakuntaValinnat[index] = paikkakunta;

        // Lisätään suosikkilistaukseen yksi katselukerta kyseiselle paikkakunnalle
        let uudetSuosikit;
        if (paikkakunta !== "kartta") {
            uudetSuosikit = { ...this.state.suosikit };
            uudetSuosikit[paikkakunta] = uudetSuosikit[paikkakunta] + 1 || 1;
        }

        // Tallennetaan käyttäjän historia firestoreen
        dataService.tallennaKayttajanHistoria(this.props.user.uid, {
            viimeksiValitut: uudetPaikkakuntaValinnat,
            karttahistoria: uudetKarttaValinnat,
            suosikit: uudetSuosikit
        });
        
        // Etsitään valitun paikkakunnan koordinaatit ja keskitetään karttanäkymä
        const pkObj = this.state.paikkakunnat.find(pk => pk.name === paikkakunta);
        const centerLatLon = [pkObj.lat, pkObj.lon]

        this.setState({
            paikkakuntaValinnat: uudetPaikkakuntaValinnat,
            karttaValinnat: uudetKarttaValinnat,
            suosikit: uudetSuosikit,
            karttaCenter: centerLatLon
        });

        // Haetaan lopuksi paikkakuntakohtaiset säätiedot ja päivitetään komponentin tila 
        // kun pyyntöön saadaan vastaus
        if (paikkakunta !== "kartta") {
            console.log("haetaan säätiedot paikkakunnalle", paikkakunta);
            dataService
                .haeSaatiedotNimella(paikkakunta)
                .then((data) => {
                    this.setState({ [`saatiedot${numero}`]: data });
                })
                .catch((e) => console.log(e));
        }

    };

    /**
     * Poistaa valitun paikkakunnan suosikkilistauksesta
     */
    handleValikkoRemove = (paikkakunta, event) => {
        const uudetSuosikit = { ...this.state.suosikit };
        delete uudetSuosikit[paikkakunta];

        dataService.tallennaKayttajanHistoria(this.props.user.uid, {
            suosikit: uudetSuosikit,
        });

        this.setState({ suosikit: uudetSuosikit });
    };


    /**
     * Päivittää karttanäkymän vastaamaan klikatussa alasvetovalikossa valittuna olevaa
     * paikkakuntaa tai karttapistettä.
     */
    onValitsinClick = (pk_nimi, id, event) => {
        const karttavalinta = this.state.karttaValinnat[id - 1];
        const paikkakunta = this.state.paikkakunnat.find(pk => pk.name === pk_nimi) || {lat: undefined,lon: undefined};
        const centerLatLon = [karttavalinta.lat || paikkakunta.lat || jkl_koordinaatit[0],
                              karttavalinta.lon || paikkakunta.lon || jkl_koordinaatit[1]];
        this.setState({kartallaNaytetaan: id, karttaCenter: centerLatLon})
    };


    /**
     * Valitsee tuplaklikattua karttapistettä vastaavat koordinaatit ja hakee koordinaatteja vastaavat säätiedot.
     */
    onKarttaDblClick = (event) => {
        const {lat: lat, lng: lon} = event.latlng;
        const index = this.state.kartallaNaytetaan - 1;
        const uudetKarttaValinnat = [...this.state.karttaValinnat];
        const uudetPaikkakuntaValinnat = [...this.state.paikkakuntaValinnat];

        // Lisätään valittu karttapiste karttavalinnat sisältävään taulukkoon
        uudetKarttaValinnat[index] = {
            lat: lat,
            lon: lon
        }

        // Muutetaan valittu paikkakunta karttapisteeksi
        uudetPaikkakuntaValinnat[index] = "kartta"

        // Tallennetaan käyttäjän historia firestoreen
        dataService.tallennaKayttajanHistoria(this.props.user.uid, {
            viimeksiValitut: uudetPaikkakuntaValinnat,
            karttahistoria: uudetKarttaValinnat
        });

        this.setState({karttaValinnat: uudetKarttaValinnat,
                        paikkakuntaValinnat: uudetPaikkakuntaValinnat})

        // Haetaan koordinaatteja vastaavat säätiedot ja päivitetään komponentin tila
        // kun pyyntöön saadaan vastaus
        dataService.haeSaatiedotKoordinaateilla(lat, lon)
        .then((data) => {
            this.setState({ [`saatiedot${index + 1}`]: data });
        })
    }


    /**
     * Hakee ensimmäisen renderöinnin jälkeen käyttäjän katseluhistorian sekä tietokantaan
     * tallennetut paikkakuntavalinnat ja lisää ne komponentin tilaan.
     */
    async componentDidMount() {
        const initialState = {};

        // Haetaan käyttäjän historia
        const kayttajanHistoria = await dataService.haeKayttajanHistoria(this.props.user.uid);

        if (kayttajanHistoria) {
            if (kayttajanHistoria.viimeksiValitut) {
                initialState.paikkakuntaValinnat = kayttajanHistoria.viimeksiValitut;
            }
            if (kayttajanHistoria.karttahistoria) {
                initialState.karttaValinnat = kayttajanHistoria.karttahistoria;
            }
            if (kayttajanHistoria.suosikit) {
                initialState.suosikit = kayttajanHistoria.suosikit;
            }
        } else {
            // Tallennetaan uuden käyttäjän tiedot firestoreen
            dataService
                .tallennaKayttajanHistoria(this.props.user.uid, {
                    viimeksiValitut: this.state.paikkakuntaValinnat,
                    suosikit: this.state.suosikit,
                    karttahistoria: this.state.karttaValinnat
                })
                .then(() => console.log("Uuden käyttäjän tiedot tallennettu"))
                .catch((e) =>
                    console.log("Virhe käyttäjän tietojen tallennuksessa", e)
                );
        }

        // Haetaan paikkakuntalistaus
        initialState.paikkakunnat = await dataService.haePaikkakunnat();

        this.setState(initialState);

        // Iteroidaan käyttäjän edellisen katselukerran tiedot läpi ja haetaan niitä vastaavat säätiedot
        for (const i = 0; i < 3; i++) {
            if (initialState.paikkakuntaValinnat[i] !== "") {
                if (initialState.paikkakuntaValinnat[i] === "kartta" && 
                    initialState.karttaValinnat[i]) {
                    dataService
                        .haeSaatiedotKoordinaateilla(initialState.karttaValinnat[i].lat, initialState.karttaValinnat[i].lon)
                        .then((data) => {
                            this.setState({
                                [`saatiedot${parseInt(i) + 1}`]: data,
                            });
                        })
                        .catch((e) => console.log(e));
                } else {
                    dataService
                        .haeSaatiedotNimella(
                            initialState.paikkakuntaValinnat[i]
                        )
                        .then((data) => {
                            this.setState({
                                [`saatiedot${parseInt(i) + 1}`]: data,
                            });
                        })
                        .catch((e) => console.log(e));
                }
            }
        }
    }

    /**
     * Keskeyttää keskeneräiset asynkroniset kutsut yms kun komponentti unmountataan.
     */
    componentWillUnmount() {
        this.controller.abort();
    }

    render() {
        const suosikit = Object.entries(this.state.suosikit);
        suosikit.sort((a, b) => b[1] - a[1]);

        const paikanNimet = this.state.paikkakunnat.map((pk) => pk.name);

        const karttaTiedot = this.state.karttaValinnat[this.state.kartallaNaytetaan - 1];

        return (
            <div className="grid-container">
                <Valitsinpalkki
                    paikkakuntaValinnat={this.state.paikkakuntaValinnat}
                    paikkakunnat={paikanNimet}
                    onValitsinChange={this.handlePaikkakuntaSelect}
                    onValitsinClick={this.onValitsinClick}
                />
                <Kartta 
                    centerLatLon={[karttaTiedot.lat || this.state.karttaCenter[0],
                                    karttaTiedot.lon || this.state.karttaCenter[1]]}
                    paikkakunta={karttaTiedot.paikkakunta}
                    markerLatLon={[karttaTiedot.lat, karttaTiedot.lon]}
                    onKarttaDblClick={this.onKarttaDblClick}/>
                <Suosikit
                    suosikit={suosikit}
                    handleValikkoSelect={this.handlePaikkakuntaSelect}
                    handleValikkoRemove={this.handleValikkoRemove}
                />
                <Havaintotaulukko
                    paikkakunnat={[
                        this.state.saatiedot1.havainnot_pk,
                        this.state.saatiedot2.havainnot_pk,
                        this.state.saatiedot3.havainnot_pk,
                    ]}
                    havainnot={[
                        this.state.saatiedot1.havainnot,
                        this.state.saatiedot2.havainnot,
                        this.state.saatiedot3.havainnot,
                    ]}
                />
                <Kaavio
                    ennusteet_pk={[
                        this.state.saatiedot1.ennuste_pk,
                        this.state.saatiedot2.ennuste_pk,
                        this.state.saatiedot3.ennuste_pk,
                    ]}
                    ennusteet={[
                        this.state.saatiedot1.ennuste,
                        this.state.saatiedot2.ennuste,
                        this.state.saatiedot3.ennuste,
                    ]}/>
                <Ennustetaulukko
                    ennusteet_pk={[
                        this.state.saatiedot1.ennuste_pk,
                        this.state.saatiedot2.ennuste_pk,
                        this.state.saatiedot3.ennuste_pk,
                    ]}
                    havainnot_pk={[
                        this.state.saatiedot1.havainnot_pk,
                        this.state.saatiedot2.havainnot_pk,
                        this.state.saatiedot3.havainnot_pk,
                    ]}
                    ennusteet={[
                        this.state.saatiedot1.ennuste,
                        this.state.saatiedot2.ennuste,
                        this.state.saatiedot3.ennuste,
                    ]}
                />
            </div>
        );
    }
}

export default Main;
