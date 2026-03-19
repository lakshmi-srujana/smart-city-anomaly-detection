import axios from "axios";

const api = axios.create({
  baseURL: "http://localhost:8000",
});

function handleApiError(error, fallbackMessage) {
  const message =
    error?.response?.data?.detail ||
    error?.response?.data?.message ||
    error?.message ||
    fallbackMessage;

  console.error(fallbackMessage, error);
  return {
    error: true,
    message,
  };
}

export async function fetchHealth() {
  try {
    const response = await api.get("/api/health");
    return response.data;
  } catch (error) {
    return handleApiError(error, "Failed to fetch health status.");
  }
}

export async function fetchData() {
  try {
    const response = await api.get("/api/data");
    return response.data;
  } catch (error) {
    return handleApiError(error, "Failed to fetch power data.");
  }
}

export async function runPrediction(modelName) {
  try {
    const response = await api.post(`/api/predict/${modelName}`);
    return response.data;
  } catch (error) {
    return handleApiError(error, `Failed to run prediction for ${modelName}.`);
  }
}

export async function fetchLogs(modelName = null) {
  try {
    const response = await api.get("/api/logs", {
      params: modelName ? { model: modelName } : {},
    });
    return response.data;
  } catch (error) {
    return handleApiError(error, "Failed to fetch anomaly logs.");
  }
}

export async function fetchMetrics() {
  try {
    const response = await api.get("/api/metrics");
    return response.data;
  } catch (error) {
    return handleApiError(error, "Failed to fetch model metrics.");
  }
}
