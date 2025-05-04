import { useState } from "react";
import BusCard from "../components/BusCard";
import BusInfo from '../assets/allbusroutes.json'
import { getBusRoute } from "../services/getBusRoute";
import '../css/Home.css'

function AllBuses(){
    const [searchQuery,setSearchQuery]= useState('')
    const {routes, loading, error } = getBusRoute();
    
    
    if (loading) return <div>Loading routes...</div>
    if (error) return <div>Error : {error}</div>

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
            {routes.filter(route => 
                    route.route.toLowerCase().includes(searchQuery.toLowerCase()) ||
                    route.rtname.toLowerCase().includes(searchQuery.toLowerCase())
                )
                .map(route => 
                    <BusCard bus={route} key={route.id} />
                )}
            </div>

        </div>
    )
}

export default AllBuses;