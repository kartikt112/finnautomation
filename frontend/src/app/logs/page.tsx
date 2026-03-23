"use client";
import { useEffect, useState } from "react";
import Header from "@/components/Header";
import LogTable from "@/components/LogTable";
import { getLogs, LogEntry } from "@/lib/api";

export default function LogsPage() {
  const [logs, setLogs] = useState<LogEntry[]>([]);
  const [limit, setLimit] = useState(50);

  useEffect(() => {
    getLogs({ limit }).then(setLogs).catch(console.error);
  }, [limit]);

  return (
    <div>
      <Header title="Execution Logs" />
      <div className="p-6">
        <div className="bg-white rounded-lg shadow">
          <div className="px-5 py-4 border-b border-gray-200 flex items-center justify-between">
            <h2 className="font-semibold text-gray-900">Logs ({logs.length})</h2>
            <div className="flex gap-2">
              <button
                onClick={() => getLogs({ limit }).then(setLogs)}
                className="text-sm text-blue-600 hover:text-blue-800"
              >
                Refresh
              </button>
              <select
                value={limit}
                onChange={(e) => setLimit(Number(e.target.value))}
                className="border border-gray-300 rounded px-2 py-1 text-sm"
              >
                <option value={25}>25</option>
                <option value={50}>50</option>
                <option value={100}>100</option>
                <option value={200}>200</option>
              </select>
            </div>
          </div>
          <LogTable logs={logs} />
        </div>
      </div>
    </div>
  );
}
