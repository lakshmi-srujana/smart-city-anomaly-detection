import { Activity, AlertTriangle, Clock3, Database } from "lucide-react";

function formatValue(value, suffix = "") {
  if (value === null || value === undefined) {
    return "--";
  }

  if (typeof value === "number") {
    return `${value.toLocaleString()}${suffix}`;
  }

  return `${value}${suffix}`;
}

const cards = [
  {
    key: "total",
    label: "Total Points",
    icon: Database,
    color: "text-indigo-300 bg-indigo-500/10",
    valueKey: "totalPoints",
  },
  {
    key: "anomalies",
    label: "Anomalies",
    icon: AlertTriangle,
    color: "text-red-300 bg-red-500/10",
    valueKey: "anomalyCount",
  },
  {
    key: "rate",
    label: "Anomaly Rate",
    icon: Activity,
    color: "text-amber-300 bg-amber-500/10",
    valueKey: "anomalyRate",
    suffix: "%",
  },
  {
    key: "time",
    label: "Inference Time",
    icon: Clock3,
    color: "text-emerald-300 bg-emerald-500/10",
    valueKey: "inferenceTime",
    suffix: " ms",
  },
];

export function MetricCards({
  totalPoints,
  anomalyCount,
  anomalyRate,
  inferenceTime,
  loading,
}) {
  const values = {
    totalPoints,
    anomalyCount,
    anomalyRate,
    inferenceTime,
  };

  return (
    <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
      {cards.map(({ key, label, icon: Icon, color, valueKey, suffix = "" }) => (
        <div
          key={key}
          className="rounded-xl bg-gray-900 p-6 shadow-[0_20px_60px_-35px_rgba(15,23,42,0.9)]"
        >
          <div className="flex items-start justify-between gap-4">
            <div className={`rounded-xl p-3 ${color}`}>
              <Icon className="h-5 w-5" />
            </div>
            {loading ? (
              <div className="h-4 w-16 animate-pulse rounded bg-gray-800" />
            ) : null}
          </div>

          <div className="mt-5 text-3xl font-semibold tracking-tight text-white">
            {loading ? (
              <div className="h-9 w-28 animate-pulse rounded bg-gray-800" />
            ) : (
              formatValue(values[valueKey], suffix)
            )}
          </div>

          <p className="mt-3 text-sm text-gray-400">{label}</p>
        </div>
      ))}
    </div>
  );
}
