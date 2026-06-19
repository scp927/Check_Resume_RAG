import type { ATSRunResponse, JDResumeCheckResponse, Job, LangGraphSearchResponse, ParsedJD, Resume, SearchResult } from "@/types/ats";

const DEFAULT_API_BASE =
  process.env.NODE_ENV === "production"
    ? "https://checkresumerag-production.up.railway.app/api"
    : "http://localhost:8000/api";

export const API_BASE = (process.env.NEXT_PUBLIC_API_BASE_URL ?? DEFAULT_API_BASE).replace(/\/$/, "");

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`${API_BASE}${path}`, {
    ...init,
    headers: {
      "Content-Type": "application/json",
      ...(init?.headers ?? {})
    },
    cache: "no-store"
  });
  if (!response.ok) {
    throw new Error(`API request failed: ${response.status} ${response.statusText}`);
  }
  return response.json() as Promise<T>;
}

export const api = {
  resumes: () => request<Resume[]>("/resumes?limit=1000"),
  resumeStats: () => request<{ total: number; skills: string[]; average_experience: number }>("/resumes/stats"),
  jobs: () => request<Job[]>("/jobs"),
  parseJob: (description: string, required_skills: string[] = []) =>
    request<ParsedJD>("/jobs/parse", {
      method: "POST",
      body: JSON.stringify({ description, required_skills })
    }),
  search: (query: string, top_k = 10) =>
    request<SearchResult[]>("/search", {
      method: "POST",
      body: JSON.stringify({ query, top_k })
    }),
  langGraphSearch: (payload: { query: string; job_description?: string; top_k?: number; max_iterations?: number; validation_threshold?: number }) =>
    request<LangGraphSearchResponse>("/search/langgraph", {
      method: "POST",
      body: JSON.stringify(payload)
    }),
  runAts: (payload: { job_id?: string; job_description?: string; resume_ids?: string[]; top_k?: number }) =>
    request<ATSRunResponse>("/ats/run", {
      method: "POST",
      body: JSON.stringify(payload)
    }),
  checkJDResume: (payload: { job_description: string; resume_text: string; resume_name?: string; resume_skills?: string[]; experience?: number }) =>
    request<JDResumeCheckResponse>("/ats/check", {
      method: "POST",
      body: JSON.stringify(payload)
    })
};
