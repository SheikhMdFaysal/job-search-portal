import Link from "next/link";
import { BriefcaseBusiness, Inbox, LineChart, Settings } from "lucide-react";

const nav = [
  { href: "/", label: "Dashboard", icon: LineChart },
  { href: "/jobs", label: "Jobs", icon: BriefcaseBusiness },
  { href: "/applications", label: "Applications", icon: Inbox },
  { href: "/onboarding", label: "Profile", icon: Settings }
];

export function Shell({ children }: { children: React.ReactNode }) {
  return (
    <main className="min-h-screen">
      <aside className="fixed inset-y-0 left-0 hidden w-64 border-r border-line bg-white/70 px-4 py-6 lg:block">
        <div className="mb-8 px-2">
          <p className="text-sm uppercase tracking-wide text-steel">Personal portal</p>
          <h1 className="text-2xl font-semibold">Job Search</h1>
        </div>
        <nav className="space-y-1">
          {nav.map((item) => (
            <Link
              key={item.href}
              href={item.href}
              className="flex items-center gap-3 rounded-md px-3 py-2 text-sm font-medium hover:bg-paper"
            >
              <item.icon className="h-4 w-4" />
              {item.label}
            </Link>
          ))}
        </nav>
      </aside>
      <section className="lg:pl-64">
        <div className="mx-auto max-w-7xl px-4 py-6 sm:px-6 lg:px-8">{children}</div>
      </section>
    </main>
  );
}
