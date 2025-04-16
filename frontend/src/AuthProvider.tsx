// AuthProvider.tsx
import { createContext, useEffect, useContext, useState } from 'react';

interface AuthContextType {
  isLoggedIn: boolean | null;
  login: () => void;
  logout: () => void;
}

const AuthContext = createContext<AuthContextType>({
  isLoggedIn: null,
  login: () => { },
  logout: () => { }
});

export const AuthProvider = ({ children }: { children: React.ReactNode }) => {
  const [isLoggedIn, setIsLoggedIn] = useState<boolean | null>(null);

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
          console.log("authenticated at the start (session)")
          setIsLoggedIn(true);
        } else {
          console.log("not authenticated at the start (no session)")

          setIsLoggedIn(false);
        }
      })
      .catch(error => {
        console.error("Token validation error:", error);
        setIsLoggedIn(false);
      });
  }, []);

  const login = () => {
    setIsLoggedIn(true);
  };

  const logout = () => {
    setIsLoggedIn(false);
  };

  return (
    <AuthContext.Provider value={{ isLoggedIn, login, logout }}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = (): AuthContextType => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};