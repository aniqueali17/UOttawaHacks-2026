import type { Job } from "./types";

const API_BASE = import.meta.env.VITE_API_BASE ?? "http://localhost:8000";

const MOCK_JOBS: Job[] = [
  { title: "Software Developer Intern", location: "Ottawa, ON", posted_date: "2026-01-10", apply_url: "https://example.com/apply" },
  { title: "Frontend Engineer", location: "Remote (Canada)", posted_date: "2026-01-05", apply_url: "https://example.com/apply2" },
];

export async function extractJobs(url: string): Promise<Job[]> {
  try {
    const res = await fetch(`${API_BASE}/api/extract`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ url }),
    });
    if (!res.ok) throw new Error(await res.text());
    const data = await res.json();
    return data.jobs ?? [];
  } catch {
    // fallback while backend isn't ready
    await new Promise((r) => setTimeout(r, 600));
    return MOCK_JOBS;
  }
}
