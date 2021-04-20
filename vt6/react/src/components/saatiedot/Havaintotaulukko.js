import React, { PureComponent } from "react";

class Havaintotaulukko extends PureComponent {
    constructor(props) {
        super(props);
    }

    render() {
        const {paikkakunnat, havainnot} = this.props;

        /*
        * Näytetään taulukossa mittaushavainnot, tai "NA" jos havaintotaulukon indeksissä ei ole dataa tai kyseisen
        * anturin mittausdataa ei ole saatavilla
        */ 
        return (
            <table className="havaintotaulukko">
                <tbody>
                    <tr>
                        <th>Säähavainnot</th>
                        <th>{paikkakunnat[0] || "Paikkakunta 1"}</th>
                        <th>{paikkakunnat[1] || "Paikkakunta 2"}</th>
                        <th>{paikkakunnat[2] || "Paikkakunta 3"}</th>
                    </tr>
                    <tr>
                        <td>Ilman lämpötila</td>
                        <td>{havainnot[0] ? havainnot[0].ILMA ? Math.round(havainnot[0].ILMA) : "NA" : "NA" } °C</td>
                        <td>{havainnot[1] ? havainnot[1].ILMA ? Math.round(havainnot[1].ILMA) : "NA" : "NA" } °C</td>
                        <td>{havainnot[2] ? havainnot[2].ILMA ? Math.round(havainnot[2].ILMA) : "NA" : "NA" } °C</td>
                    </tr>
                    <tr>
                        <td>Tien lämpötila</td>
                        <td>{havainnot[0] ? havainnot[0].TIE_1 ? Math.round(havainnot[0].TIE_1) : "NA" : "NA" } °C</td>
                        <td>{havainnot[1] ? havainnot[1].TIE_1 ? Math.round(havainnot[1].TIE_1) : "NA" : "NA" } °C</td>
                        <td>{havainnot[2] ? havainnot[2].TIE_1 ? Math.round(havainnot[2].TIE_1) : "NA" : "NA" } °C</td>
                    </tr>
                    <tr>
                        <td>Maan lämpötila</td>
                        <td>{havainnot[0] ? havainnot[0].MAA_1 ? Math.round(havainnot[0].MAA_1) : "NA" : "NA" } °C</td>
                        <td>{havainnot[1] ? havainnot[1].MAA_1 ? Math.round(havainnot[1].MAA_1) : "NA" : "NA" } °C</td>
                        <td>{havainnot[2] ? havainnot[2].MAA_1 ? Math.round(havainnot[2].MAA_1) : "NA" : "NA" } °C</td>
                    </tr>
                    <tr>
                        <td>Tuulennopeus</td>
                        <td>{havainnot[0] ? havainnot[0].KESKITUULI ? Math.round(havainnot[0].KESKITUULI) : "NA" : "NA" } m/s</td>
                        <td>{havainnot[1] ? havainnot[1].KESKITUULI ? Math.round(havainnot[1].KESKITUULI) : "NA" : "NA" } m/s</td>
                        <td>{havainnot[2] ? havainnot[2].KESKITUULI ? Math.round(havainnot[2].KESKITUULI) : "NA" : "NA" } m/s</td>
                    </tr>
                    <tr>
                        <td>Tuulen suunta</td>
                        <td>{havainnot[0] ? havainnot[0].TUULENSUUNTA ? Math.round(havainnot[0].TUULENSUUNTA) : "NA" : "NA" } °</td>
                        <td>{havainnot[1] ? havainnot[1].TUULENSUUNTA ? Math.round(havainnot[1].TUULENSUUNTA) : "NA" : "NA" } °</td>
                        <td>{havainnot[2] ? havainnot[2].TUULENSUUNTA ? Math.round(havainnot[2].TUULENSUUNTA) : "NA" : "NA" } °</td>
                    </tr>
                    <tr>
                        <td>Ilmankosteus</td>
                        <td>{havainnot[0] ? havainnot[0].ILMAN_KOSTEUS ? Math.round(havainnot[0].ILMAN_KOSTEUS) : "NA" : "NA" } %</td>
                        <td>{havainnot[1] ? havainnot[1].ILMAN_KOSTEUS ? Math.round(havainnot[1].ILMAN_KOSTEUS) : "NA" : "NA" } %</td>
                        <td>{havainnot[2] ? havainnot[2].ILMAN_KOSTEUS ? Math.round(havainnot[2].ILMAN_KOSTEUS) : "NA" : "NA" } %</td>
                    </tr>
                    <tr>
                        <td>Näkyvyys</td>
                        <td>{havainnot[0] ? havainnot[0].NAKYVYYS ? Math.round(havainnot[0].NAKYVYYS) : "NA" : "NA" } km</td>
                        <td>{havainnot[1] ? havainnot[1].NAKYVYYS ? Math.round(havainnot[1].NAKYVYYS) : "NA" : "NA" } km</td>
                        <td>{havainnot[2] ? havainnot[2].NAKYVYYS ? Math.round(havainnot[2].NAKYVYYS) : "NA" : "NA" } km</td>
                    </tr>
                </tbody>
            </table>
        );
    }
}

export default Havaintotaulukko;
