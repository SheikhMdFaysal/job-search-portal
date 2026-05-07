import { ExternalLink, MapPin, Sparkles } from "lucide-react";
import type { Job } from "@/lib/api";

export function JobCard({ job }: { job: Job }) {
  return (
    <article className="rounded-md border border-line bg-white p-4 shadow-soft">
      <div className="flex items-start justify-between gap-4">
        <div>
          <p className="text-sm text-steel">{job.company}</p>
          <h2 className="mt-1 text-lg font-semibold leading-snug">{job.title}</h2>
        </div>
        <div className="flex h-12 w-12 shrink-0 items-center justify-center rounded-md bg-mint/30 font-semibold">
          {job.match_score ?? "--"}
        </div>
      </div>
      <div className="mt-3 flex flex-wrap items-center gap-3 text-sm text-steel">
        <span className="inline-flex items-center gap-1">
          <MapPin className="h-4 w-4" />
          {job.location ?? "Location not listed"}
        </span>
        <span className="inline-flex items-center gap-1">
          <Sparkles className="h-4 w-4" />
          {job.source}
        </span>
      </div>
      <p className="mt-3 line-clamp-3 text-sm leading-6 text-ink/75">{job.match_reasoning}</p>
      <div className="mt-4 flex items-center justify-between">
        <span className="rounded-md bg-paper px-2 py-1 text-xs font-medium">{job.application_status ?? "new"}</span>
        <a href={job.url} target="_blank" className="inline-flex items-center gap-1 text-sm font-medium">
          Apply <ExternalLink className="h-4 w-4" />
        </a>
      </div>
    </article>
  );
}
