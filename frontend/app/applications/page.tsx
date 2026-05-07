import { Shell } from "@/components/shell";
import { getApplications } from "@/lib/api";

const statuses = ["saved", "applied", "interview", "offer", "rejected", "ghosted"];

export default async function ApplicationsPage() {
  const applications = await getApplications().catch(() => []);
  return (
    <Shell>
      <div className="mb-6">
        <p className="text-sm uppercase tracking-wide text-steel">Pipeline</p>
        <h1 className="text-3xl font-semibold">Applications</h1>
      </div>
      <div className="grid gap-4 xl:grid-cols-3">
        {statuses.map((status) => (
          <section key={status} className="min-h-64 rounded-md border border-line bg-white p-4">
            <h2 className="mb-3 text-sm font-semibold uppercase tracking-wide text-steel">{status}</h2>
            <div className="space-y-3">
              {applications
                .filter((application) => application.status === status)
                .map((application) => (
                  <article key={application.id} className="rounded-md border border-line bg-paper p-3">
                    <p className="text-sm text-steel">{application.job.company}</p>
                    <h3 className="font-semibold">{application.job.title}</h3>
                    <p className="mt-2 text-xs text-steel">{application.job.source}</p>
                  </article>
                ))}
            </div>
          </section>
        ))}
      </div>
    </Shell>
  );
}
