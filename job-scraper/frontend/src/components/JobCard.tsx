import type { Job } from "../types";

export function JobCard({ job }: { job: Job }) {
  return (
    <div style={{ border: "1px solid #ddd", borderRadius: 12, padding: 14 }}>
      <div style={{ fontWeight: 700 }}>{job.title ?? "Untitled role"}</div>
      <div style={{ opacity: 0.8, marginTop: 6 }}>
        {job.location ?? "Unknown location"} • {job.posted_date ?? "Unknown date"}
      </div>
      <div style={{ opacity: 0.8, marginTop: 6 }}>
        {job.team ?? "Unknown team"} • {job.employment_type ?? "Unknown type"}
      </div>

      {job.apply_url && (
        <a href={job.apply_url} target="_blank" rel="noreferrer" style={{ display: "inline-block", marginTop: 10 }}>
          Apply →
        </a>
      )}
    </div>
  );
}
