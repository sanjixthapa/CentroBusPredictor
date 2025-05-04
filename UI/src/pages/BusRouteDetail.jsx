import React from 'react'
import { useParams } from 'react-router-dom';
import { getStopBack, getStopTo } from '../services/getBusRoute';
import StopCard from '../components/StopCard';
import '../css/Home.css'

function BusRouteDetail() {

  // Step 2: Destructure and log the specific param
  const { routeID } = useParams();
  console.log("busRoute:", routeID);

  const {stopsBack, loading: loadingBack, error: errorBack} = getStopBack(routeID);
  const {stopsTo, loading: loadingTo , error: errorTo } = getStopTo(routeID);

  console.log(stopsBack)
  console.log(loadingBack)
  console.log(loadingTo)


  if (loadingTo || loadingBack) return <div>Loading...</div>;
  if (errorTo || errorBack) return <div>Error loading data.</div>;

  return (
    <div className='stops-information'>
        <div className='bus-to'>
          {stopsTo.map(stop => <StopCard  stop={stop} key={stop.stop_id} />)}
        </div>
        <div className='bus-from'>
          {stopsBack.map(stop => <StopCard  stop={stop} key={stop.stop_id} />)}
        </div>
    </div>
  )
}

export default BusRouteDetail;