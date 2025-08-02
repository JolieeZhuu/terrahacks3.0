import {useAuth0} from "@auth0/auth0-react";
import type { JSX } from "react";
import {Navigate} from 'react-router-dom';

export function PrivateRoute({children}: { children: JSX.Element }) {
    const {isAuthenticated, isLoading} = useAuth0();

    if (isLoading) {
        return <div>Loading...</div>;
    }
    return isAuthenticated ? children : <Navigate to="/" replace />;
}