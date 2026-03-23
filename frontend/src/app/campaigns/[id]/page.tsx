"use client";
import { useEffect, useState } from "react";
import { useParams } from "next/navigation";
import Header from "@/components/Header";
import { getCampaign, pauseCampaign, resumeCampaign, triggerJob, CampaignDetail } from "@/lib/api";

const statusColors: Record<string, string> = {
  pending: "bg-gray-100 text-gray-800",
  queued: "bg-indigo-100 text-indigo-800",
  running: "bg-blue-100 text-blue-800",
  success: "bg-green-100 text-green-800",
  failed: "bg-red-100 text-red-800",
  retrying: "bg-yellow-100 text-yellow-800",
};

export default function CampaignDetailPage() {
  const { id } = useParams<{ id: string }>();
  const [campaign, setCampaign] = useState<CampaignDetail | null>(null);
  const [loading, setLoading] = useState(true);

  function load() {
    getCampaign(id).then(setCampaign).catch(console.error).finally(() => setLoading(false));
  }

  useEffect(() => { load(); }, [id]);

  async function handlePause() {
    await pauseCampaign(id);
    load();
  }

  async function handleResume() {
    await resumeCampaign(id);
    load();
  }

  async function handleTrigger() {
    await triggerJob(id);
    setTimeout(load, 1000);
  }

  if (loading) return <div className="p-6">Loading...</div>;
  if (!campaign) return <div className="p-6">Campaign not found</div>;

  const progress = campaign.total_jobs > 0
    ? Math.round((campaign.successful_jobs / campaign.total_jobs) * 100)
    : 0;

  return (
    <div>
      <Header title={campaign.name} />
      <div className="p-6 space-y-6">
        {/* Info Cards */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <div className="bg-white rounded-lg shadow p-4">
            <p className="text-sm text-gray-500">Status</p>
            <p className={`text-lg font-bold capitalize ${
              campaign.status === "active" ? "text-green-600" :
              campaign.status === "paused" ? "text-yellow-600" : "text-gray-600"
            }`}>{campaign.status}</p>
          </div>
          <div className="bg-white rounded-lg shadow p-4">
            <p className="text-sm text-gray-500">Total Jobs</p>
            <p className="text-lg font-bold">{campaign.total_jobs}</p>
          </div>
          <div className="bg-white rounded-lg shadow p-4">
            <p className="text-sm text-gray-500">Successful</p>
            <p className="text-lg font-bold text-green-600">{campaign.successful_jobs}</p>
          </div>
          <div className="bg-white rounded-lg shadow p-4">
            <p className="text-sm text-gray-500">Failed</p>
            <p className="text-lg font-bold text-red-600">{campaign.failed_jobs}</p>
          </div>
        </div>

        {/* Actions */}
        <div className="flex gap-3">
          {campaign.status === "active" && (
            <button onClick={handlePause} className="bg-yellow-500 text-white px-4 py-2 rounded-lg text-sm hover:bg-yellow-600">
              Pause Campaign
            </button>
          )}
          {campaign.status === "paused" && (
            <button onClick={handleResume} className="bg-green-500 text-white px-4 py-2 rounded-lg text-sm hover:bg-green-600">
              Resume Campaign
            </button>
          )}
          <button onClick={handleTrigger} className="bg-blue-600 text-white px-4 py-2 rounded-lg text-sm hover:bg-blue-700">
            Trigger Job Now
          </button>
          <button onClick={load} className="bg-gray-200 text-gray-700 px-4 py-2 rounded-lg text-sm hover:bg-gray-300">
            Refresh
          </button>
        </div>

        {/* Details */}
        <div className="bg-white rounded-lg shadow p-5">
          <h3 className="font-semibold mb-3">Campaign Details</h3>
          <div className="grid grid-cols-2 gap-4 text-sm">
            <div><span className="text-gray-500">Client:</span> {campaign.client.name}</div>
            <div><span className="text-gray-500">Target URL:</span> <a href={campaign.target_url} className="text-blue-600 hover:underline" target="_blank">{campaign.target_url}</a></div>
            <div><span className="text-gray-500">Start Date:</span> {campaign.start_date}</div>
            <div><span className="text-gray-500">End Date:</span> {campaign.end_date}</div>
            <div><span className="text-gray-500">Duration:</span> {campaign.duration_days} days</div>
            <div><span className="text-gray-500">Success Rate:</span> {progress}%</div>
          </div>
        </div>

        {/* Jobs Table */}
        <div className="bg-white rounded-lg shadow">
          <div className="px-5 py-4 border-b border-gray-200">
            <h2 className="font-semibold">Jobs ({campaign.jobs.length})</h2>
          </div>
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead className="bg-gray-50">
                <tr>
                  <th className="text-left px-4 py-3 font-medium text-gray-500">Scheduled</th>
                  <th className="text-left px-4 py-3 font-medium text-gray-500">Status</th>
                  <th className="text-left px-4 py-3 font-medium text-gray-500">Started</th>
                  <th className="text-left px-4 py-3 font-medium text-gray-500">Completed</th>
                  <th className="text-left px-4 py-3 font-medium text-gray-500">Retries</th>
                  <th className="text-left px-4 py-3 font-medium text-gray-500">Error</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-100">
                {campaign.jobs.map((job) => (
                  <tr key={job.id} className="hover:bg-gray-50">
                    <td className="px-4 py-3 whitespace-nowrap">{new Date(job.scheduled_time).toLocaleString()}</td>
                    <td className="px-4 py-3">
                      <span className={`inline-block px-2 py-1 rounded-full text-xs font-medium ${statusColors[job.status] || ""}`}>
                        {job.status}
                      </span>
                    </td>
                    <td className="px-4 py-3 whitespace-nowrap">{job.started_at ? new Date(job.started_at).toLocaleString() : "-"}</td>
                    <td className="px-4 py-3 whitespace-nowrap">{job.completed_at ? new Date(job.completed_at).toLocaleString() : "-"}</td>
                    <td className="px-4 py-3">{job.retry_count}</td>
                    <td className="px-4 py-3 text-red-500 max-w-xs truncate">{job.error_message || "-"}</td>
                  </tr>
                ))}
                {campaign.jobs.length === 0 && (
                  <tr><td colSpan={6} className="px-4 py-8 text-center text-gray-400">No jobs generated yet</td></tr>
                )}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  );
}
