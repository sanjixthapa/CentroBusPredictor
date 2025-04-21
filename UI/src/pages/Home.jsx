import { useState } from "react";
import BusCard from "../components/BusCard";
import '../css/Home.css'
import { getBusRoute } from "../services/getBusRoute";

function Home() {
    // need to add the state for rerendering
    const [searchQuery,setSearchQuery] = useState('')
    const {routes, loading, error } = getBusRoute();
    
    // const HandleSearch=(e) =>{
    //     // preventDefault so that it won't refresh page when state change
    //     e.preventDefault()
    //     alert(searchQuery)
    //     setSearchQuery("")
    // }
    if (loading) return <div>Loading routes...</div>
    if (error) return <div>Error : {error}</div>

    return (
        <div className="home">
            <div className="bus-header">
                <h2>Running Buses</h2>
            </div>
            <div className="bus-grid">
                {/* it help with the filters*/}
                {routes.map(route => 
                <BusCard bus={route} key={route.id} />)}
            </div>
        </div>
    )
}

export default Home