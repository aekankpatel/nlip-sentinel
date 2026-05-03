const configuredBackend = import.meta.env.VITE_BACKEND_URL || "http://localhost:8000";
const localFallbacks = ["http://localhost:8000", "http://localhost:8001"];
const BACKEND_URLS = import.meta.env.PROD
  ? [configuredBackend]
  : Array.from(new Set([configuredBackend, ...localFallbacks]));

async function requestBackend(path, options = {}) {
  let lastError;
  for (const baseUrl of BACKEND_URLS) {
    try {
      const response = await fetch(`${baseUrl}${path}`, options);
      if (response.ok) return response.json();
      lastError = new Error(`Backend ${baseUrl} returned ${response.status}`);
    } catch (error) {
      lastError = error;
    }
  }
  throw lastError || new Error("Backend request failed");
}

export async function runWorkflow(question) {
  return requestBackend("/api/run-workflow", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ question }),
  });
}

export async function loadDemo() {
  return requestBackend("/api/demo");
}
