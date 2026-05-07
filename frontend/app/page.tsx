import { Shell } from "@/components/shell";
import { JobCard } from "@/components/job-card";
import { getAnalytics, getTopJobs } from "@/lib/api";

const emptyAnalytics = {
  status_counts: {} as Record<string, number>,
  source_counts: {} as Record<string, number>,
  weekly_velocity: [] as Array<Record<string, unknown>>,
  response_rate: 0
};

export default async function DashboardPage() {
  const [jobs, analytics] = await Promise.all([
    getTopJobs().catch(() => []),
    getAnalytics().catch(() => emptyAnalytics)
  ]);

  return (
    <Shell>
      <div className="mb-6 flex flex-col justify-between gap-3 sm:flex-row sm:items-end">
        <div>
          <p className="text-sm uppercase tracking-wide text-steel">Today</p>
          <h1 className="text-3xl font-semibold">Top matched jobs</h1>
        </div>
        <div className="rounded-md border border-line bg-white px-4 py-3 text-sm">
          Response rate: <span className="font-semibold">{Math.round(analytics.response_rate * 100)}%</span>
        </div>
      </div>

      <section className="mb-6 grid gap-3 sm:grid-cols-3">
        {["saved", "applied", "interview"].map((status) => (
          <div key={status} className="rounded-md border border-line bg-white p-4">
            <p className="text-sm capitalize text-steel">{status}</p>
            <p className="mt-1 text-3xl font-semibold">{analytics.status_counts[status] ?? 0}</p>
          </div>
        ))}
      </section>

      <section className="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
        {jobs.map((job) => (
          <JobCard key={job.id} job={job} />
        ))}
      </section>
    </Shell>
  );
}
