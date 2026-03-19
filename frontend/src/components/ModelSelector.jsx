import { BrainCircuit, Radar, ShieldAlert } from "lucide-react";

const models = [
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

export function ModelSelector({
  selectedModel,
  setSelectedModel,
  onRunDetection,
  loading,
}) {
  return (
    <div className="space-y-4">
      <div className="space-y-3">
        {models.map((model) => {
          const Icon = model.icon;
          const isActive = selectedModel === model.key;

          return (
            <button
              key={model.key}
              type="button"
              onClick={() => setSelectedModel(model.key)}
              className={`flex w-full items-center gap-3 rounded-xl px-4 py-3 text-left transition ${
                isActive
                  ? "bg-indigo-600 text-white"
                  : "bg-gray-800 text-gray-300 hover:bg-gray-700"
              }`}
            >
              <Icon className="h-5 w-5" />
              <span className="text-sm font-medium">{model.label}</span>
            </button>
          );
        })}
      </div>

      <button
        type="button"
        onClick={onRunDetection}
        disabled={loading}
        className="w-full rounded-xl bg-indigo-500 px-4 py-3 font-semibold text-white transition hover:bg-indigo-600 disabled:cursor-not-allowed disabled:opacity-60"
      >
        {loading ? "Running..." : "Run Detection"}
      </button>
    </div>
  );
}
