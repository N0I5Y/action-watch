import React from "react";
import ReactDOM from "react-dom/client";
import App from "./App.tsx";
import { AuthProvider } from "./contexts/AuthContext";
import { TimezoneProvider } from "./contexts/TimezoneContext";
import "./index.css";

ReactDOM.createRoot(document.getElementById("root") as HTMLElement).render(
  <React.StrictMode>
    <AuthProvider>
      <TimezoneProvider>
        <App />
      </TimezoneProvider>
    </AuthProvider>
  </React.StrictMode>
);

