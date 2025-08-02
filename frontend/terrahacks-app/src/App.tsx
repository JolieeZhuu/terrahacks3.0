import './App.css'
// Pages
import Home from './pages/home'
import Dashboard from './pages/dashboard'
import VerticalOverlapCarousel from './components/phrasebook'

// routing
import {
    HashRouter as Router,
    Routes,
    Route,
    Navigate
} from 'react-router-dom'
import { PrivateRoute } from './auth/privateRoute'

export default function App() {
  return (
    <Routes>
      <Route path="/" element={<Home/>}/>
      <Route path="/dashboard" element={<PrivateRoute><Dashboard/></PrivateRoute>}/>
      <Route path="/phrasebook" element={<PrivateRoute><VerticalOverlapCarousel/></PrivateRoute>}/>
      <Route path="*" element={<Navigate to="/"/>}/>
    </Routes>
  );
}



/*
import { useAuth0 } from "@auth0/auth0-react";
import { useEffect } from 'react';
import './App.css'
import Dashboard from './components/dashboard'
import Phrasebook from './components/phrasebook'

// routing
import {
    HashRouter as Router,
    Routes,
    Route,
    Navigate,
    useNavigate
} from 'react-router-dom'

function AuthenticatedApp() {
  const { logout, user, getAccessTokenSilently } = useAuth0();
  const navigate = useNavigate();

  const callProtectedAPI = async () => {
    const token = await getAccessTokenSilently();
    const res = await fetch("http://localhost:5000/api/protected", {
      headers: {
        Authorization: `Bearer ${token}`
      }
    });
    const data = await res.json();
    console.log(data);
  };

  return (
    <>
      <nav style={{ padding: '1rem', borderBottom: '1px solid #ccc' }}>
        <button onClick={() => logout({ returnTo: window.location.origin })}>
          Log Out
        </button>
        <span style={{ marginLeft: '1rem' }}>Hello {user?.name}</span>
        <button onClick={callProtectedAPI} style={{ marginLeft: '1rem' }}>
          Call Protected API
        </button>
      </nav>
      
      <Routes>
        <Route path="/" element={<Dashboard/>}/>
        <Route path="/phrasebook" element={<Phrasebook/>}/>
        <Route path="*" element={<Navigate to="/"/>}/>
      </Routes>
    </>
  );
}

export default function App() {
  const { loginWithRedirect, isAuthenticated, isLoading } = useAuth0();

  if (isLoading) {
    return <div>Loading...</div>;
  }

  return (
    <Router>
      <div>
        {!isAuthenticated ? (
          <div style={{ padding: '2rem', textAlign: 'center' }}>
            <h1>Welcome</h1>
            <button 
              onClick={() => loginWithRedirect({
                redirectUri: `${window.location.origin}/#/`
              })}
            >
              Log In
            </button>
          </div>
        ) : (
          <AuthenticatedApp />
        )}
      </div>
    </Router>
  );
}
*/