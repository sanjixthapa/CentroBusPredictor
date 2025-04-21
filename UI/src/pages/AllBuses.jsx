import { useState } from "react";
import BusCard from "../components/BusCard";
import BusInfo from '../assets/allbusroutes.json'
import '../css/Home.css'

function AllBuses(){
    const [searchQuery,setSearchQuery]= useState('')

    const HandleSearch=(e)=>{
        e.preventDefault()
        alert(searchQuery)
        setSearchQuery('')
    }
    
    
    return (
        
        <div className="main-display">
            <form className="search-form" onSubmit={HandleSearch}>
                <input type="text"
                placeholder="Search for Bus"
                className="search-input"
                value={searchQuery}
                onChange={(e)=> setSearchQuery(e.target.value)}
                />
                <button type="submit" className="search-button">Search</button>
            </form>
            <div className="bus-grid">
                {BusInfo.buses.filter(bus =>
                    bus.route.toLowerCase().includes(searchQuery.toLowerCase()) ||
                    bus.stops.some(stop=>
                        stop.name.toLowerCase().includes(searchQuery.toLowerCase())
                    )
                )
                .map(bus => (
                    <BusCard bus={bus} key={bus.busNumber} />
                ))    
                }
            </div>

        </div>
    )
}

export default AllBuses;