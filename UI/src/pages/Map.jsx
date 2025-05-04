import { MapContainer, TileLayer, Marker, Popup } from 'react-leaflet';
import 'leaflet/dist/leaflet.css'; 
import '../css/map.css';
import {getPrediction, getStopTo, getBuses, getStopBack } from '../services/getBusRoute';
import { useParams } from 'react-router-dom';
import { useState } from "react";

function Map() {
    // do handle click on the location for stop
    const {routeID, busID} = useParams()
    const {runBuses, loading, error } = getBuses();
    const {direction, setDirection} = useState('to')
    console.log('Current direction:', direction);
    console.log(runBuses)
    
    // get Buses not returning an array
    const { stopsTo, loading: loadingTo, error: errorTo } = getStopTo(routeID);
    const {stopsBack, loading: loadingBack, error:errorBack} = getStopBack(routeID);
    // const {predictions, loading: loadingPre, error: errorPre} = getPrediction(busID);
    
    console.log(stopsTo);
    console.log(stopsBack);
    
    if (loadingTo || loadingBack) return <div>Loading</div>;
    if (errorTo || errorBack) return <div>Error 404</div>;

    // Calculate average center if there are stops
    const calculateCenter = () => {
        if (!stopsTo || stopsTo.length === 0) return [43.4543, -76.5435]; // Default to first stop if no stops
        
        const avgLat = stopsTo.reduce((sum, stop) => sum + stop.latitude, 0) / stopsTo.length;
        const avgLng = stopsTo.reduce((sum, stop) => sum + stop.longitude, 0) / stopsTo.length;
        return [avgLat, avgLng];
    };

    return (
        <div className='map-main-display'>
            <div className='map-navbar'>
                <button className='to-button' onClick={()=> setDirection("to")}>To</button>
                <button className='from-button' onClick={()=> setDirection("from")}>From</button>
            </div>
            <div className="map-container" style={{ height: '100vh', width: '100%' }}>
                <MapContainer 
                    center={calculateCenter()} 
                    zoom={15}  // Higher zoom for campus-level view
                    scrollWheelZoom={true}  // Enable zooming
                    style={{ height: '100%', width: '100%' }}
                >
                    <TileLayer
                        attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
                        url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
                    />
                    
                    {/* Map all stops */}
                    {(direction === 'to' ? stopsTo: stopsBack)?.map((stop, index) => (
                        <Marker 
                            key={`${stop.stop_id}-${index}`} 
                            position={[stop.latitude, stop.longitude]}
                        >
                            <Popup>
                                <strong>{stop.stop_name}</strong><br />
                                Direction: {stop.direction}<br />
                                Stop ID: {stop.stop_id}
                            </Popup>
                        </Marker>
                    ))}
                </MapContainer>
            </div>
        </div>
    );
}

export default Map;