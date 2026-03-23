"use client";
import { useEffect, useState } from "react";
import Link from "next/link";
import Header from "@/components/Header";
import CampaignCard from "@/components/CampaignCard";
import { getCampaigns, Campaign } from "@/lib/api";

export default function CampaignsPage() {
  const [campaigns, setCampaigns] = useState<Campaign[]>([]);
  const [filter, setFilter] = useState<string>("");

  useEffect(() => {
    getCampaigns(filter ? { status: filter } : undefined).then(setCampaigns).catch(console.error);
  }, [filter]);

  return (
    <div>
      <Header title="Campaigns" />
      <div className="p-6 space-y-4">
        <div className="flex items-center justify-between">
          <div className="flex gap-2">
            {["", "active", "paused", "completed"].map((s) => (
              <button
                key={s}
                onClick={() => setFilter(s)}
                className={`px-3 py-1 rounded-full text-sm ${
                  filter === s ? "bg-blue-600 text-white" : "bg-white text-gray-600 border"
                }`}
              >
                {s || "All"}
              </button>
            ))}
          </div>
          <Link
            href="/campaigns/new"
            className="bg-blue-600 text-white px-4 py-2 rounded-lg text-sm font-medium hover:bg-blue-700"
          >
            New Campaign
          </Link>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {campaigns.map((c) => (
            <CampaignCard key={c.id} campaign={c} />
          ))}
        </div>
        {campaigns.length === 0 && (
          <p className="text-center text-gray-400 py-12">No campaigns found</p>
        )}
      </div>
    </div>
  );
}
