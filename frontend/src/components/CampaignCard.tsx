"use client";
import Link from "next/link";
import { Campaign } from "@/lib/api";

const statusColors = {
  active: "bg-green-100 text-green-800",
  paused: "bg-yellow-100 text-yellow-800",
  completed: "bg-gray-100 text-gray-800",
};

export default function CampaignCard({ campaign }: { campaign: Campaign }) {
  const start = new Date(campaign.start_date);
  const end = new Date(campaign.end_date);
  const now = new Date();
  const totalDays = (end.getTime() - start.getTime()) / (1000 * 60 * 60 * 24);
  const elapsed = Math.max(0, (now.getTime() - start.getTime()) / (1000 * 60 * 60 * 24));
  const progress = Math.min(100, (elapsed / totalDays) * 100);

  return (
    <Link href={`/campaigns/${campaign.id}`} className="block">
      <div className="bg-white rounded-lg shadow p-5 hover:shadow-md transition-shadow">
        <div className="flex items-center justify-between mb-3">
          <h3 className="font-semibold text-gray-900">{campaign.name}</h3>
          <span className={`text-xs px-2 py-1 rounded-full font-medium ${statusColors[campaign.status]}`}>
            {campaign.status}
          </span>
        </div>
        <p className="text-sm text-gray-500 mb-3 truncate">{campaign.target_url}</p>
        <div className="w-full bg-gray-200 rounded-full h-2 mb-2">
          <div
            className="bg-blue-500 h-2 rounded-full transition-all"
            style={{ width: `${progress}%` }}
          />
        </div>
        <div className="flex justify-between text-xs text-gray-400">
          <span>{campaign.start_date}</span>
          <span>{campaign.end_date}</span>
        </div>
      </div>
    </Link>
  );
}
