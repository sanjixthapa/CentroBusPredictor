import { useState } from 'react'
import Home from './pages/Home'
import AllBuses from './pages/AllBuses'
import './css/App.css'
import { Route, Routes } from 'react-router-dom'
import NavBar from './components/NavBar'
import Help from './pages/Help'
import Map from './pages/Map'
import BusRouteDetail from './pages/BusRouteDetail'

function App() {
  
  return (
    <div className='navigation'>
      <NavBar />
      <main className='main-content'>
        
        <Routes>
          <Route path='/' element={<Home />} />
          <Route path='/allbuses' element={<AllBuses />} />
          <Route path='/help' element={<Help />} />
          <Route path="/:routeID" element={<BusRouteDetail />} />
          <Route path='/:routeID/:stopId' element={<Map />} />
          <Route path="/:routeID/:busID/1"  element={<Map />} />
        </Routes>
      </main>
    </div>
  )
}

export default App
