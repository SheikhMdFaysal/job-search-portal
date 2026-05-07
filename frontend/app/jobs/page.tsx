import { JobCard } from "@/components/job-card";
import { Shell } from "@/components/shell";
import { getJobs } from "@/lib/api";

export default async function JobsPage() {
  const jobs = await getJobs().catch(() => []);
  return (
    <Shell>
      <div className="mb-6">
        <p className="text-sm uppercase tracking-wide text-steel">Feed</p>
        <h1 className="text-3xl font-semibold">All jobs</h1>
      </div>
      <section className="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
        {jobs.map((job) => (
          <JobCard key={job.id} job={job} />
        ))}
      </section>
    </Shell>
  );
}
