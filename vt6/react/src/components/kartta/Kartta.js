import React, { PureComponent } from "react";
import "leaflet/dist/leaflet.css";
import { MapContainer, TileLayer } from "react-leaflet";
import Paikkakunta from "./Paikkakunta";

class Kartta extends PureComponent {
    constructor(props) {
        super(props);
    }

    render() {
        const {
            markerLatLon,
            centerLatLon,
            paikkakunta,
            onKarttaDblClick,
        } = this.props;

        console.log(centerLatLon);

        return (
            <div className="kartta">
                    <MapContainer
                        center={centerLatLon}
                        zoom={9}
                        scrollWheelZoom={false}
                        doubleClickZoom={false}
                    >
                        <TileLayer
                            attribution='&copy; <a href="http://osm.org/copyright">OpenStreetMap</a> contributors'
                            url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
                        />
                        <Paikkakunta
                            markerLatLon={markerLatLon}
                            centerLatLon={centerLatLon}
                            paikkakunta={paikkakunta}
                            onKarttaDblClick={onKarttaDblClick}
                        />
                    </MapContainer>
            </div>
        );
    }
}

export default Kartta;
