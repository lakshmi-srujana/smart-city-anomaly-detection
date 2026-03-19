import {
  CartesianGrid,
  Legend,
  Line,
  ResponsiveContainer,
  Scatter,
  Tooltip,
  XAxis,
  YAxis,
  ComposedChart,
} from "recharts";

export function AnomalyChart({ data, loading }) {
  return (
    <section className="rounded-3xl border border-gray-800 bg-gray-900/75 p-5">
      <div className="mb-5 flex items-center justify-between">
        <div>
          <p className="text-sm font-medium uppercase tracking-[0.24em] text-cyan-300">
            Signal View
          </p>
          <h3 className="mt-2 text-xl font-semibold text-white">Anomaly Chart</h3>
        </div>
        <p className="text-sm text-gray-500">
          {loading ? "Refreshing..." : `${data.length} records loaded`}
        </p>
      </div>

      <div className="h-96">
        <ResponsiveContainer width="100%" height="100%">
          <ComposedChart data={data}>
            <CartesianGrid strokeDasharray="3 3" stroke="#1f2937" />
            <XAxis dataKey="timestamp" hide />
            <YAxis stroke="#94a3b8" />
            <Tooltip
              contentStyle={{
                backgroundColor: "#020617",
                border: "1px solid #1f2937",
                borderRadius: 16,
              }}
              labelStyle={{ color: "#e2e8f0" }}
            />
            <Legend />
            <Line
              type="monotone"
              dataKey="value"
              stroke="#22d3ee"
              strokeWidth={2}
              dot={false}
              name="Power"
            />
            <Scatter
              dataKey="anomaly"
              fill="#f97316"
              name="Anomaly"
            />
          </ComposedChart>
        </ResponsiveContainer>
      </div>
    </section>
  );
}
