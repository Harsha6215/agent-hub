export default function ApiKeys() {
  return (
    <div>
      <div className="flex items-center justify-between mb-6">
        <h1 className="text-2xl font-bold">API Keys</h1>
        <button className="px-4 py-2 bg-primary-600 hover:bg-primary-700 rounded-lg text-sm font-medium transition-colors">
          Create New Key
        </button>
      </div>
      <div className="p-12 bg-gray-900 rounded-xl border border-gray-800 text-center">
        <p className="text-4xl mb-4">🔑</p>
        <h2 className="text-lg font-semibold text-gray-300">No API keys created</h2>
        <p className="text-sm text-gray-500 mt-2">
          Create an API key to start calling agents programmatically.
        </p>
      </div>
    </div>
  );
}
