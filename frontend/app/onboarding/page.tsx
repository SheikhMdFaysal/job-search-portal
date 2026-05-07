import { Shell } from "@/components/shell";
import { ResumeUpload } from "@/components/resume-upload";

export default function OnboardingPage() {
  return (
    <Shell>
      <div className="max-w-3xl">
        <p className="text-sm uppercase tracking-wide text-steel">Profile</p>
        <h1 className="mb-4 text-3xl font-semibold">Onboarding</h1>
        <form className="space-y-4 rounded-md border border-line bg-white p-5">
          <ResumeUpload />
          <label className="block">
            <span className="text-sm font-medium">Target roles</span>
            <input className="mt-1 w-full rounded-md border border-line px-3 py-2" defaultValue="data analyst, business analyst, financial analyst" />
          </label>
          <label className="block">
            <span className="text-sm font-medium">Locations</span>
            <input className="mt-1 w-full rounded-md border border-line px-3 py-2" defaultValue="Jersey City NJ, New York NY, Remote US" />
          </label>
          <label className="block">
            <span className="text-sm font-medium">Master resume JSON</span>
            <textarea className="mt-1 h-72 w-full rounded-md border border-line px-3 py-2 font-mono text-sm" defaultValue={'{\n  "name": "Sheikh Md Faysal",\n  "skills": ["SQL", "Python", "Excel", "Power BI", "Tableau"]\n}'} />
          </label>
          <button className="rounded-md bg-ink px-4 py-2 text-sm font-semibold text-white" type="button">
            Save profile
          </button>
        </form>
      </div>
    </Shell>
  );
}
