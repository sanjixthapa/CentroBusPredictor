import {Link} from 'react-router-dom'
import '../css/Navbar.css'
import CentroLogo from '../assets/CentroLogo.png';

function NavBar() {

    
    const HandleSearch =()=>{
        alert("searching")
    }
    
    return (
        <nav className="navbar">
            <div className='navbar-brand'>
                <Link to='/'><img src={CentroLogo} alt="Centro Logo"/></Link>
            </div>
            {/* <form className='search-form' onSubmit={HandleSearch}>
                <input type='text'
                placeholder='Search for bus'
                className='search-input'
                 />
                <button type='submit' className='search-button'>Search</button>
            </form> */}
            <div className='navbar-links'>
                <Link to='/'>Home </Link>
                <Link to='/allbuses'>Bus Information</Link>
                <Link to='/map'>Map</Link>
                <Link to='/help'>Help</Link>
            </div>
        </nav>
    )
}

export default NavBar;