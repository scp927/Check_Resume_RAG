"use client";

import { useEffect, useState } from "react";
import type { ReactNode } from "react";

import { RankingTable } from "@/components/ats/ranking-table";
import { ScoreBreakdown } from "@/components/ats/score-breakdown";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { API_BASE, api } from "@/lib/api";
import { getResumeSections } from "@/lib/resume-utils";
import type { ATSRunResponse, ATSRunStreamEvent, CandidateScore, Job, LangGraphSearchResponse, WorkflowStep } from "@/types/ats";

export default function ATSRunPage() {
  const [jobs, setJobs] = useState<Job[]>([]);
  const [jobId, setJobId] = useState("job-001");
  const [result, setResult] = useState<ATSRunResponse | null>(null);
  const [searchResult, setSearchResult] = useState<LangGraphSearchResponse | null>(null);
  const [selectedCandidate, setSelectedCandidate] = useState<CandidateScore | null>(null);
  const [workflowSteps, setWorkflowSteps] = useState<WorkflowStep[]>([]);
  const [currentWorkflowStep, setCurrentWorkflowStep] = useState<WorkflowStep | null>(null);
  const [previousWorkflowStep, setPreviousWorkflowStep] = useState<WorkflowStep | null>(null);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    api.jobs().then((items) => {
      setJobs(items);
      setJobId(items[0]?.id ?? "job-001");
    });
  }, []);

  async function runAts() {
    setLoading(true);
    setResult(null);
    setSearchResult(null);
    setSelectedCandidate(null);
    setWorkflowSteps([]);
    setCurrentWorkflowStep(null);
    setPreviousWorkflowStep(null);
    setError("");
    try {
      const response = await fetch(`${API_BASE}/ats/run/stream`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ job_id: jobId, top_k: 15 })
      });
      if (!response.ok || !response.body) {
        throw new Error(`ATS stream failed: ${response.status}`);
      }
      const atsResult = await readAtsStream(response.body);
      const selectedJob = jobs.find((job) => job.id === jobId) ?? atsResult?.job;
      if (selectedJob) {
        const semanticResult = await api.langGraphSearch({
          query: `${selectedJob.title} ${selectedJob.required_skills.join(" ")}`,
          job_description: selectedJob.description,
          top_k: 15,
          max_iterations: 2,
          validation_threshold: 72
        });
        setSearchResult(semanticResult);
      }
    } catch (exc) {
      setError(exc instanceof Error ? exc.message : "Screening run failed.");
    } finally {
      setLoading(false);
    }
  }

  async function readAtsStream(body: ReadableStream<Uint8Array>) {
    const reader = body.getReader();
    const decoder = new TextDecoder();
    let buffer = "";
    let finalResult: ATSRunResponse | null = null;

    while (true) {
      const { value, done } = await reader.read();
      if (done) break;
      buffer += decoder.decode(value, { stream: true });
      const lines = buffer.split("\n");
      buffer = lines.pop() ?? "";
      for (const line of lines) {
        if (!line.trim()) continue;
        finalResult = applyAtsEvent(JSON.parse(line) as ATSRunStreamEvent) ?? finalResult;
      }
    }
    if (buffer.trim()) {
      finalResult = applyAtsEvent(JSON.parse(buffer) as ATSRunStreamEvent) ?? finalResult;
    }
    return finalResult;
  }

  function applyAtsEvent(event: ATSRunStreamEvent) {
    if (event.type === "error") {
      setError(event.message);
      return null;
    }
    setWorkflowSteps((steps) => upsertStep(steps, event.step));
    showWorkflowStep(event.step);
    if (event.type === "final") {
      setResult(event.result);
      return event.result;
    }
    return null;
  }

  function showWorkflowStep(nextStep: WorkflowStep) {
    setCurrentWorkflowStep((currentStep) => {
      if (currentStep && currentStep.step !== nextStep.step) {
        setPreviousWorkflowStep(currentStep);
      }
      return nextStep;
    });
  }

  const topCandidate = result?.leaderboard[0];

  return (
    <div className="space-y-6">
      <section>
        <h1 className="text-3xl font-bold">Screening Run</h1>
      </section>

      <section className="border-b border-slate-200 bg-white p-5">
        <h2 className="text-base font-semibold tracking-tight text-slate-950">Select job description</h2>
        <div className="mt-4 flex flex-col gap-3 md:flex-row">
          <select className="min-h-11 flex-1 border border-slate-300 bg-white px-4" value={jobId} onChange={(event) => setJobId(event.target.value)}>
            {jobs.map((job) => <option key={job.id} value={job.id}>{job.title}</option>)}
          </select>
          <Button onClick={runAts} disabled={loading}>{loading ? "Running..." : "Run ATS + Search"}</Button>
        </div>
      </section>

      <section className="bg-white/55 p-5 opacity-70">
        <WorkflowTicker
          currentStep={currentWorkflowStep ?? idleStep}
          previousStep={previousWorkflowStep}
          isRunning={loading}
          completedCount={workflowSteps.length}
        />
        {error && <div className="mt-4 border border-red-300 bg-red-50 p-3 text-sm text-red-700">{error}</div>}
      </section>

      {result && (
        <div className="result-reveal space-y-4">
          <div className="grid gap-4 lg:grid-cols-[0.8fr_1.2fr]">
            <section className="border-b border-slate-200 bg-white p-5">
              <h2 className="text-base font-semibold tracking-tight text-slate-950">JD parsed output</h2>
              <div className="mt-4 space-y-3 text-sm">
                <div><strong>Experience:</strong> {result.parsed_jd.experience_level} · {result.parsed_jd.min_experience}+ years</div>
                <div className="flex flex-wrap gap-1">
                  {result.parsed_jd.required_skills.map((skill) => <Badge key={skill}>{skill}</Badge>)}
                </div>
                <div className="text-slate-600">Domains: {result.parsed_jd.domain_keywords.join(", ") || "none detected"}</div>
              </div>
            </section>
            {topCandidate && (
              <section className="border-b border-slate-200 bg-white p-5">
                <h2 className="text-base font-semibold tracking-tight text-slate-950">Top candidate breakdown</h2>
                <div className="mt-1 text-sm text-slate-500">{topCandidate.name} · Final score {topCandidate.score}</div>
                <div className="mt-4">
                  <ScoreBreakdown candidate={topCandidate} />
                </div>
              </section>
            )}
          </div>
          {searchResult && (
            <section className="border-b border-slate-200 bg-white p-5">
              <h2 className="text-base font-semibold tracking-tight text-slate-950">Search validation</h2>
              <div className="mt-3 grid gap-3 text-sm text-slate-600 md:grid-cols-3">
                <div><span className="font-semibold text-slate-950">Status:</span> {searchResult.validated ? "Validated" : "Needs review"}</div>
                <div><span className="font-semibold text-slate-950">Score:</span> {searchResult.validation_score}</div>
                <div><span className="font-semibold text-slate-950">Iterations:</span> {searchResult.iterations}</div>
              </div>
              <p className="mt-3 text-sm leading-6 text-slate-600">{searchResult.expanded_query}</p>
            </section>
          )}
          <RankingTable candidates={result.leaderboard} onCandidateClick={setSelectedCandidate} />
        </div>
      )}
      {selectedCandidate && (
        <CandidateModal candidate={selectedCandidate} onClose={() => setSelectedCandidate(null)} />
      )}
    </div>
  );
}

const idleStep: WorkflowStep = {
  step: "waiting",
  status: "idle",
  message: "Select a JD and run ATS + Search to see process progress.",
  details: {}
};

function upsertStep(steps: WorkflowStep[], nextStep: WorkflowStep) {
  const index = steps.findIndex((step) => step.step === nextStep.step);
  if (index === -1) {
    return [...steps, nextStep];
  }
  return steps.map((step, currentIndex) => (currentIndex === index ? nextStep : step));
}

function WorkflowTicker({
  currentStep,
  previousStep,
  isRunning,
  completedCount
}: {
  currentStep: WorkflowStep;
  previousStep: WorkflowStep | null;
  isRunning: boolean;
  completedCount: number;
}) {
  return (
    <div className="border-y border-slate-200 px-5 py-4 text-slate-700">
      <div className="mb-4 flex items-center justify-between border-b border-slate-200 pb-3">
        <div className="text-xs font-semibold uppercase tracking-widest text-slate-400">Process</div>
        <div className="text-xs font-semibold uppercase tracking-wide text-slate-400">
          {isRunning ? "Running" : completedCount ? "Complete" : "Idle"}
        </div>
      </div>
      <div className="mb-4 h-1 overflow-hidden border border-slate-200 bg-slate-100">
        <div className={`h-full w-1/2 bg-blue-500/45 ${isRunning ? "workflow-scan" : ""}`} />
      </div>
      <div className="h-36 overflow-hidden">
        <div
          key={previousStep ? `${previousStep.step}->${currentStep.step}` : currentStep.step}
          className={`h-72 ${previousStep ? "workflow-message-enter" : "workflow-message-initial"}`}
        >
          {previousStep && (
            <WorkflowMessage
              key={`previous-${previousStep.step}-${previousStep.message}`}
              step={previousStep}
            />
          )}
          <WorkflowMessage
            key={`current-${currentStep.step}-${currentStep.message}`}
            step={currentStep}
            showCursor={isRunning}
          />
        </div>
      </div>
      <div className="mt-4 border-t border-slate-200 pt-3 text-xs text-slate-400">
        {completedCount ? `${completedCount} process events completed` : "Waiting for ATS run"}
      </div>
    </div>
  );
}

function WorkflowMessage({
  step,
  showCursor = false
}: {
  step: WorkflowStep;
  showCursor?: boolean;
}) {
  return (
    <div className="flex h-36 flex-col justify-start">
      <div className="text-xs font-semibold uppercase tracking-widest text-blue-500">{step.status}</div>
      <div className="mt-3 text-xl font-semibold text-slate-800">
        {step.step.replaceAll("_", " ")}
        {showCursor && <span className="ml-1 animate-pulse text-blue-500">|</span>}
      </div>
      <p className="mt-3 max-w-2xl text-sm leading-6 text-slate-500">{step.message}</p>
    </div>
  );
}

function CandidateModal({ candidate, onClose }: { candidate: CandidateScore; onClose: () => void }) {
  const resume = candidate.resume;
  const sections = resume ? getResumeSections(resume) : null;

  return (
    <div className="fixed inset-0 z-50 bg-slate-950/40 p-4" role="dialog" aria-modal="true" onClick={onClose}>
      <div className="mx-auto max-h-[90vh] max-w-5xl overflow-y-auto border border-slate-300 bg-white p-6 shadow-xl" onClick={(event) => event.stopPropagation()}>
        <div className="flex items-start justify-between gap-4 border-b border-slate-200 pb-4">
          <div>
            <h2 className="text-2xl font-semibold tracking-tight">{candidate.name}</h2>
            <div className="mt-2 text-sm text-slate-500">Final score {candidate.score} · Semantic {candidate.semantic_similarity}</div>
          </div>
          <Button className="border-slate-300 bg-white text-slate-700 hover:border-slate-400 hover:bg-slate-50" onClick={onClose}>Close</Button>
        </div>

        <div className="mt-5 grid gap-6 lg:grid-cols-[0.7fr_1.3fr]">
          <section className="space-y-4">
            <div className="border border-slate-200 p-4">
              <h3 className="text-xs font-semibold uppercase tracking-wide text-slate-500">ATS evidence</h3>
              <p className="mt-3 text-sm leading-6 text-slate-700">{candidate.explanation}</p>
              <div className="mt-4 flex flex-wrap gap-1.5">
                {candidate.matching_skills.map((skill) => <Badge key={skill}>{skill}</Badge>)}
              </div>
            </div>

            <div className="border border-slate-200 p-4">
              <h3 className="text-xs font-semibold uppercase tracking-wide text-slate-500">Score breakdown</h3>
              <div className="mt-4">
                <ScoreBreakdown candidate={candidate} />
              </div>
            </div>

            {!!candidate.missing_skills.length && (
              <div className="border border-slate-200 p-4">
                <h3 className="text-xs font-semibold uppercase tracking-wide text-slate-500">Missing skills</h3>
                <div className="mt-3 flex flex-wrap gap-1.5">
                  {candidate.missing_skills.map((skill) => <Badge key={skill}>{skill}</Badge>)}
                </div>
              </div>
            )}
          </section>

          <section className="space-y-6 text-sm text-slate-700">
            {resume ? (
              <>
                <CandidateResumeSection title="Summary">
                  <p className="leading-7">{sections?.summary}</p>
                </CandidateResumeSection>

                <CandidateResumeSection title="Work Experience">
                  <div className="space-y-4">
                    {sections?.workExperience.map((item) => (
                      <div key={`${item.company}-${item.period}`} className="border-l-2 border-slate-200 pl-4">
                        <div className="font-semibold text-slate-950">{item.title}</div>
                        <div className="mt-1 text-slate-500">{item.company} · {item.location} · {item.period}</div>
                        <ul className="mt-2 list-disc space-y-1 pl-5 leading-6">
                          {item.highlights.map((highlight) => <li key={highlight}>{highlight}</li>)}
                        </ul>
                      </div>
                    ))}
                  </div>
                </CandidateResumeSection>

                <CandidateResumeSection title="Education">
                  <p>{resume.education}</p>
                </CandidateResumeSection>

                <CandidateResumeSection title="Certifications">
                  <ul className="list-disc space-y-1 pl-5">
                    {sections?.certifications.map((certification) => <li key={certification}>{certification}</li>)}
                  </ul>
                </CandidateResumeSection>

                {resume.contact_info && (
                  <CandidateResumeSection title="Contact Info">
                    <div className="grid gap-2 sm:grid-cols-2">
                      {Object.entries(resume.contact_info).filter(([, value]) => value).map(([key, value]) => (
                        <div key={key}><span className="font-semibold capitalize">{key.replace("_", " ")}:</span> {value}</div>
                      ))}
                    </div>
                  </CandidateResumeSection>
                )}

                {!!sections?.projects.length && (
                  <CandidateResumeSection title="Projects">
                    <div className="space-y-3">
                      {sections.projects.map((project) => (
                        <div key={project.name}>
                          <div className="font-semibold text-slate-950">{project.name}</div>
                          <p className="mt-1 leading-6">{project.description}</p>
                          <div className="mt-2 flex flex-wrap gap-1">
                            {project.technologies.map((technology) => <Badge key={technology}>{technology}</Badge>)}
                          </div>
                        </div>
                      ))}
                    </div>
                  </CandidateResumeSection>
                )}

                {!!sections?.languages.length && (
                  <CandidateResumeSection title="Languages">
                    <p>{sections.languages.join(", ")}</p>
                  </CandidateResumeSection>
                )}
              </>
            ) : (
              <p className="leading-7">{candidate.explanation}</p>
            )}
          </section>
        </div>
      </div>
    </div>
  );
}

function CandidateResumeSection({ title, children }: { title: string; children: ReactNode }) {
  return (
    <section>
      <h3 className="border-b border-slate-200 pb-2 text-xs font-semibold uppercase tracking-wide text-slate-500">{title}</h3>
      <div className="mt-3">{children}</div>
    </section>
  );
}
