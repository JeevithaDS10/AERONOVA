import "./navbar.css";

export default function Navbar() {
  return (
    <nav className="navbar">
      <div className="nav-left">
        ✈️ <span>AeroNova</span>
      </div>

      <ul className="nav-center">
        <li>Home</li>
        <li>Flights</li>
        <li>Price Prediction</li>
        <li>Weather</li>
        <li>My Trips</li>
      </ul>

      <div className="nav-right">
        <div className="live-text">
          ✨ New routes added • Fare alerts enabled • Travel smart ✨
        </div>
        <div className="profile">👤</div>
      </div>
    </nav>
  );
}
