import { api } from "@/lib/api";
import { Card, CardDescription, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";

export default async function DashboardPage() {
  let connectionError: string | null = null;
  let jobs: Awaited<ReturnType<typeof api.jobs>> = [];
  let stats: Awaited<ReturnType<typeof api.resumeStats>> = {
    total: 0,
    skills: [],
    average_experience: 0
  };

  try {
    [jobs, stats] = await Promise.all([api.jobs(), api.resumeStats()]);
  } catch (error) {
    connectionError = error instanceof Error ? error.message : "Backend API is unavailable.";
  }

  const pipeline = [
    { stage: "Sourced", count: 186, change: "+24" },
    { stage: "Screen", count: 92, change: "+11" },
    { stage: "Interview", count: 31, change: "+6" },
    { stage: "Offer", count: 8, change: "+2" }
  ];

  return (
    <div className="space-y-5">
      <section className="border border-slate-300 bg-white p-5">
        <div className="flex flex-wrap items-start justify-between gap-4">
          <div>
            <h1 className="text-3xl font-semibold tracking-tight">Recruiting Operations Dashboard</h1>
            <p className="mt-2 max-w-2xl text-sm leading-6 text-slate-600">
              Active requisitions, candidate pipeline health, and screening workflow oversight.
            </p>
          </div>
        </div>
      </section>

      {connectionError && (
        <section className="border border-amber-300 bg-amber-50 p-4 text-sm text-amber-900">
          Backend connection failed: {connectionError}. Check the frontend `NEXT_PUBLIC_API_BASE_URL` value and the backend Railway service logs.
        </section>
      )}

      <div className="grid gap-4 md:grid-cols-4">
        <Metric title="Candidates indexed" value={stats.total.toString()} helper="Resume corpus" />
        <Metric title="Open requisitions" value={jobs.length.toString()} helper="Active templates" />
        <Metric title="Avg. experience" value={`${stats.average_experience} yrs`} helper="Across talent pool" />
        <Metric title="Priority roles" value="7" helper="Hiring focus" />
      </div>

      <div className="grid gap-4 lg:grid-cols-4">
        {pipeline.map((item) => (
          <Card key={item.stage} className="p-0">
            <div className="border-b border-slate-200 bg-slate-50 px-4 py-3 text-xs font-semibold uppercase tracking-wide text-slate-500">
              {item.stage}
            </div>
            <div className="p-4">
              <div className="text-3xl font-semibold">{item.count}</div>
              <div className="mt-1 text-xs font-medium text-emerald-700">{item.change} this week</div>
            </div>
          </Card>
        ))}
      </div>

      <div className="grid gap-4 lg:grid-cols-[1.3fr_0.7fr]">
        <Card>
          <CardTitle>Screening Workflow</CardTitle>
          <div className="mt-5 border border-slate-200 text-sm">
            {["Load JD", "Parse JD", "Generate embeddings", "FAISS retrieval", "Score candidates", "Rank and explain"].map((step, index) => (
              <div key={step} className="grid grid-cols-[52px_1fr_96px] border-b border-slate-200 last:border-b-0">
                <span className="border-r border-slate-200 bg-slate-50 px-4 py-3 text-xs font-semibold text-slate-500">0{index + 1}</span>
                <span className="px-4 py-3 font-medium">{step}</span>
                <span className="border-l border-slate-200 px-4 py-3 text-xs font-semibold uppercase text-emerald-700">Visible</span>
              </div>
            ))}
          </div>
        </Card>
        <Card>
          <CardTitle>Open Requisitions</CardTitle>
          <div className="mt-4 border border-slate-200">
            {jobs.slice(0, 6).map((job) => (
              <div key={job.id} className="border-b border-slate-200 p-3 last:border-b-0">
                <div className="flex items-center justify-between gap-3">
                  <div className="font-semibold">{job.title}</div>
                  <span className="text-xs text-slate-500">{job.id}</span>
                </div>
                <div className="mt-2 flex flex-wrap gap-1.5">
                  {job.required_skills.slice(0, 4).map((skill) => (
                    <Badge key={skill}>{skill}</Badge>
                  ))}
                </div>
              </div>
            ))}
          </div>
        </Card>
      </div>
    </div>
  );
}

function Metric({ title, value, helper }: { title: string; value: string; helper: string }) {
  return (
    <Card className="p-0">
      <div className="border-b border-slate-200 bg-slate-50 px-4 py-3">
        <CardDescription className="font-semibold uppercase tracking-wide">{title}</CardDescription>
      </div>
      <div className="p-4">
        <div className="text-3xl font-semibold tracking-tight">{value}</div>
        <div className="mt-1 text-xs text-slate-500">{helper}</div>
      </div>
    </Card>
  );
}
