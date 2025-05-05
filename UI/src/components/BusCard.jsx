import "../css/BusCard.css";
import {Link} from 'react-router-dom'

function BusCard({ bus }) {
  const linkPath = bus.route
  ? `/${bus.route}`
  : `/${bus.route_id}/${bus.bus_id}/1`;

  return (
    <Link to={linkPath}>
      <div className="bus-card">
        <div className="bus-title">
          <h3>{bus.route}</h3>
          <h2>{bus.rtname}</h2>
        </div>
        <div className="bus-info">
          <h4>{bus.bus_id}</h4>
          <p>{bus.route_id}</p>
        </div>
      </div>
    </Link>
  );
}

export default BusCard;
