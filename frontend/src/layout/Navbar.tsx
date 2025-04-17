import {useEffect, useState} from 'react';
import {Link, useLocation} from 'react-router-dom';
import {motion} from 'framer-motion';

import {useAuth} from '../AuthProvider'; // Adjust the path if needed

// Define the Navbar component
const Navbar = () => {
    const location = useLocation();
    const [activePath, setActivePath] = useState('');
    const {isLoggedIn, logout} = useAuth();

    useEffect(() => {
        setActivePath(location.pathname);
    }, [location.pathname]);

    // Define the routes for the navbar.  This should match your router.
    const navRoutes = [{path: '/dashboard', label: 'Dashboard'}, {path: '/profile', label: 'Profile'}, {
        path: '/clubs', label: 'Clubs'
    }, {path: '/calendar', label: 'Calendar'}, {path: '/my-applications', label: 'My Applications'},];

    // Only render the Navbar if the user is logged in
    if (!isLoggedIn) {
        return null;
    }
    const handleLogout = async () => {
        try {
            const response = await fetch("/api/user/logout", { //Removed fetch
                method: "POST", credentials: "include",
            });
            if (response.ok) {
                logout();
                const {logoutUrl} = await response.json();
                window.location.href = logoutUrl;
            } else {
                console.error("Logout failed: ", response.statusText);
            }
        } catch (error) {
            console.error("Logout failed:", error);
        }
    };

    return (<nav className="bg-gray-100 dark:bg-gray-900 p-4">
        <div className="container mx-auto flex justify-between items-center">
            <div className="flex gap-6 justify-center flex-grow">  {/* Added flex-grow to navLinks div */}
                {navRoutes.map((route) => (<motion.div
                    key={route.path}
                    whileHover={{scale: 1.1}}
                    transition={{type: "spring", stiffness: 400, damping: 17}}
                >
                    <Link to={route.path} className={`
                                text-black dark:text-gray-200
                                hover:text-white dark:hover:text-white
                                hover:bg-gray-500 dark:hover:bg-gray-800
                                px-4 py-3 rounded-md
                                ${activePath === route.path ? 'bg-gray-500 dark:bg-gray-800 text-white dark:text-white' : ''}
                                transition-colors duration-200
                            `}>
                        {route.label}
                    </Link>
                </motion.div>))}
            </div>
            <div className="absolute up-4 right-16">
                <motion.button
                    onClick={handleLogout}
                    whileHover={{scale: 1.1}}
                    transition={{type: "spring", stiffness: 400, damping: 17}}
                    className="text-black dark:text-gray-200
                            hover:text-white dark:hover:text-white
                            hover:bg-red-500 dark:hover:bg-red-500
                            px-4 py-2 rounded-md transition-colors duration-200"
                >
                    Logout
                </motion.button>
            </div>
        </div>
    </nav>);
};


export default Navbar;