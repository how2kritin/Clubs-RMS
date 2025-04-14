import { useContext } from "react";
import { AuthContext } from "../AuthProvider.tsx";

const LandingPage = () => {
  const { isLoggedIn, login, logout } = useContext(AuthContext);

  const handleOnClick = async () => {
    if(!isLoggedIn){
        login()
        try {
        const response = await fetch("/api/user/login", {
            method: "POST",
            credentials: "include",
        });
        // redirect to CAS
        const { loginUrl } = await response.json();
        window.location.href = loginUrl;
        } catch (error) {
        console.error("Login failed:", error);
        }
    }
    else{
        try {
            logout()
            const response = await fetch("/api/user/logout", {
                method: "POST",
                credentials: "include",
            });
            if (response.ok) {
                // call logout to update the context state
                logout();
            } else {
                console.error("Logout failed: ", response.statusText);
            }
        } catch (error) {
            console.error("Logout failed:", error);
        }
    }
  };

  return (
    <div className="flex-grow flex flex-col items-center justify-center px-4">
      <div className="text-center">
        <h1 className="text-4xl md:text-6xl font-bold mb-8 text-indigo-700 dark:text-indigo-400">
          Clubs++@IIITH
        </h1>
        <p className="text-xl mb-10 max-w-2xl text-gray-700 dark:text-gray-300">
          A comprehensive recruitment management system for clubs and organizations at IIIT Hyderabad
        </p>
        <button
          onClick={handleOnClick}
          className="px-8 py-3 text-lg font-medium rounded-md bg-indigo-600 text-white hover:bg-indigo-700 dark:bg-indigo-700 dark:hover:bg-indigo-800 transition-colors duration-200"
        >
          {isLoggedIn ? "Logout" : "Login"}
        </button>
      </div>
    </div>
  );
};

export default LandingPage;
