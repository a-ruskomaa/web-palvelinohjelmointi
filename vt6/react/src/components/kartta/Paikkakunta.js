import React, { useEffect } from "react";
import { Marker, Popup, useMapEvents } from "react-leaflet";
import L from "leaflet";
import icon from "leaflet/dist/images/marker-icon.png";
import iconShadow from "leaflet/dist/images/marker-shadow.png";

// Jostain syystä react-leaflet ei osaa hakea oletusikonia oikeasta osoitteesta, vaan herjaa 404.
// Kierretään tämä ongelma määrittelemällä oma oletusikoni.
const DefaultIcon = L.icon({
    iconUrl: icon,
    shadowUrl: iconShadow,
    iconSize: [25,41],
    iconAnchor: [12,41]
});

const Paikkakunta = ({ centerLatLon, markerLatLon, onKarttaDblClick }) => {
    // Kutsutaan tapahtumankäsittelijää kun karttaa tuplaklikataan
    const map = useMapEvents({
        dblclick: onKarttaDblClick,
    });

    // Keskittää kartan kun centerLatLon property saa uuden arvon
    useEffect(() => {
        map.setView(centerLatLon)
    }, [centerLatLon, map])

    return markerLatLon[0] && markerLatLon[1] ? (
        <Marker position={markerLatLon} icon={DefaultIcon} />
    ) : null;
};

export default Paikkakunta;
