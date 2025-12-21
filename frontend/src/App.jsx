import { Routes, Route } from "react-router-dom";
import Splash from "./pages/Splash";
import AuthPage from "./pages/AuthPage";
import Dashboard from "./pages/Dashboard";
import SearchFlights from "./pages/SearchFlights";
import FlightResults from "./pages/FlightResults";
import Weather from "./pages/Weather";
import PricePrediction from "./pages/PricePrediction";

export default function App() {
  return (
    <Routes>
      <Route path="/" element={<Splash />} />
      <Route path="/auth" element={<AuthPage />} />
      <Route path="/login" element={<AuthPage />} />
      <Route path="/register" element={<AuthPage />} />

      {/* Post-login */}
      <Route path="/dashboard" element={<Dashboard />} />
      <Route path="/search" element={<SearchFlights />} />
      <Route path="/results" element={<FlightResults />} />




      {/* Smart features */}
      <Route path="/weather" element={<Weather />} />
      <Route path="/price" element={<PricePrediction />} />
    </Routes>
  );
}