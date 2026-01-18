const API_BASE = "/api";

export async function extractJobs(url: string) {
  const res = await fetch(`${API_BASE}/extract`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ url }),
  });

  const text = await res.text();
  
  if (!res.ok) throw new Error(text);

  const json = JSON.parse(text);
  return json.jobs ?? [];
}