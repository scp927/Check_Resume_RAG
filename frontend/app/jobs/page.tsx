"use client";

import { useEffect, useState } from "react";

import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardDescription, CardTitle } from "@/components/ui/card";
import { api } from "@/lib/api";
import type { Job } from "@/types/ats";

export default function JobsPage() {
  const [jobs, setJobs] = useState<Job[]>([]);
  const [selectedJob, setSelectedJob] = useState<Job | null>(null);

  useEffect(() => {
    api.jobs().then(setJobs);
  }, []);

  return (
    <div className="space-y-6">
      <section>
        <h1 className="text-3xl font-bold">Job Descriptions</h1>
        <p className="mt-2 text-slate-600">Detailed global requisitions with responsibilities, requirements, and first-90-day expectations.</p>
      </section>
      <div className="grid gap-4 lg:grid-cols-2">
        {jobs.map((job, index) => {
          const jobWithPoster = { ...job, poster: job.poster ?? DEFAULT_POSTERS[index % DEFAULT_POSTERS.length] };
          return (
          <Card key={job.id} className="cursor-pointer transition hover:border-blue-300 hover:bg-blue-50/20" onClick={() => setSelectedJob(jobWithPoster)}>
            <div className="flex items-start justify-between gap-4">
              <div>
                <CardTitle>{job.title}</CardTitle>
                <CardDescription className="mt-1">{job.id}</CardDescription>
              </div>
              <Badge>{job.required_skills.length} required</Badge>
            </div>
            {jobWithPoster.poster && (
              <JobPosterBlock job={jobWithPoster} />
            )}
            <p className="mt-4 line-clamp-6 whitespace-pre-line text-sm leading-6 text-slate-600">{job.description}</p>
            <div className="mt-4 flex flex-wrap gap-1">
              {job.required_skills.map((skill) => (
                <Badge key={skill}>{skill}</Badge>
              ))}
            </div>
          </Card>
        );})}
      </div>
      {selectedJob && (
        <div className="fixed inset-0 z-50 bg-slate-950/40 p-4" role="dialog" aria-modal="true" onClick={() => setSelectedJob(null)}>
          <div className="mx-auto max-h-[90vh] max-w-4xl overflow-y-auto border border-slate-300 bg-white p-6 shadow-xl" onClick={(event) => event.stopPropagation()}>
            {selectedJob.poster && <JobPosterBlock job={selectedJob} prominent />}
            <div className="flex items-start justify-between gap-4 border-b border-slate-200 pb-4">
              <div>
                <h2 className="text-2xl font-semibold tracking-tight">{selectedJob.title}</h2>
                <div className="mt-2 text-sm text-slate-500">{selectedJob.id}</div>
              </div>
              <Button className="border-slate-300 bg-white text-slate-700 hover:border-slate-400 hover:bg-slate-50" onClick={() => setSelectedJob(null)}>Close</Button>
            </div>
            <div className="mt-6 whitespace-pre-line text-sm leading-7 text-slate-700">{selectedJob.description}</div>
            <div className="mt-6 flex flex-wrap gap-1.5">
              {selectedJob.required_skills.map((skill) => <Badge key={skill}>{skill}</Badge>)}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

const DEFAULT_POSTERS: NonNullable<Job["poster"]>[] = [
  {
    name: "Krutika Jhaveri",
    degree: "3rd",
    headline: "HR Technology & Talent Acquisition Consultant | Startup & Staffing",
    subheadline: "Recruitment Specialist | Diversity, Equity & Inclusion Advocate | Ex-Leadership Recruiter at AWS | MBA in IT | Freelance Interview Coach",
    label: "Job poster"
  },
  {
    name: "Maya Chen",
    degree: "2nd",
    headline: "Technical Recruiting Lead | AI Startups | Global Engineering Hiring",
    subheadline: "Former SaaS Talent Partner | Engineering Leadership Search | DEI Hiring Programs | Interview Coach",
    label: "Job poster"
  },
  {
    name: "Arjun Mehta",
    degree: "3rd",
    headline: "Startup Talent Partner | Product Engineering & Infrastructure Recruiting",
    subheadline: "Ex-Cloud Platform Recruiter | MBA | Remote Team Hiring | Compensation Advisory",
    label: "Job poster"
  }
];

function JobPosterBlock({ job, prominent = false }: { job: Job; prominent?: boolean }) {
  if (!job.poster) return null;
  const initials = job.poster.name.split(" ").map((part) => part[0]).join("").slice(0, 2);

  return (
    <div className={prominent ? "mb-5 border-b border-slate-200 pb-5" : "mt-4 border-y border-slate-200 py-4"}>
      <div className="text-sm font-semibold text-slate-950">Meet the hiring team</div>
      <div className="mt-3 flex items-center justify-between gap-4">
        <div className="flex min-w-0 items-start gap-3">
          <div className="relative flex h-14 w-14 shrink-0 items-center justify-center overflow-hidden rounded-full border border-blue-100 bg-gradient-to-br from-blue-100 via-white to-indigo-100 text-base font-semibold text-blue-700 shadow-sm">
            <span>{initials}</span>
            <span className="absolute bottom-0 right-0 h-4 w-4 rounded-full border-2 border-white bg-emerald-500" />
          </div>
          <div className="min-w-0">
            <div className="font-semibold text-slate-950">
              {job.poster.name} <span className="font-normal text-slate-500">· {job.poster.degree}</span>
            </div>
            <div className="mt-1 text-xs leading-5 text-slate-700">{job.poster.headline}</div>
            <div className="text-xs leading-5 text-slate-600">{job.poster.subheadline}</div>
            <div className="mt-1 text-xs text-slate-500">{job.poster.label}</div>
          </div>
        </div>
        <button className="shrink-0 border border-slate-300 bg-white px-4 py-2 text-sm font-semibold text-slate-700 transition hover:border-blue-300 hover:text-blue-700">
          Message
        </button>
      </div>
    </div>
  );
}
