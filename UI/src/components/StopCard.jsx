import '../css/StopCard.css'

function StopCard({stop}) {
    return (
        <div className="stops-card">
            <div className="stop-direction">
                <h3>{stop.direction}</h3>
            </div>
            <div className="stop-name">
                <p>{stop.stop_name}</p>
            </div>

        </div>
    )
}

export default StopCard;