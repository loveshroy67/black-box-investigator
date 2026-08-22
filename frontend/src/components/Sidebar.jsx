import { NavLink } from "react-router-dom";
import BackendStatus from "./BackendStatus";

const links = [
  ["/", "Dashboard", "⌂"],
  ["/incidents", "Incidents", "◈"],
  ["/timeline", "Timeline", "◷"],
  ["/evidence", "Evidence", "⌁"],
  ["/investigation", "Investigation", "✦"],
];

function Sidebar({ incidentId }) {
  return (
    <aside className="sidebar">
      <div className="brand"><span className="brand-mark">BB</span><span><strong>BLACK BOX</strong><small>INVESTIGATOR</small></span></div>
      <nav className="sidebar-nav" aria-label="Primary navigation">
        {links.map(([to, label, icon]) => <NavLink key={to} to={to} className={({ isActive }) => `nav-link${isActive ? " active" : ""}`}><span className="nav-icon">{icon}</span>{label}</NavLink>)}
      </nav>
      <div className="sidebar-bottom">
        <BackendStatus />
        <div className="incident-mini"><span>Active case</span><strong>{incidentId}</strong></div>
      </div>
    </aside>
  );
}

export default Sidebar;
