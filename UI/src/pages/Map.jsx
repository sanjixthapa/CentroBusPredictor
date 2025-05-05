import { MapContainer, TileLayer, Marker, Popup } from 'react-leaflet';
import 'leaflet/dist/leaflet.css'; 
import '../css/map.css';
import {getPrediction, getStopTo, getBuses, getStopBack, getWeather } from '../services/getBusRoute';
import { useParams } from 'react-router-dom';
import { useState } from "react";
import busLogo from '../assets/bus.png';
import L from 'leaflet'; 

function Map() {
    // do handle click on the location for stop
    const { routeID, busID = 'defaultBusID'  } = useParams();
    const {runBuses, loading: loadingBus, error: errorBus } = getBuses();
    const [direction, setDirection] = useState('to')
    const [selectedStopID, setSelectedStop] = useState(null);
    const {predictions, loading: loadingPredictions} = getPrediction(
        routeID,
        selectedStopID?.stop_id
    )
    const {weathers, loading: loadingWeather, error: erroWeather} = getWeather(routeID)
    


    const handleStopClick = (stop)=> {
        setSelectedStop(stop)
    }

 

    const busIcon = new L.Icon({
        iconUrl: busLogo,
        iconSize: [30, 30],
        iconAnchor: [15, 15],
    });
    
   

    const foundBus = busID !== 'defaultBusID' 
        ? runBuses?.find(bus => bus.bus_id === Number(busID))
        : null;

    
    

    
    // get Buses not returning an array
    const { stopsTo, loading: loadingTo, error: errorTo } = getStopTo(routeID);
    const {stopsBack, loading: loadingBack, error:errorBack} = getStopBack(routeID);
    console.log(routeID)
    // const {predictions, loading: loadingPre, error: errorPre} = getPrediction(busID,routeIDID);
    
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
                            eventHandlers={{
                                click: () => handleStopClick(stop)
                            }}
                        >
                            <Popup>
                                <strong>{stop.stop_name}</strong><br />
                                Direction: {stop.direction}<br />
                                Stop ID: {stop.stop_id}

                                {selectedStopID?.stop_id === stop.stop_id && (
                                    <div className='predictions'>
                                        {loadingPredictions ? (
                                            <p>Loading predictions...</p>
                                        ) : predictions ? (
                                            <>
                                                <p>Arrival window: {predictions.predicted_arrival_window}</p>
                                                {/* <pre>{JSON.stringify(predictions, null, 2)}</pre> Debug output */}
                                            </>
                                        ) : (
                                            <p>No predictions available</p>
                                        )}
                                    </div>
                                )}
                            </Popup>
                        </Marker>
                    ))}
                    {foundBus && (
                        <Marker 
                        icon={busIcon}
                        key={`bus-${foundBus.bus_id}`}
                        position={[
                            Number(foundBus.latitude), 
                            Number(foundBus.longitude)
                        ]}
                        >
                        <Popup>
                            Bus {foundBus.bus_id}<br />
                            Route: {foundBus.route_id}<br />
                            Speed: {foundBus.speed} mph
                        </Popup>
                        </Marker>
                    )}
                </MapContainer>
            </div>
            
            <div className='weather'>
                {weathers.length > 0 ?
                (
                    weathers.map((bus)=>
                    (
                        bus.weather && (
                            <div key={bus.bus_id}>
                                <h4>Bus {bus.route_id} Weather</h4>
                                <p>🌧️ Precipitation: {bus.weather.precipitation} mm</p>
                                <p>🌡️ Temperature: {bus.weather.temperature}°C</p>
                                <p>💨 Wind Speed: {bus.weather.wind_speed} km/h</p>
                            </div>
                        )
                    ))
                ):(
                    <p>No weather details</p>
                )
                }
            </div>
        </div>
    );
}

export default Map;