import React, { useEffect } from "react";
import { Marker, Popup, useMapEvents } from "react-leaflet";
import L from "leaflet";
import icon from "leaflet/dist/images/marker-icon.png";
import iconShadow from "leaflet/dist/images/marker-shadow.png";

const DefaultIcon = L.icon({
    iconUrl: icon,
    shadowUrl: iconShadow,
    iconSize: [25,41],
    iconAnchor: [12,41]
});

const Paikkakunta = ({ centerLatLon, markerLatLon, paikkakunta, onKarttaDblClick }) => {
    const map = useMapEvents({
        dblclick: onKarttaDblClick,
    });

    useEffect(() => {

        map.setView(centerLatLon)
    }, centerLatLon)

    return markerLatLon[0] && markerLatLon[1] ? (
        // <Marker position={[lat, lon]}>
        <Marker position={markerLatLon} icon={DefaultIcon} />
    ) : null;
};

export default Paikkakunta;
