import Navbar from "../components/Navbar";
import heroImage from "../assets/dashboard-hero4.jpeg";
import "./dashboard.css";

export default function Dashboard() {
  return (
    <>
      <Navbar />

      <section className="hero">
        <img src={heroImage} alt="plane" className="hero-plane" />

        <div className="hero-content">
          <span className="greeting">Hello, Jeevitha 👋</span>

          <h1>
            Plan smarter.<br />
            Fly with confidence.
          </h1>

          <p>Your journey begins with the right decision.</p>

          <button>Search Flights</button>
        </div>
      </section>
    </>
  );
}
