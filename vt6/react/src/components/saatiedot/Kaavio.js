import React, { PureComponent } from "react";
import { Line } from "react-chartjs-2";

const data = {
    datasets: [
        {
            label: "Paikkakunta 1",
            fill: false,
            lineTension: 0.5,
            borderColor: 'rgb(192, 75, 192)',
            borderWidth: 2,
            data: new Array(10),
        },
        {
            label: "Paikkakunta 2",
            fill: false,
            lineTension: 0.5,
            borderColor: 'rgb(75, 192, 192)',
            borderWidth: 2,
            data: new Array(10),
        },
        {
            label: "Paikkakunta 3",
            fill: false,
            lineTension: 0.5,
            borderColor: 'rgb(192, 192, 75)',
            borderWidth: 2,
            data: new Array(10),
        }
    ],
};

class Kaavio extends PureComponent {
    constructor(props) {
        super(props);
    }

    render() {
        const { ennusteet, ennusteet_pk } = this.props;

        data.labels = (ennusteet[0] || ennusteet[1] || ennusteet[2] || new Array(10).fill({aika: ""})).map(dp => dp.aika);

        data.datasets[0].label = (ennusteet_pk[0] || "Paikkakunta 1")
        data.datasets[1].label = (ennusteet_pk[1] || "Paikkakunta 2")
        data.datasets[2].label = (ennusteet_pk[2] || "Paikkakunta 3")

        data.datasets[0].data = (ennusteet[0] || new Array(10).fill({lampotila: undefined})).map(dp => dp.lampotila);
        data.datasets[1].data = (ennusteet[1] || new Array(10).fill({lampotila: undefined})).map(dp => dp.lampotila);
        data.datasets[2].data = (ennusteet[2] || new Array(10).fill({lampotila: undefined})).map(dp => dp.lampotila);

        return (
            <div className="kaavio">
                <Line
                    data={data}
                    options={{
                        legend: {
                            display: true,
                            position: "right",
                        },
                    }}
                />
            </div>
        );
    }
}

export default Kaavio;
