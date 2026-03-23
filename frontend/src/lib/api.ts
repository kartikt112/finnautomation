const BASE_URL = "/api";

async function request<T>(path: string, options?: RequestInit): Promise<T> {
  const res = await fetch(`${BASE_URL}${path}`, {
    headers: { "Content-Type": "application/json", ...options?.headers },
    ...options,
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(err.detail || "Request failed");
  }
  return res.json();
}

// --- Clients ---
export interface Client {
  id: string;
  name: string;
  multilogin_profile_group: string | null;
  created_at: string;
}

export const getClients = () => request<Client[]>("/clients");
export const createClient = (data: { name: string; multilogin_profile_group?: string }) =>
  request<Client>("/clients", { method: "POST", body: JSON.stringify(data) });
export const deleteClient = (id: string) =>
  request(`/clients/${id}`, { method: "DELETE" });

// --- Campaigns ---
export interface Campaign {
  id: string;
  client_id: string;
  name: string;
  target_url: string;
  excel_file_path: string | null;
  duration_days: number;
  start_date: string;
  end_date: string;
  status: "active" | "paused" | "completed";
  created_at: string;
}

export interface CampaignDetail extends Campaign {
  client: Client;
  jobs: Job[];
  total_jobs: number;
  successful_jobs: number;
  failed_jobs: number;
}

export const getCampaigns = (params?: { status?: string; client_id?: string }) => {
  const query = new URLSearchParams();
  if (params?.status) query.set("status", params.status);
  if (params?.client_id) query.set("client_id", params.client_id);
  const qs = query.toString();
  return request<Campaign[]>(`/campaigns${qs ? `?${qs}` : ""}`);
};

export const getCampaign = (id: string) => request<CampaignDetail>(`/campaigns/${id}`);
export const pauseCampaign = (id: string) => request(`/campaigns/${id}/pause`, { method: "POST" });
export const resumeCampaign = (id: string) => request(`/campaigns/${id}/resume`, { method: "POST" });

export const uploadCampaign = async (formData: FormData) => {
  const res = await fetch(`${BASE_URL}/upload`, { method: "POST", body: formData });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(err.detail || "Upload failed");
  }
  return res.json() as Promise<Campaign>;
};

// --- Jobs ---
export interface Job {
  id: string;
  campaign_id: string;
  scheduled_time: string;
  started_at: string | null;
  completed_at: string | null;
  status: "pending" | "queued" | "running" | "success" | "failed" | "retrying";
  retry_count: number;
  entry_data: Record<string, string> | null;
  error_message: string | null;
  created_at: string;
}

export const getJobs = (params?: { campaign_id?: string; status?: string; limit?: number }) => {
  const query = new URLSearchParams();
  if (params?.campaign_id) query.set("campaign_id", params.campaign_id);
  if (params?.status) query.set("status", params.status);
  if (params?.limit) query.set("limit", String(params.limit));
  const qs = query.toString();
  return request<Job[]>(`/jobs${qs ? `?${qs}` : ""}`);
};

export const triggerJob = (campaign_id: string) =>
  request(`/trigger`, { method: "POST", body: JSON.stringify({ campaign_id }) });

// --- Logs ---
export interface LogEntry {
  id: string;
  job_id: string;
  status: string;
  message: string | null;
  error_trace: string | null;
  created_at: string;
}

export const getLogs = (params?: { job_id?: string; limit?: number }) => {
  const query = new URLSearchParams();
  if (params?.job_id) query.set("job_id", params.job_id);
  if (params?.limit) query.set("limit", String(params.limit));
  const qs = query.toString();
  return request<LogEntry[]>(`/logs${qs ? `?${qs}` : ""}`);
};

// --- Dashboard ---
export interface DashboardStats {
  total_clients: number;
  active_campaigns: number;
  todays_jobs: number;
  success_rate: number;
  total_jobs_today: number;
  successful_today: number;
  failed_today: number;
}

export const getDashboardStats = () => request<DashboardStats>("/dashboard/stats");
