import { useState } from "react";
import BusCard from "../components/BusCard";
import '../css/Home.css'
import { getBuses, getBusRoute } from "../services/getBusRoute";

function Home() {
    // need to add the state for rerendering
    const {runBuses, loading: loadingBuses, error: errorBuses } = getBuses();
    console.log(runBuses)
    // const {routes, loading: loadingRoute, loading: errorRoute } = getBusRoute();
    
    if (loadingBuses) return <div>Loading routes...</div>
    if (errorBuses) return <div>Error : {error}</div>

    return (
        <div className="home">
            <div className="bus-header">
                <h2>Running Buses</h2>
            </div>
            <div className="bus-grid">
                {/* it help with the filters*/}
                {runBuses.map(route => 
                <BusCard bus={route} key={route.id} />)}
            </div>
        </div>
    )
}

export default Home