"use client";

import { useEffect, useState } from "react";
import type { ReactNode } from "react";

import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardDescription, CardTitle } from "@/components/ui/card";
import { api } from "@/lib/api";
import { getResumeSections } from "@/lib/resume-utils";
import type { Resume } from "@/types/ats";

export default function ResumesPage() {
  const [resumes, setResumes] = useState<Resume[]>([]);
  const [selectedResume, setSelectedResume] = useState<Resume | null>(null);
  const selectedSections = selectedResume ? getResumeSections(selectedResume) : null;

  useEffect(() => {
    api.resumes().then(setResumes);
  }, []);

  return (
    <div className="space-y-6">
      <section>
        <h1 className="text-3xl font-bold">Candidate Directory</h1>
        <p className="mt-2 text-slate-600">Worldwide candidate profiles with experience, education, skills, and career summaries.</p>
      </section>
      <div className="grid gap-4 lg:grid-cols-3">
        {resumes.slice(0, 60).map((resume) => (
          <ResumeCard key={resume.id} resume={resume} onClick={() => setSelectedResume(resume)} />
        ))}
      </div>
      {selectedResume && selectedSections && (
        <div className="fixed inset-0 z-50 bg-slate-950/40 p-4" role="dialog" aria-modal="true" onClick={() => setSelectedResume(null)}>
          <div className="mx-auto max-h-[90vh] max-w-3xl overflow-y-auto border border-slate-300 bg-white p-6 shadow-xl" onClick={(event) => event.stopPropagation()}>
            <div className="flex items-start justify-between gap-4 border-b border-slate-200 pb-4">
              <div>
                <h2 className="text-2xl font-semibold tracking-tight">{selectedResume.name}</h2>
                <div className="mt-2 text-sm text-slate-500">{selectedResume.experience} years · {selectedResume.education}</div>
              </div>
              <Button className="border-slate-300 bg-white text-slate-700 hover:border-slate-400 hover:bg-slate-50" onClick={() => setSelectedResume(null)}>Close</Button>
            </div>
            <div className="mt-5 flex flex-wrap gap-1.5">
              {selectedResume.skills.map((skill) => <Badge key={skill}>{skill}</Badge>)}
            </div>
            <div className="mt-6 space-y-6 text-sm text-slate-700">
              <ResumeSection title="Summary">
                <p className="leading-7">{selectedSections.summary}</p>
              </ResumeSection>

              <ResumeSection title="Work Experience">
                <div className="space-y-4">
                  {selectedSections.workExperience.map((item) => (
                    <div key={`${item.company}-${item.period}`} className="border-l-2 border-slate-200 pl-4">
                      <div className="font-semibold text-slate-950">{item.title}</div>
                      <div className="mt-1 text-slate-500">{item.company} · {item.location} · {item.period}</div>
                      <ul className="mt-2 list-disc space-y-1 pl-5 leading-6">
                        {item.highlights.map((highlight) => <li key={highlight}>{highlight}</li>)}
                      </ul>
                    </div>
                  ))}
                </div>
              </ResumeSection>

              <ResumeSection title="Education">
                <p>{selectedResume.education}</p>
              </ResumeSection>

              <ResumeSection title="Certifications">
                <ul className="list-disc space-y-1 pl-5">
                  {selectedSections.certifications.map((certification) => <li key={certification}>{certification}</li>)}
                </ul>
              </ResumeSection>

              {selectedResume.contact_info && (
                <ResumeSection title="Contact Info">
                  <div className="grid gap-2 sm:grid-cols-2">
                    {Object.entries(selectedResume.contact_info).filter(([, value]) => value).map(([key, value]) => (
                      <div key={key}><span className="font-semibold capitalize">{key.replace("_", " ")}:</span> {value}</div>
                    ))}
                  </div>
                </ResumeSection>
              )}

              {!!selectedSections.projects.length && (
                <ResumeSection title="Projects">
                  <div className="space-y-3">
                    {selectedSections.projects.map((project) => (
                      <div key={project.name}>
                        <div className="font-semibold text-slate-950">{project.name}</div>
                        <p className="mt-1 leading-6">{project.description}</p>
                        <div className="mt-2 flex flex-wrap gap-1">
                          {project.technologies.map((technology) => <Badge key={technology}>{technology}</Badge>)}
                        </div>
                      </div>
                    ))}
                  </div>
                </ResumeSection>
              )}

              {!!selectedSections.languages.length && (
                <ResumeSection title="Languages">
                  <p>{selectedSections.languages.join(", ")}</p>
                </ResumeSection>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

function ResumeCard({ resume, onClick }: { resume: Resume; onClick: () => void }) {
  const sections = getResumeSections(resume);

  return (
    <Card className="cursor-pointer transition hover:border-blue-300 hover:bg-blue-50/20" onClick={onClick}>
      <CardTitle>{resume.name}</CardTitle>
      <CardDescription className="mt-1">{resume.experience} years · {resume.education}</CardDescription>
      <div className="mt-4 flex flex-wrap gap-1">
        {resume.skills.slice(0, 7).map((skill) => (
          <Badge key={skill}>{skill}</Badge>
        ))}
      </div>
      <p className="mt-4 line-clamp-3 text-sm text-slate-600">{sections.summary}</p>
    </Card>
  );
}

function ResumeSection({ title, children }: { title: string; children: ReactNode }) {
  return (
    <section>
      <h3 className="border-b border-slate-200 pb-2 text-xs font-semibold uppercase tracking-wide text-slate-500">{title}</h3>
      <div className="mt-3">{children}</div>
    </section>
  );
}
