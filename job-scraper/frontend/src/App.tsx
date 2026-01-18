import { useState } from "react";
import { extractJobs } from "./api";
import type { Job } from "./types";
import { JobCard } from "./components/JobCard";

export default function App() {
  const [url, setUrl] = useState("");
  const [jobs, setJobs] = useState<Job[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string>("");

  //phase 2 UI state
  const [search, setSearch] = useState("");
  const [loc, setLoc] = useState("");

  const DEMO_URLS = [
    "https://boards.greenhouse.io/airbnb",
    "https://boards.greenhouse.io/databricks",
    "https://jobs.lever.co/notion",
  ];

  // In App.tsx - around line 25

async function onFetch() {
  setError("");
  setLoading(true);
  try {
    const jobs = await extractJobs(url);
    setJobs(jobs);

    // setSearch("");  // ⚠️ Remove this line
    // setLoc("");     // ⚠️ Remove this line
  } catch (e: any) {
    setError(e?.message ?? "Something went wrong");
  } finally {
    setLoading(false);
  }
}
  const getLocation = (j: any) =>
  j.location ?? j.job_location ?? j.locations ?? j.city ?? j.region ?? "";

  const locations = Array.from(
    new Set(jobs.map((j) => getLocation(j as any)).filter(Boolean))
  ).sort();

  const filtered = jobs.filter((j) => {
    const title = String((j as any).title ?? (j as any).job_title ?? "").toLowerCase();
    const company = String((j as any).company ?? "").toLowerCase();
    return `${title} ${company}`.includes(search.toLowerCase());
  });

const filteredByLoc = filtered.filter((j) => !loc || getLocation(j as any) === loc);

  const sorted = [...filteredByLoc].sort((a, b) => {
    const da = String((a as any).posting_date ?? (a as any).posted_date ?? "");
    const db = String((b as any).posting_date ?? (b as any).posted_date ?? "");
    return db.localeCompare(da); // newest first for ISO strings
  });

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

      {/* Phase 2 controls */}
      <div style={{ display: "flex", gap: 10, marginTop: 12 }}>
        <input
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          placeholder="Search title/company..."
          style={{ flex: 1, padding: 12, borderRadius: 10, border: "1px solid #ccc" }}
        />

        <select
          value={loc}
          onChange={(e) => setLoc(e.target.value)}
          style={{ width: 240, padding: 12, borderRadius: 10, border: "1px solid #ccc" }}
        >
          <option value="">All locations</option>
          {locations.map((l) => (
            <option key={l} value={l}>
              {l}
            </option>
          ))}
        </select>
      </div>

      {error && <div style={{ marginTop: 12, color: "crimson" }}>{error}</div>}
        
      <div style={{ marginTop: 10, opacity: 0.7, fontSize: 14 }}>
        Fetched: {jobs.length} | Showing: {sorted.length}
      </div>
      <div style={{ display: "grid", gridTemplateColumns: "1fr", gap: 12, marginTop: 18 }}>
        {sorted.map((j, i) => (
          <JobCard key={(j as any).apply_url ?? `${(j as any).title}-${i}`} job={j} />
        ))}
      </div>
    </div>
  );
}

// helpers(unused for now)
function copyJSON(jobs: any) {
  navigator.clipboard.writeText(JSON.stringify({ jobs }, null, 2));
}
