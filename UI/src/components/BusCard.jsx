

function BusCard({bus}) {
    return (
        <div className="bus-card">
            <div className="bus-title">
                <h3>Bus Name</h3>
            </div>
            <div className="bus-info">
                <h4>{bus.route}</h4>
                <p>{bus.path}</p>
            </div>
        </div>
    )
}

export default BusCard;