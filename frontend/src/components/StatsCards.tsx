"use client";
import { DashboardStats } from "@/lib/api";

export default function StatsCards({ stats }: { stats: DashboardStats | null }) {
  const cards = [
    { label: "Total Clients", value: stats?.total_clients ?? "-", color: "bg-blue-500" },
    { label: "Active Campaigns", value: stats?.active_campaigns ?? "-", color: "bg-green-500" },
    { label: "Today's Jobs", value: stats?.todays_jobs ?? "-", color: "bg-purple-500" },
    { label: "Success Rate", value: stats ? `${stats.success_rate}%` : "-", color: "bg-amber-500" },
  ];

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
      {cards.map((card) => (
        <div key={card.label} className="bg-white rounded-lg shadow p-5">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-500">{card.label}</p>
              <p className="text-2xl font-bold mt-1">{card.value}</p>
            </div>
            <div className={`w-10 h-10 rounded-full ${card.color} opacity-20`} />
          </div>
        </div>
      ))}
    </div>
  );
}
