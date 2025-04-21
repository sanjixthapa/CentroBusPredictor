import {useState, useEffect} from 'react'

export function getBusRoute(){
    const [routes, setRoutes]= useState([])
    const [loading, setLoading] = useState(true)
    const [error, setError] = useState(null)

    useEffect(()=>{
        const fetchData = async () =>{
            try{
                const response = await fetch('http://127.0.0.1:5000/routes');
                if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
                const data = await response.json();
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

export function getStopTo(query){
    const [stopsTo,setStopsTo] =useState([])
    const [loading, setLoading]= useState(true)
    const [error,setError] = useState(null)

    useEffect(()=> {
        const fetchData = async () => {
            try{
                const response = await fetch(`http://127.0.0.1:5000/stops?route=${query}&dir=TO%20CAMPUS`);
                const data = await response.json();
                console.log(data)
                setStopsTo(data)
            }catch(err){
                setError(err)
                console.log(err.message)
            }finally{
                setLoading(false)
            }
        }
        fetchData();
    },[query])
    return {stopsTo, loading, error}
}

export function getStopBack(query){
    const [stopsBack,setStopsBack] =useState([])
    const [loading, setLoading]= useState(true)
    const [error,setError] = useState(null)

    useEffect(()=> {
        const fetchData = async () => {
            try{
                const response = await fetch(`http://127.0.0.1:5000/stops?route=${query}&dir=FROM%20CAMPUS`)
                const data = await response.json();
                console.log(data)
                setStopsBack(data)
            }catch(err){
                setError(err)
                console.log(err.message)
            }finally{
                setLoading(false)
            }

        }
        fetchData();
    },[query])

    return {stopsBack, loading, error}
    
}