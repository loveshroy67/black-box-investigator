const API_URL = import.meta.env.VITE_API_URL || "http://127.0.0.1:8000";

async function request(path, options = {}) {
  const controller = new AbortController();
  const timeoutId = setTimeout(() => controller.abort(), 90000);

  try {
    const response = await fetch(`${API_URL}${path}`, {
      ...options,
      signal: options.signal || controller.signal,
    });
    const contentType = response.headers.get("content-type") || "";
    const payload = contentType.includes("application/json")
      ? await response.json()
      : await response.text();

    if (!response.ok) {
      const detail = typeof payload === "object" ? payload.detail : payload;
      const error = new Error(detail || `Request failed: ${response.status}`);
      error.status = response.status;
      throw error;
    }

    return payload;
  } catch (error) {
    if (error instanceof TypeError) {
      throw new Error(`Cannot connect to backend at ${API_URL}`, { cause: error });
    }

    if (error.name === "AbortError") {
      throw new Error(`Backend request timed out at ${API_URL}`, { cause: error });
    }

    throw error;
  } finally {
    clearTimeout(timeoutId);
  }
}

export function getTimeline(incidentId) {
  return request(`/incidents/${incidentId}/timeline`);
}

export function investigateIncident(incidentId) {
  return request(`/incidents/${incidentId}/investigate`, { method: "POST" });
}

export function getInvestigation(incidentId) {
  return request(`/incidents/${incidentId}/investigation`);
}

export function uploadEvidence(incidentId, file) {
  const formData = new FormData();
  formData.append("file", file);

  return request(`/incidents/${incidentId}/evidence`, {
    method: "POST",
    body: formData,
  });
}

export { API_URL };
