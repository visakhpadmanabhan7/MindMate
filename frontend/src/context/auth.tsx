"use client";

import { createContext, useContext, useState, useEffect, ReactNode } from "react";

interface AuthContextType {
  email: string | null;
  ready: boolean;
  login: (email: string) => void;
  logout: () => void;
}

const AuthContext = createContext<AuthContextType>({
  email: null,
  ready: false,
  login: () => {},
  logout: () => {},
});

export function AuthProvider({ children }: { children: ReactNode }) {
  const [email, setEmail] = useState<string | null>(null);
  const [ready, setReady] = useState(false);

  useEffect(() => {
    const stored = localStorage.getItem("mindmate_email");
    if (stored) setEmail(stored);
    setReady(true);
  }, []);

  const login = (email: string) => {
    setEmail(email);
    localStorage.setItem("mindmate_email", email);
  };

  const logout = () => {
    setEmail(null);
    localStorage.removeItem("mindmate_email");
  };

  // Don't render children until hydration is complete
  if (!ready) return null;

  return (
    <AuthContext.Provider value={{ email, ready, login, logout }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  return useContext(AuthContext);
}
