import { useEffect, useState } from "react";
import { BrowserRouter, Navigate, Route, Routes, useLocation } from "react-router-dom";
import "./index.css";
import Sidebar from "./components/Sidebar";
import Topbar from "./components/Topbar";
import ErrorMessage from "./components/ErrorMessage";
import LoadingState from "./components/LoadingState";
import Dashboard from "./pages/Dashboard";
import Incidents from "./pages/Incidents";
import TimelinePage from "./pages/TimelinePage";
import Evidence from "./pages/Evidence";
import Investigation from "./pages/Investigation";
import { getInvestigation, getTimeline, investigateIncident, uploadEvidence } from "./services/api";

const INCIDENT_ID = "INC-001";
const pageTitles = {
  "/": "Incident Investigation",
  "/incidents": "Incidents",
  "/timeline": "Timeline",
  "/evidence": "Evidence",
  "/investigation": "Investigation",
};

const deduplicateEvents = (data) => {
  if (!data?.events) return data;

  const seen = new Set();
  const events = data.events.filter((event) => {
    const signature = [
      event.timestamp,
      event.type,
      event.severity,
      event.event,
      event.title,
      event.message,
      event.description,
      event.source,
    ].join("|");

    if (seen.has(signature)) return false;
    seen.add(signature);
    return true;
  });

  return { ...data, events, total_events: events.length };
};

function Workspace() {
  const location = useLocation();
  const [timeline, setTimeline] = useState(null);
  const [investigation, setInvestigation] = useState(null);
  const [latestEvidence, setLatestEvidence] = useState(null);
  const [loading, setLoading] = useState(true);
  const [uploading, setUploading] = useState(false);
  const [refreshing, setRefreshing] = useState(false);
  const [error, setError] = useState("");

  const refreshTimeline = async () => {
    setRefreshing(true);
    try {
      setTimeline(deduplicateEvents(await getTimeline(INCIDENT_ID)));
      setError("");
    } catch (refreshError) {
      setError(refreshError instanceof Error ? refreshError.message : "Unable to load timeline");
    } finally {
      setRefreshing(false);
    }
  };

  useEffect(() => {
    let active = true;

    const loadInitialData = async () => {
      const [timelineResult, investigationResult] = await Promise.allSettled([
        getTimeline(INCIDENT_ID),
        getInvestigation(INCIDENT_ID),
      ]);

      if (!active) return;

      if (timelineResult.status === "fulfilled") {
        setTimeline(deduplicateEvents(timelineResult.value));
      } else {
        setError("Unable to load incident timeline");
      }

      if (investigationResult.status === "fulfilled") {
        setInvestigation(investigationResult.value);
      } else if (![400, 404].includes(investigationResult.reason?.status)) {
        setError("Unable to load investigation data");
      }

      setLoading(false);
    };

    loadInitialData().catch(() => {
      if (active) {
        setError("Unable to connect to backend");
        setLoading(false);
      }
    });

    return () => { active = false; };
  }, []);

  const handleInvestigate = async () => {
    setLoading(true);
    setError("");
    try {
      const triggerResult = await investigateIncident(INCIDENT_ID);
      const refreshedInvestigation = await getInvestigation(INCIDENT_ID);

      setInvestigation({
        ...refreshedInvestigation,
        source: triggerResult.source,
      });
      await refreshTimeline();
    } catch (investigationError) {
      setError(investigationError instanceof Error ? investigationError.message : "Investigation failed");
    } finally {
      setLoading(false);
    }
  };

  const handleUpload = async (file) => {
    setUploading(true);
    setError("");
    setInvestigation(null);
    try {
      setLatestEvidence(await uploadEvidence(INCIDENT_ID, file));
      await refreshTimeline();
    } catch (uploadError) {
      setError(uploadError instanceof Error ? uploadError.message : "Evidence upload failed");
    } finally {
      setUploading(false);
    }
  };

  if (loading && !timeline) return <LoadingState label="Connecting to incident workspace" />;

  return <div className="app-shell"><Sidebar incidentId={INCIDENT_ID} /><div className="main-content main-area"><Topbar title={pageTitles[location.pathname] || "Incident Investigation"} incidentId={INCIDENT_ID} onRefresh={refreshTimeline} refreshing={refreshing} /><ErrorMessage message={error} onDismiss={() => setError("")} /><Routes><Route path="/" element={<Dashboard incidentId={INCIDENT_ID} timeline={timeline} investigation={investigation} latestEvidence={latestEvidence} loading={loading} uploading={uploading} onInvestigate={handleInvestigate} onUpload={handleUpload} />} /><Route path="/incidents" element={<Incidents incidentId={INCIDENT_ID} investigation={investigation} timeline={timeline} />} /><Route path="/timeline" element={<TimelinePage timeline={timeline} />} /><Route path="/evidence" element={<Evidence latestEvidence={latestEvidence} onUpload={handleUpload} uploading={uploading} />} /><Route path="/investigation" element={<Investigation investigation={investigation} onInvestigate={handleInvestigate} loading={loading} />} /><Route path="*" element={<Navigate to="/" replace />} /></Routes></div></div>;
}

function App() {
  return <BrowserRouter><Workspace /></BrowserRouter>;
}

export default App;
