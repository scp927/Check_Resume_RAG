import type { CandidateScore } from "@/types/ats";

const labels: Record<keyof CandidateScore["reason_breakdown"], string> = {
  semantic: "Semantic",
  skills: "Skills",
  experience: "Experience",
  keyword_bonus: "Keyword bonus"
};

export function ScoreBreakdown({ candidate }: { candidate: CandidateScore }) {
  return (
    <div className="space-y-3">
      {(Object.keys(candidate.reason_breakdown) as Array<keyof CandidateScore["reason_breakdown"]>).map((key) => {
        const value = candidate.reason_breakdown[key];
        return (
          <div key={key}>
            <div className="mb-1 flex justify-between text-xs text-slate-500">
              <span>{labels[key]}</span>
              <span>{value}</span>
            </div>
            <div className="h-2 overflow-hidden border border-slate-200 bg-slate-100">
              <div className="h-full bg-blue-700" style={{ width: `${Math.min(value, 40) * 2.5}%` }} />
            </div>
          </div>
        );
      })}
    </div>
  );
}
