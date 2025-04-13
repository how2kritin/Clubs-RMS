// App.js (React Component)

const App = () => {
    const handleLoginClick = async () => {
        try {
            const response = await fetch("/api/user/login", {
                method: "POST", credentials: "include",
            });
            // redirect to CAS
            const {loginUrl} = await response.json();
            window.location.href = loginUrl
        } catch (error) {
            console.error("Login failed:", error);
        }
    };

    return (<div className="min-h-screen flex flex-col transition-colors duration-300 bg-gray-100 dark:bg-gray-900">
            <main className="flex-grow flex flex-col items-center justify-center px-4">
                <div className="text-center">
                    <h1 className="text-4xl md:text-6xl font-bold mb-8 text-indigo-700 dark:text-indigo-400">
                        Clubs++@IIITH
                    </h1>
                    <p className="text-xl mb-10 max-w-2xl text-gray-700 dark:text-gray-300">
                        A comprehensive recruitment management system for clubs and organizations at IIIT Hyderabad
                    </p>
                    <button
                        onClick={handleLoginClick}
                        className="px-8 py-3 text-lg font-medium rounded-md bg-indigo-600 text-white hover:bg-indigo-700 dark:bg-indigo-700 dark:hover:bg-indigo-800 transition-colors duration-200"
                    >
                        Login
                    </button>
                </div>
            </main>
            <footer className="py-6 text-center text-gray-600 dark:text-gray-400">
                <p>© {new Date().getFullYear()} Clubs++@IIITH. All rights reserved.</p>
            </footer>
        </div>);
};

export default App;
