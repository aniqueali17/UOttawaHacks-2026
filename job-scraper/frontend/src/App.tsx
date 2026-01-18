import { useState } from "react";
import { extractJobs } from "./api";
import type { Job } from "./types";
import { JobCard } from "./components/JobCard";

export default function App() {
  const [url, setUrl] = useState("");
  const [jobs, setJobs] = useState<Job[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string>("");
  const DEMO_URLS = [
  "https://company.com/careers",
  "https://boards.greenhouse.io/company",
  "https://jobs.lever.co/company",];

  async function onFetch() {
    setError("");
    setLoading(true);
    try {
      const data = await extractJobs(url);
      setJobs(data);
    } catch (e: any) {
      setError(e?.message ?? "Something went wrong");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div style={{ maxWidth: 900, margin: "40px auto", padding: 16, fontFamily: "system-ui" }}>
      <h1 style={{ marginBottom: 6 }}>Job Scraper MVP</h1>
      <p style={{ opacity: 0.8, marginTop: 0 }}>
        Paste a careers URL → get latest job listings.
      </p>

      <div style={{ display: "flex", gap: 10, marginTop: 14 }}>
        <input
          value={url}
          onChange={(e) => setUrl(e.target.value)}
          placeholder="https://company.com/careers"
          style={{ flex: 1, padding: 12, borderRadius: 10, border: "1px solid #ccc" }}
        />
        <button
          onClick={onFetch}
          disabled={loading || !url}
          style={{ padding: "12px 16px", borderRadius: 10, border: "1px solid #ccc", cursor: "pointer" }}
        >
          {loading ? "Fetching..." : "Fetch Jobs"}
        </button>
      </div>

      {error && <div style={{ marginTop: 12, color: "crimson" }}>{error}</div>}

      <div style={{ display: "grid", gridTemplateColumns: "1fr", gap: 12, marginTop: 18 }}>
        {jobs.map((j, i) => (
          <JobCard key={j.apply_url ?? `${j.title}-${i}`} job={j} />
        ))}
      </div>
    </div>
  );
}
//helpers
function copyJSON(jobs: any) {
  navigator.clipboard.writeText(JSON.stringify({ jobs }, null, 2));
}

function exportCSV(jobs: any[]) {
  const headers = ["title","location","posted_date","apply_url","team","employment_type"];
  const rows = jobs.map(j => headers.map(h => JSON.stringify(j?.[h] ?? "")).join(","));
  const csv = [headers.join(","), ...rows].join("\n");

  const blob = new Blob([csv], { type: "text/csv;charset=utf-8;" });
  const link = document.createElement("a");
  link.href = URL.createObjectURL(blob);
  link.download = "jobs.csv";
  link.click();
  URL.revokeObjectURL(link.href);
}
