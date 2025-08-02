import { useAuth0 } from "@auth0/auth0-react";

function Home() {
    const {loginWithRedirect, isAuthenticated, isLoading, logout} = useAuth0();

    return (
        <div className="home-container">
            <h1>Welcome to the Home Page</h1>
            {!isAuthenticated && !isLoading && (
                <button onClick={() => loginWithRedirect({appState: {returnTo: '/dashboard'}})}>
                    Log In
                </button>
            )}
            {isAuthenticated && (
                <div>
                    <p>You are logged in!</p>
                    <button onClick={() => logout()}>
                        Log Out
                    </button>
                </div>
            )}
        </div>
    );
}

export default Home;