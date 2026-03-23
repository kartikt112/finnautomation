"use client";
import { useEffect, useState } from "react";
import Header from "@/components/Header";
import StatsCards from "@/components/StatsCards";
import { getDashboardStats, DashboardStats, getJobs, Job } from "@/lib/api";

export default function DashboardPage() {
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [recentJobs, setRecentJobs] = useState<Job[]>([]);

  useEffect(() => {
    getDashboardStats().then(setStats).catch(console.error);
    getJobs({ limit: 10 }).then(setRecentJobs).catch(console.error);
  }, []);

  return (
    <div>
      <Header title="Dashboard" />
      <div className="p-6 space-y-6">
        <StatsCards stats={stats} />

        <div className="bg-white rounded-lg shadow">
          <div className="px-5 py-4 border-b border-gray-200">
            <h2 className="font-semibold text-gray-900">Recent Jobs</h2>
          </div>
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead className="bg-gray-50">
                <tr>
                  <th className="text-left px-4 py-3 font-medium text-gray-500">Scheduled</th>
                  <th className="text-left px-4 py-3 font-medium text-gray-500">Status</th>
                  <th className="text-left px-4 py-3 font-medium text-gray-500">Retries</th>
                  <th className="text-left px-4 py-3 font-medium text-gray-500">Error</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-100">
                {recentJobs.map((job) => (
                  <tr key={job.id} className="hover:bg-gray-50">
                    <td className="px-4 py-3 whitespace-nowrap">{new Date(job.scheduled_time).toLocaleString()}</td>
                    <td className="px-4 py-3">
                      <span className={`inline-block px-2 py-1 rounded-full text-xs font-medium ${
                        job.status === "success" ? "bg-green-100 text-green-800" :
                        job.status === "failed" ? "bg-red-100 text-red-800" :
                        job.status === "running" ? "bg-blue-100 text-blue-800" :
                        "bg-gray-100 text-gray-800"
                      }`}>
                        {job.status}
                      </span>
                    </td>
                    <td className="px-4 py-3">{job.retry_count}</td>
                    <td className="px-4 py-3 text-red-500 max-w-xs truncate">{job.error_message || "-"}</td>
                  </tr>
                ))}
                {recentJobs.length === 0 && (
                  <tr><td colSpan={4} className="px-4 py-8 text-center text-gray-400">No jobs yet</td></tr>
                )}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  );
}
