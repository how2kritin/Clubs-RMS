

const App = () => {
  // Handle login button click using standard navigation
  const handleLoginClick = async () => {
    const username = "ashutosh.rudrabhatla@research.iiit.ac.in";
    const password = "password";
  
    const formData = new URLSearchParams();
    formData.append('username', username);
    formData.append('password', password);
  
    try {
      // Use the proxy path '/api' which maps to your backend
      const response = await fetch('/api/user/login', {  // Updated path
        method: 'GET',
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded'
        },
        body: formData.toString(),
        credentials: 'include'  // Keep this for session cookies
      });
  
      if (response.ok) {
        const data = await response.json();
        console.log('Logged in successfully:', data);
      } else {
        const errorText = await response.text();
        console.error('Login failed:', response);
      }
    } catch (error) {
      console.error('Network error:', error);
    }
  };
  

  return (
    <div className="min-h-screen flex flex-col transition-colors duration-300 bg-gray-100 dark:bg-gray-900">
      {/* Top right theme toggle */}

      {/* Main content */}
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

      {/* Footer */}
      <footer className="py-6 text-center text-gray-600 dark:text-gray-400">
        <p>© {new Date().getFullYear()} Clubs++@IIITH. All rights reserved.</p>
      </footer>
    </div>
  );
};

export default App;