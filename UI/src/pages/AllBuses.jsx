import BusCard from "../components/BusCard";
import '../css/Home.css'

function AllBuses(){
    const buses = [
        { id: 1, route: "Oswego to Syracuse", path: "Green Route" },
        { id: 2, route: "Oswego to Fulton", path: "Blue Route" },
        { id: 3, route: "Fulton to Syracuse", path: "Red Route" },
        { id: 4, route: "Oswego to Rochester", path: "Yellow Route" },
        { id: 5, route: "Syracuse to Albany", path: "Orange Route" },
        { id: 6, route: "Fulton to Buffalo", path: "Purple Route" },
        { id: 7, route: "Rochester to Buffalo", path: "Silver Route" },
        { id: 8, route: "Oswego to Watertown", path: "Teal Route" },
        { id: 9, route: "Watertown to Syracuse", path: "Cyan Route" },
        { id: 10, route: "Buffalo to Albany", path: "Magenta Route" },
        { id: 11, route: "Oswego to Utica", path: "Brown Route" },
        { id: 12, route: "Albany to NYC", path: "Gold Route" },
        { id: 13, route: "Syracuse to Binghamton", path: "Indigo Route" },
        { id: 14, route: "Binghamton to NYC", path: "Black Route" },
        { id: 15, route: "Utica to Rochester", path: "White Route" }
    ];
    
    
    return (
        
        <div className="main-display">
            <div className="bus-display">
                {buses.map(bus =>
                    <BusCard bus={bus} key={bus.id} />
                )}
            </div>

        </div>
    )
}

export default AllBuses;