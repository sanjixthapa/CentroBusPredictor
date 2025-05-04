import { Link, useParams } from 'react-router-dom';
import '../css/StopCard.css'

function StopCard({stop}) {
    const {routeID} = useParams();

    return (
        <Link to={`/${routeID}/${stop.stop_id}`}>
        <div className="stops-card">
            <div className="stop-direction">
                <h3>{stop.direction}</h3>
            </div>
            <div className="stop-name">
                <p>{stop.stop_name}</p>
            </div>
        </div>
        
        </Link>
        
    )
}

export default StopCard;