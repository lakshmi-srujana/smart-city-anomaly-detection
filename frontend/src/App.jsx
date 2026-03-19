import { useEffect, useMemo, useState } from "react";
import {
  Activity,
  BrainCircuit,
  ChartColumn,
  Radar,
  ShieldAlert,
  Zap,
} from "lucide-react";

import {
  fetchData,
  fetchLogs,
  fetchMetrics,
  runPrediction,
} from "./api/client";
import {
  AnomalyChart,
  AnomalyTable,
  ComparisonChart,
  MetricCard,
} from "./components";

const MODELS = [
  {
    key: "isolation_forest",
    label: "Isolation Forest",
    icon: ShieldAlert,
  },
  {
    key: "lstm",
    label: "LSTM Autoencoder",
    icon: BrainCircuit,
  },
  {
    key: "ocsvm",
    label: "One-Class SVM",
    icon: Radar,
  },
];

function App() {
  const [selectedModel, setSelectedModel] = useState("isolation_forest");
  const [predictionData, setPredictionData] = useState(null);
  const [logs, setLogs] = useState([]);
  const [metrics, setMetrics] = useState([]);
  const [loading, setLoading] = useState(false);
  const [seriesData, setSeriesData] = useState({ timestamps: [], values: [] });
  const [error, setError] = useState("");

  useEffect(() => {
    async function loadDashboardData() {
      setLoading(true);
      setError("");

      const [dataResponse, metricsResponse] = await Promise.all([
        fetchData(),
        fetchMetrics(),
      ]);

      if (dataResponse?.error) {
        setError(dataResponse.message);
      } else {
        setSeriesData(dataResponse);
      }

      if (metricsResponse?.error) {
        setError((current) => current || metricsResponse.message);
      } else {
        setMetrics(metricsResponse);
      }

      setLoading(false);
    }

    loadDashboardData();
  }, []);

  const totalPoints = predictionData?.values?.length ?? seriesData.values?.length ?? 0;
  const anomalyCount = predictionData?.anomaly_count ?? 0;
  const anomalyRate = ((predictionData?.anomaly_rate ?? 0) * 100).toFixed(2);

  const chartData = useMemo(() => {
    if (predictionData?.timestamps?.length) {
      return predictionData.timestamps.map((timestamp, index) => ({
        timestamp,
        value: predictionData.values[index],
        anomaly: predictionData.anomalies[index] ? predictionData.values[index] : null,
        reconstructionError: predictionData.reconstruction_errors?.[index] ?? null,
      }));
    }

    return (seriesData.timestamps || []).map((timestamp, index) => ({
      timestamp,
      value: seriesData.values[index],
      anomaly: null,
      reconstructionError: null,
    }));
  }, [predictionData, seriesData]);

  async function handleRunDetection() {
    setLoading(true);
    setError("");

    const predictionResponse = await runPrediction(selectedModel);
    if (predictionResponse?.error) {
      setError(predictionResponse.message);
      setLoading(false);
      return;
    }

    setPredictionData(predictionResponse);

    const [logsResponse, metricsResponse] = await Promise.all([
      fetchLogs(selectedModel),
      fetchMetrics(),
    ]);

    if (logsResponse?.error) {
      setError((current) => current || logsResponse.message);
    } else {
      setLogs(logsResponse);
    }

    if (metricsResponse?.error) {
      setError((current) => current || metricsResponse.message);
    } else {
      setMetrics(metricsResponse);
    }

    setLoading(false);
  }

  return (
    <div className="min-h-screen bg-gray-950 text-gray-100">
      <div className="flex min-h-screen flex-col lg:flex-row">
        <aside className="w-full border-b border-gray-800 bg-gray-950/95 px-6 py-8 lg:w-64 lg:border-b-0 lg:border-r">
          <div className="flex items-center gap-3">
            <div className="rounded-2xl bg-cyan-500/15 p-3 text-cyan-300">
              <Zap className="h-6 w-6" />
            </div>
            <div>
              <p className="text-xs font-semibold uppercase tracking-[0.3em] text-cyan-300">
                Smart City
              </p>
              <h1 className="text-xl font-semibold text-white">Anomaly Monitor</h1>
            </div>
          </div>

          <div className="mt-10">
            <p className="mb-4 text-xs font-semibold uppercase tracking-[0.28em] text-gray-500">
              Models
            </p>
            <div className="space-y-3">
              {MODELS.map((model) => {
                const Icon = model.icon;
                const isSelected = selectedModel === model.key;

                return (
                  <button
                    key={model.key}
                    type="button"
                    onClick={() => setSelectedModel(model.key)}
                    className={`flex w-full items-center gap-3 rounded-2xl border px-4 py-3 text-left transition ${
                      isSelected
                        ? "border-cyan-400 bg-cyan-400/10 text-white"
                        : "border-gray-800 bg-gray-900/70 text-gray-300 hover:border-gray-700 hover:bg-gray-900"
                    }`}
                  >
                    <Icon className="h-5 w-5" />
                    <span className="text-sm font-medium">{model.label}</span>
                  </button>
                );
              })}
            </div>
          </div>

          <button
            type="button"
            onClick={handleRunDetection}
            disabled={loading}
            className="mt-8 flex w-full items-center justify-center gap-2 rounded-2xl bg-cyan-400 px-4 py-3 font-semibold text-gray-950 transition hover:bg-cyan-300 disabled:cursor-not-allowed disabled:opacity-60"
          >
            <Activity className="h-4 w-4" />
            {loading ? "Running..." : "Run Detection"}
          </button>

          <div className="mt-8 rounded-2xl border border-gray-800 bg-gray-900/60 p-4">
            <p className="text-xs uppercase tracking-[0.28em] text-gray-500">Status</p>
            <p className="mt-2 text-sm text-gray-300">
              {error || "Backend connected. Ready to run anomaly detection."}
            </p>
          </div>
        </aside>

        <main className="flex-1 px-6 py-8 lg:px-8">
          <div className="mx-auto max-w-7xl">
            <div className="mb-8 flex flex-col gap-3 md:flex-row md:items-end md:justify-between">
              <div>
                <p className="text-sm font-medium uppercase tracking-[0.28em] text-cyan-300">
                  Real-Time Analytics
                </p>
                <h2 className="mt-2 text-3xl font-semibold text-white">
                  Household Power Anomaly Dashboard
                </h2>
              </div>
              <div className="text-sm text-gray-400">
                Active model:{" "}
                <span className="font-medium text-white">
                  {MODELS.find((model) => model.key === selectedModel)?.label}
                </span>
              </div>
            </div>

            <div className="grid gap-4 md:grid-cols-3">
              <MetricCard
                title="Total Points"
                value={totalPoints.toLocaleString()}
                subtitle="Current series window"
                icon={ChartColumn}
              />
              <MetricCard
                title="Anomalies"
                value={anomalyCount.toLocaleString()}
                subtitle="Detected in latest run"
                icon={ShieldAlert}
              />
              <MetricCard
                title="Anomaly Rate %"
                value={anomalyRate}
                subtitle="Share of flagged records"
                icon={Activity}
              />
            </div>

            <div className="mt-6">
              <AnomalyChart data={chartData} loading={loading} />
            </div>

            <div className="mt-6 grid gap-6 xl:grid-cols-[1.2fr_0.8fr]">
              <ComparisonChart metrics={metrics} />
              <AnomalyTable logs={logs} />
            </div>
          </div>
        </main>
      </div>
    </div>
  );
}

export default App;
