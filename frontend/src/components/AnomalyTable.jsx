function formatNumber(value) {
  if (value === null || value === undefined || Number.isNaN(Number(value))) {
    return "--";
  }

  return Number(value).toFixed(4);
}

export function AnomalyTable({ logs }) {
  const rows = Array.isArray(logs) ? logs.slice(0, 15) : [];

  return (
    <section className="rounded-xl bg-gray-900 p-5">
      <div className="mb-5">
        <h3 className="text-xl font-semibold text-white">Recent Anomaly Logs</h3>
      </div>

      <div className="overflow-hidden rounded-xl border border-gray-800">
        <div className="overflow-x-auto">
          <table className="min-w-full text-left text-sm">
            <thead className="bg-gray-950 text-gray-400">
              <tr>
                <th className="px-4 py-3 font-medium">Timestamp</th>
                <th className="px-4 py-3 font-medium">Model</th>
                <th className="px-4 py-3 font-medium">Value</th>
                <th className="px-4 py-3 font-medium">Reconstruction Error</th>
                <th className="px-4 py-3 font-medium">Status</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-800 bg-gray-900 text-gray-200">
              {rows.length === 0 ? (
                <tr>
                  <td colSpan="5" className="px-4 py-8 text-center text-gray-500">
                    No anomaly logs available yet.
                  </td>
                </tr>
              ) : (
                rows.map((log, index) => (
                  <tr key={log.id ?? `${log.timestamp}-${log.model_name}-${index}`}>
                    <td className="px-4 py-3">{String(log.timestamp ?? "--")}</td>
                    <td className="px-4 py-3">{log.model_name ?? "--"}</td>
                    <td className="px-4 py-3">{formatNumber(log.value)}</td>
                    <td className="px-4 py-3">
                      {formatNumber(log.reconstruction_error)}
                    </td>
                    <td className="px-4 py-3">
                      <span
                        className={`inline-flex rounded-full px-2.5 py-1 text-xs font-semibold ${
                          log.is_anomaly
                            ? "bg-red-500/15 text-red-300"
                            : "bg-emerald-500/15 text-emerald-300"
                        }`}
                      >
                        {log.is_anomaly ? "Anomaly" : "Normal"}
                      </span>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>
    </section>
  );
}
