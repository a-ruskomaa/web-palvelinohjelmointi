import React, { PureComponent } from "react";

class Ennustetaulukko extends PureComponent {
    constructor(props) {
        super(props);
    }

    render() {
        const { ennusteet, ennusteet_pk, havainnot_pk } = this.props;

        const rows = [];

        /*
        * Propertyna annettu 'ennusteet' sisältää kaikkien kolmen paikkakunnan ennustedatan.
        * Jos paikkakuntaa i ei ole valittu, on ennusteet[i] määrittelemätön (undefined). Lisätään
        * tässä tapauksessa taulukkoon apuobjekteja, jotka helpottavat luotavan html-taulukon käsittelyä.
        */
        for (const i in ennusteet) {
            if (!ennusteet[i]) {
                ennusteet[i] = new Array(10).fill({
                    aika: undefined,
                    lampotila: undefined,
                });
            }
        }

        /*
        * Luodaan 10 <tr>-objektia, joiden lapsina on kentät ennusteiden aikavälille sekä ennusteiden
        * lämpötilat paikkakuntakohtaisesti. Oletus on, että kaikki MET Norway:n palvelusta haetut
        * ennusteet ajoittuvat samoille aikaväleille. Jos mikään kolmesta ennustetaulukosta ei sisällä
        * aikatietoja, näytetään taulukossa "NA". Samoin toimitaan jos joku sarakkeista ei sisällä lämpötiladataa.
        */
        for (let i = 0; i < 10; i++) {
            rows.push(
                <tr key={`ennusterivi_${i}`}>
                    <td>
                        {ennusteet[0][i].aika ||
                            ennusteet[1][i].aika ||
                            ennusteet[2][i].aika ||
                            "NA"}
                    </td>
                    <td>{ennusteet[0][i].lampotila || "NA"} °C</td>
                    <td>{ennusteet[1][i].lampotila || "NA"} °C</td>
                    <td>{ennusteet[2][i].lampotila || "NA"} °C</td>
                </tr>
            );
        }

        /*
        * Otsakkeissa näytettävä teksti riippuu siitä, vastaako paikkakunta, johon sääennusteet kohdistuvat sitä
        * paikkakuntaa jonka käyttäjä on valinnut. Jos paikkakuntaa ei ole valittuna, näytetään teksti "Paikkakunta i"
        */
        return (
            <div className="ennustetaulukko">
                <table>
                    <tbody>
                        <tr>
                            <th>Sääennuste</th>
                            <th>
                                {ennusteet_pk[0] && havainnot_pk[0]
                                    ? ennusteet_pk[0] === havainnot_pk[0]
                                        ? havainnot_pk[0]
                                        : `${havainnot_pk[0]} (${ennusteet_pk[0]})`
                                    : "Paikkakunta 1"}
                            </th>
                            <th>
                                {ennusteet_pk[1] && havainnot_pk[1]
                                    ? ennusteet_pk[1] === havainnot_pk[1]
                                        ? havainnot_pk[1]
                                        : `${havainnot_pk[1]} (${ennusteet_pk[1]})`
                                    : "Paikkakunta 2"}
                            </th>
                            <th>
                                {ennusteet_pk[2] && havainnot_pk[2]
                                    ? ennusteet_pk[2] === havainnot_pk[2]
                                        ? havainnot_pk[2]
                                        : `${havainnot_pk[2]} (${ennusteet_pk[2]})`
                                    : "Paikkakunta 3"}
                            </th>
                        </tr>
                        {rows}
                    </tbody>
                </table>
                <a href="https://www.yr.no/en">
                    Weather data from Yr, provided by MET Norway
                </a>
            </div>
        );
    }
}

export default Ennustetaulukko;
