import {
  Bar,
  BarChart,
  CartesianGrid,
  Legend,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";

function buildChartData(metrics) {
  if (!Array.isArray(metrics) || metrics.length === 0) {
    return [];
  }

  const latestByModel = new Map();

  metrics.forEach((entry) => {
    if (!latestByModel.has(entry.model_name)) {
      latestByModel.set(entry.model_name, entry);
    }
  });

  const latestMetrics = Array.from(latestByModel.values());
  const maxInferenceTime = Math.max(
    ...latestMetrics.map((entry) => Number(entry.inference_time_ms) || 0),
    1,
  );

  return latestMetrics.map((entry) => ({
    model_name: entry.model_name,
    anomaly_rate: Number(((Number(entry.anomaly_rate) || 0) * 100).toFixed(2)),
    inference_time_normalized: Number(
      ((((Number(entry.inference_time_ms) || 0) / maxInferenceTime) * 100)).toFixed(2),
    ),
  }));
}

export function ComparisonChart({ metrics }) {
  const chartData = buildChartData(metrics);

  return (
    <section className="rounded-3xl bg-gray-900 p-5">
      <div className="mb-5">
        <h3 className="text-xl font-semibold text-white">Model Comparison</h3>
      </div>

      {chartData.length === 0 ? (
        <div className="flex h-80 items-center justify-center rounded-2xl border border-dashed border-gray-800 text-sm text-gray-500">
          No model metrics available yet.
        </div>
      ) : (
        <div className="h-80">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={chartData} barGap={10}>
              <CartesianGrid strokeDasharray="3 3" stroke="#1f2937" />
              <XAxis dataKey="model_name" stroke="#94a3b8" />
              <YAxis stroke="#94a3b8" domain={[0, 100]} />
              <Tooltip
                contentStyle={{
                  backgroundColor: "#020617",
                  border: "1px solid #1f2937",
                  borderRadius: 16,
                }}
              />
              <Legend />
              <Bar
                dataKey="anomaly_rate"
                name="Anomaly Rate (%)"
                fill="#818cf8"
                radius={[6, 6, 0, 0]}
              />
              <Bar
                dataKey="inference_time_normalized"
                name="Inference Time (0-100)"
                fill="#34d399"
                radius={[6, 6, 0, 0]}
              />
            </BarChart>
          </ResponsiveContainer>
        </div>
      )}
    </section>
  );
}
