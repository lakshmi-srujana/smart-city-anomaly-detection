export function MetricCard({ title, value, subtitle, icon: Icon }) {
  return (
    <div className="rounded-3xl border border-gray-800 bg-gray-900/75 p-5 shadow-[0_20px_80px_-40px_rgba(34,211,238,0.35)]">
      <div className="flex items-start justify-between gap-4">
        <div>
          <p className="text-sm font-medium text-gray-400">{title}</p>
          <p className="mt-3 text-3xl font-semibold text-white">{value}</p>
        </div>
        <div className="rounded-2xl bg-cyan-400/10 p-3 text-cyan-300">
          <Icon className="h-5 w-5" />
        </div>
      </div>
      <p className="mt-4 text-sm text-gray-500">{subtitle}</p>
    </div>
  );
}
