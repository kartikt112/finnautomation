"use client";
import { LogEntry } from "@/lib/api";

const statusColors: Record<string, string> = {
  running: "text-blue-600",
  success: "text-green-600",
  failed: "text-red-600",
};

export default function LogTable({ logs }: { logs: LogEntry[] }) {
  if (logs.length === 0) {
    return <p className="text-gray-500 text-sm py-4 text-center">No logs yet</p>;
  }

  return (
    <div className="overflow-x-auto">
      <table className="w-full text-sm">
        <thead className="bg-gray-50">
          <tr>
            <th className="text-left px-4 py-3 font-medium text-gray-500">Time</th>
            <th className="text-left px-4 py-3 font-medium text-gray-500">Status</th>
            <th className="text-left px-4 py-3 font-medium text-gray-500">Message</th>
          </tr>
        </thead>
        <tbody className="divide-y divide-gray-100">
          {logs.map((log) => (
            <tr key={log.id} className="hover:bg-gray-50">
              <td className="px-4 py-3 text-gray-600 whitespace-nowrap">
                {new Date(log.created_at).toLocaleString()}
              </td>
              <td className={`px-4 py-3 font-medium ${statusColors[log.status] || "text-gray-600"}`}>
                {log.status}
              </td>
              <td className="px-4 py-3 text-gray-600 max-w-md truncate">{log.message}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
