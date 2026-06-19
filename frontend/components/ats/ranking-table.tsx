import { Badge } from "@/components/ui/badge";
import type { CandidateScore } from "@/types/ats";

export function RankingTable({
  candidates,
  onCandidateClick
}: {
  candidates: CandidateScore[];
  onCandidateClick?: (candidate: CandidateScore) => void;
}) {
  return (
    <div className="overflow-hidden border border-slate-300 bg-white shadow-sm">
      <table className="w-full text-left text-sm">
        <thead className="border-b border-slate-300 bg-slate-100 text-xs uppercase tracking-wide text-slate-600">
          <tr>
            <th className="p-3">Rank</th>
            <th className="p-3">Candidate</th>
            <th className="p-3">Score</th>
            <th className="p-3">Semantic</th>
            <th className="p-3">Matched Skills</th>
          </tr>
        </thead>
        <tbody className="divide-y divide-slate-200">
          {candidates.map((candidate, index) => (
            <tr
              key={candidate.resume_id}
              className={onCandidateClick ? "cursor-pointer align-top hover:bg-blue-50/50" : "align-top hover:bg-slate-50"}
              onClick={() => onCandidateClick?.(candidate)}
            >
              <td className="p-3 font-semibold">#{index + 1}</td>
              <td className="p-3">
                <div className="font-semibold text-slate-900">{candidate.name}</div>
                <div className="mt-1 text-xs text-slate-500">{candidate.explanation}</div>
              </td>
              <td className="p-3 text-lg font-bold text-blue-600">{candidate.score}</td>
              <td className="p-3">{candidate.semantic_similarity}</td>
              <td className="p-3">
                <div className="flex flex-wrap gap-1">
                  {candidate.matching_skills.slice(0, 5).map((skill) => (
                    <Badge key={skill}>{skill}</Badge>
                  ))}
                </div>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
