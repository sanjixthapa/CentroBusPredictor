import {useState, useEffect} from 'react'

export function getBusRoute(){
    const [routes, setRoutes]= useState([])
    const [loading, setLoading] = useState(true)
    const [error, setError] = useState(null)

    useEffect(()=>{
        const fetchData = async () =>{
            try{
                const response = await fetch(`http://127.0.0.1:5001/routes/db`);
                if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
                const data = await response.json();
                const routesWithIds = data.map(route => ({
                    ...route,
                    id: generateRouteId(route.route, route.rtname)
                  }));
                console.log(data)
                setRoutes(data)
            }catch(err){
                setError(err.message)
                console.log(err.message)
            }finally{
                setLoading(false)
            }
        };
        fetchData();
    },[])
    return {routes, loading, error}
}


export function getStopTo(stop_id) {
    const [stopsTo, setStopsTo] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    useEffect(() => {
        const fetchData = async () => {
            try {
                const response = await fetch(`http://127.0.0.1:5001/stops?route=${stop_id}&dir=TO%20OSWEGO`);
                if (!response.ok) throw new Error("Failed to fetch Oswego direction");
                
                const data = await response.json();
                
                if (data.error) {
                    throw new Error(data.error);
                }
                
                if (Array.isArray(data)) {
                    setStopsTo(data);
                } else {
                    throw new Error("Unexpected data format");
                }
                
            } catch (err) {
                console.log(err.message);
                
                try {
                    // Fallback to "FROM CAMPUS"
                    const fallbackResponse = await fetch(
                        `http://127.0.0.1:5001/stops?route=${stop_id}&dir=FROM%20CAMPUS`
                    );
                    
                    if (!fallbackResponse.ok) throw new Error("Failed to fetch fallback direction");
                    
                    const fallbackData = await fallbackResponse.json();
                    
                    if (fallbackData.error) {
                        throw new Error(fallbackData.error);
                    }
                    
                    if (Array.isArray(fallbackData)) {
                        setStopsTo(fallbackData);
                    } else {
                        throw new Error("Invalid fallback data format");
                    }
                    
                } catch (fallbackErr) {
                    console.log("Both fetches failed:", fallbackErr.message);
                    setError(fallbackErr);
                    setStopsTo([]);
                }
            } finally {
                setLoading(false); // This will now run in all cases
            }
        };

        fetchData();
    }, [stop_id]);

    return { stopsTo, loading, error };
}

export function getStopBack(query){
    const [stopsBack,setStopsBack] =useState([])
    const [loading, setLoading]= useState(true)
    const [error,setError] = useState(null)

    useEffect(()=> {
        const fetchData = async () => {
            try{
                //try * to see if they pull from campus and oswego for param for from
                const response = await fetch(`http://127.0.0.1:5001/stops?route=${query}&dir=FROM%20OSWEGO`)
                if(!response.ok) throw new Error("Failed to fetch oswego")
                const data = await response.json();

                if(data.error){
                    throw new Error(data.error)
                }
                if(Array.isArray(data)){
                    setStopsBack(data)
                }else{
                    throw new Error("Not a valid format")
                }
                
            }catch(err){
                console.log(err.message)
            
                try{
                    const fallBackResponse = await fetch(
                        `http://127.0.0.1:5001/stops?route=${query}&dir=FROM%20CAMPUS`
                    );
                    if(!fallBackResponse.ok) throw new Error("campus no okay");
                    const fallBackData = await fallBackResponse.json();
                    if(fallBackData.error){
                        throw new Error(fallBackData.error)
                    }
                    if(Array.isArray(fallBackData)){
                        setStopsBack(fallBackData)
                    }else{
                        throw new Error("not a valid format for fallback")
                    }
                    
                }
                catch(fallBackError){
                    console.log("Both fetches failed to pull: ", fallBackError.message);
                    setError(fallBackError)
                    setStopsBack([]);
                }
            

            }
            finally{
                setLoading(false)
            }
        }
        fetchData();
    },[query])

    return {stopsBack, loading, error}
    
}

export function getBuses(){
    const [runBuses,setRunBuses] = useState([])
    const [error, setError] =useState(null)
    const [loading, setLoading] = useState(true)

    useEffect(()=> {
        const fetchData = async () => {
            try{
                const response = await fetch('http://127.0.0.1:5001/buses/db')
                const data = await response.json()
                console.log(data)
                setRunBuses(data)
            }catch(err){
                setError(err)
                console.log(err.message)
            }finally{
                setLoading(false);
            }
        }
        fetchData();

    },[])

    return {runBuses, loading, error}
}

function generateRouteId(routeCode, routeName) {
    // Combine route code and name, then hash
    const str = `${routeCode}-${routeName}`;
    let hash = 0;
    for (let i = 0; i < str.length; i++) {
      hash = ((hash << 5) - hash) + str.charCodeAt(i);
      hash |= 0; // Convert to 32bit integer
    }
    return `route-${Math.abs(hash)}`;
  }

export function getPrediction(query){
    const [predictions,setPredictions] = useState([])
    const [error, setError] =useState(null)
    const [loading, setLoading] = useState(true)
    useEffect(()=>{
        const fetchData = async() =>{
            try{
                const response = await fetch(`http://localhost:5001/predict_eta_future?route_id=OSW10&stop_id=16183&date=2025-04-2&time=18:47`)
                const data = await response.json()
                console.log(data)
                setPredictions(data)
            }catch(err){
                setError(err)
                console.log(err.message)
            }finally{
                setLoading(false);
            }
        }
        fetchData()

    },[query])

    return {predictions, loading, error}
}