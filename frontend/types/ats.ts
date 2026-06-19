export type Resume = {
  id: string;
  name: string;
  skills: string[];
  experience: number;
  education: string;
  raw_text: string;
  summary?: string;
  work_exp?: Array<{
    title: string;
    company: string;
    location: string;
    period: string;
    highlights: string[];
  }>;
  work_experience?: Array<{
    title: string;
    company: string;
    location: string;
    period: string;
    highlights: string[];
  }>;
  certification?: string[];
  certifications?: string[];
  contact_info?: {
    email?: string | null;
    phone?: string | null;
    location?: string | null;
    linkedin?: string | null;
    github?: string | null;
  } | null;
  projects?: Array<{
    name: string;
    description: string;
    technologies: string[];
  }>;
  languages?: string[];
};

export type Job = {
  id: string;
  title: string;
  description: string;
  required_skills: string[];
  poster?: {
    name: string;
    degree: string;
    headline: string;
    subheadline: string;
    label: string;
  } | null;
};

export type ParsedJD = {
  required_skills: string[];
  nice_to_have_skills: string[];
  experience_level: string;
  min_experience: number;
  domain_keywords: string[];
};

export type CandidateScore = {
  resume_id: string;
  name: string;
  score: number;
  semantic_similarity: number;
  skill_match_ratio: number;
  matching_skills: string[];
  missing_skills: string[];
  explanation: string;
  strengths: string[];
  weaknesses: string[];
  reason_breakdown: {
    semantic: number;
    skills: number;
    experience: number;
    keyword_bonus: number;
  };
  resume?: Resume;
};

export type ATSRunResponse = {
  job: Job | null;
  parsed_jd: ParsedJD;
  candidate_count: number;
  leaderboard: CandidateScore[];
  process_visibility: Record<string, unknown>;
};

export type SearchResult = {
  resume: Resume;
  similarity: number;
};

export type WorkflowStep = {
  step: string;
  status: string;
  message: string;
  details: Record<string, unknown>;
};

export type LangGraphSearchResponse = {
  query: string;
  expanded_query: string;
  iterations: number;
  validated: boolean;
  validation_score: number;
  parsed_jd: ParsedJD;
  steps: WorkflowStep[];
  leaderboard: CandidateScore[];
};

export type LangGraphStreamEvent =
  | {
      type: "step" | "step_update" | "validation" | "loop";
      step: WorkflowStep;
      parsed_jd?: ParsedJD;
      validation_score?: number;
      expanded_query?: string;
    }
  | {
      type: "partial_results";
      step: WorkflowStep;
      leaderboard: CandidateScore[];
    }
  | {
      type: "final";
      step: WorkflowStep;
      result: LangGraphSearchResponse;
    };

export type ATSRunStreamEvent =
  | {
      type: "step" | "step_update";
      step: WorkflowStep;
    }
  | {
      type: "final";
      step: WorkflowStep;
      result: ATSRunResponse;
    }
  | {
      type: "error";
      message: string;
    };

export type JDResumeCheckResponse = {
  parsed_jd: ParsedJD;
  candidate: CandidateScore;
  validated: boolean;
  validation_score: number;
  steps: WorkflowStep[];
};
