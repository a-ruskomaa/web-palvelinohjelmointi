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

    controller = new AbortController();

    handlePaikkakuntaSelect = (paikkakunta, numero, event) => {
        const index = numero - 1;

        const uudetKarttaValinnat = [...this.state.karttaValinnat];
        uudetKarttaValinnat[index] = {
            lat: undefined,
            lon: undefined
        }

        const uudetPaikkakuntaValinnat = [...this.state.paikkakuntaValinnat];
        uudetPaikkakuntaValinnat[index] = paikkakunta;

        let uudetSuosikit;
        if (paikkakunta !== "kartta") {
            uudetSuosikit = { ...this.state.suosikit };
            uudetSuosikit[paikkakunta] = uudetSuosikit[paikkakunta] + 1 || 1;
            console.log("uudet suosikit", uudetSuosikit);
        }

        dataService.tallennaKayttajanHistoria(this.props.user, {
            viimeksiValitut: uudetPaikkakuntaValinnat,
            suosikit: uudetSuosikit,
        });
        
        const pkObj = this.state.paikkakunnat.find(pk => pk.name === paikkakunta);
        const centerLatLon = [pkObj.lat, pkObj.lon]

        this.setState({
            paikkakuntaValinnat: uudetPaikkakuntaValinnat,
            karttaValinnat: uudetKarttaValinnat,
            suosikit: uudetSuosikit,
            karttaCenter: centerLatLon
        });

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

    handleValikkoRemove = (paikkakunta, event) => {
        const uudetSuosikit = { ...this.state.suosikit };
        delete uudetSuosikit[paikkakunta];

        dataService.tallennaKayttajanHistoria(this.props.user, {
            suosikit: uudetSuosikit,
        });

        this.setState({ suosikit: uudetSuosikit });
    };


    onValitsinClick = (pk_nimi, id, event) => {
        const karttavalinta = this.state.karttaValinnat[id - 1];
        const paikkakunta = this.state.paikkakunnat.find(pk => pk.name === pk_nimi) || {lat: undefined,lon: undefined};
        const centerLatLon = [karttavalinta.lat || paikkakunta.lat || jkl_koordinaatit[0],
                              karttavalinta.lon || paikkakunta.lon || jkl_koordinaatit[1]];
        this.setState({kartallaNaytetaan: id, karttaCenter: centerLatLon})
    };


    onKarttaDblClick = (event) => {
        console.log(event)
        const {lat: lat, lng: lon} = event.latlng;
        const index = this.state.kartallaNaytetaan - 1;
        const uudetKarttaValinnat = [...this.state.karttaValinnat];
        const uudetPaikkakuntaValinnat = [...this.state.paikkakuntaValinnat];

        uudetKarttaValinnat[index] = {
            lat: lat,
            lon: lon
        }

        uudetPaikkakuntaValinnat[index] = "kartta"

        this.setState({karttaValinnat: uudetKarttaValinnat,
                        paikkakuntaValinnat: uudetPaikkakuntaValinnat})

        dataService.haeSaatiedotKoordinaateilla(lat, lon)
        .then((data) => {
            this.setState({ [`saatiedot${index + 1}`]: data });
        })
    }

    async componentDidMount() {
        const initialState = {};

        // suosikit
        const kayttajanHistoria = await dataService.haeKayttajanHistoria(
            this.props.user
        );

        if (kayttajanHistoria.exists) {
            const data = kayttajanHistoria.data();
            console.log("Käyttäjän historia", data);

            if (data.viimeksiValitut) {
                initialState.paikkakuntaValinnat = data.viimeksiValitut;
            }
            if (data.karttahistoria) {
                initialState.karttaValinnat = data.karttahistoria;
            }
            if (data.suosikit) {
                initialState.suosikit = data.suosikit;
            }
        } else {
            dataService
                .tallennaKayttajanHistoria(this.props.user, {
                    viimeksiValitut: ["", "", ""],
                    suosikit: {},
                    karttahistoria: [{}, {}, {}],
                })
                .then(() => console.log("Uuden käyttäjän tiedot tallennettu"))
                .catch((e) =>
                    console.log("Virhe käyttäjän tietojen tallennuksessa", e)
                );
        }

        // paikkakunnat
        // initialState.paikkakunnat = ["Jyväskylä", "Helsinki", "Tampere"]
        initialState.paikkakunnat = await dataService.haePaikkakunnat();
        console.log("Paikkakunnat", initialState.paikkakunnat);

        this.setState(initialState);

        for (const i in initialState.paikkakuntaValinnat) {
            if (initialState.paikkakuntaValinnat[i] !== "") {
                if (initialState.paikkakuntaValinnat[i] !== "kartta") {
                    console.log("haetaan säätiedot paikkakunnalle",
                                initialState.paikkakuntaValinnat[i]);
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

    componentDidUpdate(prevProps, prevState) {
        console.log("updated state", this.state);

        // säätiedot

        // historian päivitys
    }

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
