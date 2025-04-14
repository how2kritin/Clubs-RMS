// AuthProvider.tsx
import { createContext, useEffect, useState } from 'react';

interface AuthContextType {
  isLoggedIn: boolean;
  login: () => void;
  logout: () => void;
}

export const AuthContext = createContext<AuthContextType>({
  isLoggedIn: false,
  login: () => {},
  logout: () => {}
});

export const AuthProvider = ({ children }: { children: React.ReactNode }) => {
  const [isLoggedIn, setIsLoggedIn] = useState(false);

  useEffect(() => {
    // Call validation endpoint on mount using credentials (the token is stored as an HTTP-only cookie)
    fetch("/api/user/is_authenticated", {
      method: "GET",
      credentials: "include"
    })
      .then((res) => {
        if (res.ok) {
          return res.json();
        }
        throw new Error("Not logged in");
      })
      .then(data => {
        if (data.authenticated) {
          setIsLoggedIn(true);
          // localStorage.setItem("isLoggedIn", "true");
        } else {
          setIsLoggedIn(false);
          // localStorage.setItem("isLoggedIn", "false");
        }
      })
      .catch(error => {
        console.error("Token validation error:", error);
        setIsLoggedIn(false);
        // localStorage.setItem("isLoggedIn", "false");
      });
  }, []);

  const login = () => {
    setIsLoggedIn(true);
    // localStorage.setItem("isLoggedIn", "true");
  };

  const logout = () => {
    setIsLoggedIn(false);
    // localStorage.setItem("isLoggedIn", "false");
  };

  return (
    <AuthContext.Provider value={{ isLoggedIn, login, logout }}>
      {children}
    </AuthContext.Provider>
  );
};
