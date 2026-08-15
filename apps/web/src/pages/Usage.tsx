export default function Usage() {
  return (
    <div>
      <h1 className="text-2xl font-bold mb-6">Usage & Analytics</h1>
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
        <div className="p-6 bg-gray-900 rounded-xl border border-gray-800">
          <p className="text-sm text-gray-400">This Month</p>
          <p className="text-2xl font-bold mt-1">0 requests</p>
        </div>
        <div className="p-6 bg-gray-900 rounded-xl border border-gray-800">
          <p className="text-sm text-gray-400">Today</p>
          <p className="text-2xl font-bold mt-1">0 requests</p>
        </div>
        <div className="p-6 bg-gray-900 rounded-xl border border-gray-800">
          <p className="text-sm text-gray-400">Estimated Cost</p>
          <p className="text-2xl font-bold mt-1">₹0.00</p>
        </div>
      </div>
      <div className="p-12 bg-gray-900 rounded-xl border border-gray-800 text-center">
        <p className="text-4xl mb-4">📈</p>
        <h2 className="text-lg font-semibold text-gray-300">No usage data yet</h2>
        <p className="text-sm text-gray-500 mt-2">
          Usage charts will appear once you start making API calls.
        </p>
      </div>
    </div>
  );
}
