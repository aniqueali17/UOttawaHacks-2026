import type { Job } from "../types";

export function JobCard({ job }: { job: Job }) {
  const title = (job as any).title ?? (job as any).job_title;
  const team = (job as any).team;
  const employment = (job as any).employment_type;

    return (
        <div style={{ border: "1px solid #ddd", borderRadius: 12, padding: 14 }}>
            {/* debug (optional) */}
            {/* <pre style={{ fontSize: 12, opacity: 0.7, margin: 0 }}>{JSON.stringify(job, null, 2)}</pre> */}

            <div style={{ fontWeight: 700 }}>{title ?? "Untitled role"}</div>

            <div style={{ opacity: 0.8, marginTop: 6 }}>
                {(job as any).location ?? (job as any).job_location ?? "Unknown location"} •{" "}
                {(job as any).posting_date ?? (job as any).posted_date ?? "Unknown date"}
            </div>


            {(team || employment) && (
            <div style={{ opacity: 0.8, marginTop: 6 }}>
                {team ?? "—"} {team && employment ? "•" : ""} {employment ?? "—"}
            </div>
            )}

            {job.apply_url && (
            <a
                href={job.apply_url}
                target="_blank"
                rel="noreferrer"
                style={{ display: "inline-block", marginTop: 10 }}
            >
                Apply →
            </a>
            )}
        </div>
    );
}