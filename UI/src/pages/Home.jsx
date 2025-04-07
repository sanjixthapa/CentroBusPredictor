import { useState } from "react";
import BusCard from "../components/BusCard";
import '../css/Home.css'

function Home() {
    // need to add the state for rerendering
    const [searchQuery,setSearchQuery] = useState('')

    const buses =[
        {id:1, route:"Oswego to Syracuse", path:"Green Route"},
        {id:2, route:"Oswego to Fulton", path:"Blue Route"},
        {id:3, route:"Fulton to Syracuse", path:"Red Route"}
    ]

    const HandleSearch=(e) =>{
        // preventDefault so that it won't refresh page when state change
        e.preventDefault()
        alert(searchQuery)
        setSearchQuery("")
    }

    return (
        <div className="home">
            <form onSubmit={HandleSearch} className="search-form">
                <input type="text" 
                placeholder="Search for buses" 
                className="search-input"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                />
                <button type="submit" className="search-button">Search</button>
            </form>
            <div className="bus-grid">
                {/* it help with the filters*/}
                {buses.map(bus => 
                bus.path.toLowerCase().startsWith(searchQuery.toLowerCase()) && 
                <BusCard bus={bus} key={bus.id} />)}
            </div>
        </div>
    )
}

export default Home