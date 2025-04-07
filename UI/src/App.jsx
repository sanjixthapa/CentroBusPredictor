import { useState } from 'react'
import Home from './pages/Home'
import AllBuses from './pages/AllBuses'
import './css/App.css'
import { Route, Routes } from 'react-router-dom'
import NavBar from './components/NavBar'

function App() {
  const [count, setCount] = useState(0)

  return (
    <div className='navigation'>
      <NavBar />
      <main className='main-content'>
        
        <Routes>
          <Route path='/' element={<Home />} />
          <Route path='/allbuses' element={<AllBuses />} />
        </Routes>
      </main>
    </div>
  )
}

export default App
