export type Job = {
  id: number;
  source: string;
  title: string;
  company: string;
  location: string | null;
  description: string;
  salary_min: number | null;
  salary_max: number | null;
  posted_at: string | null;
  url: string;
  match_score: number | null;
  match_reasoning: string | null;
  hidden: boolean;
  created_at: string;
  application_status: string | null;
};

export type Application = {
  id: number;
  job_id: number;
  status: string;
  applied_at: string | null;
  resume_doc_path: string | null;
  cover_letter_path: string | null;
  last_email_at: string | null;
  notes: string;
  job: Job;
};

const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`${API_URL}/api${path}`, {
    ...init,
    headers: {
      "Content-Type": "application/json",
      ...(init?.headers ?? {})
    },
    cache: "no-store"
  });
  if (!response.ok) {
    throw new Error(await response.text());
  }
  return response.json() as Promise<T>;
}

export function getTopJobs() {
  return request<Job[]>("/jobs/top");
}

export function getJobs() {
  return request<Job[]>("/jobs");
}

export function getApplications() {
  return request<Application[]>("/applications");
}

export function getAnalytics() {
  return request<{
    status_counts: Record<string, number>;
    source_counts: Record<string, number>;
    weekly_velocity: Array<Record<string, unknown>>;
    response_rate: number;
  }>("/analytics");
}

export function createApplication(jobId: number, status = "saved") {
  return request<Application>("/applications", {
    method: "POST",
    body: JSON.stringify({ job_id: jobId, status })
  });
}

export function ingestJobs() {
  return request<{ ingested: number }>("/jobs/ingest", { method: "POST" });
}
