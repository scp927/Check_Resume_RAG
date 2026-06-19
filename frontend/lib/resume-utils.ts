import type { Resume } from "@/types/ats";

type ResumeSections = {
  summary: string;
  workExperience: NonNullable<Resume["work_exp"]>;
  education: string;
  certifications: string[];
  projects: NonNullable<Resume["projects"]>;
  languages: string[];
};

const SECTION_NAMES = ["Summary", "Skills", "Work Experience", "Education", "Certifications", "Projects", "Languages"];

export function getResumeSections(resume: Resume): ResumeSections {
  const parsed = parseRawResume(resume.raw_text);
  return {
    summary: cleanSectionText(resume.summary) || parsed.summary,
    workExperience: resume.work_exp?.length ? resume.work_exp : resume.work_experience?.length ? resume.work_experience : parsed.workExperience,
    education: cleanSectionText(resume.education) || parsed.education,
    certifications: resume.certification?.length ? resume.certification : resume.certifications?.length ? resume.certifications : parsed.certifications,
    projects: resume.projects?.length ? resume.projects : parsed.projects,
    languages: resume.languages?.length ? resume.languages : parsed.languages
  };
}

function parseRawResume(rawText: string): ResumeSections {
  const sections = Object.fromEntries(SECTION_NAMES.map((name) => [name, ""])) as Record<string, string>;
  const pattern = new RegExp(`(?:^|\\n)(${SECTION_NAMES.join("|")})\\n`, "g");
  const matches = [...rawText.matchAll(pattern)];

  matches.forEach((match, index) => {
    const title = match[1];
    const start = (match.index ?? 0) + match[0].length;
    const end = matches[index + 1]?.index ?? rawText.length;
    sections[title] = rawText.slice(start, end).trim();
  });

  return {
    summary: sections.Summary || rawText.split("\n\n")[0] || "",
    workExperience: parseWorkExperience(sections["Work Experience"]),
    education: sections.Education,
    certifications: sections.Certifications.split("\n").map((item) => item.replace(/^-\s*/, "").trim()).filter(Boolean),
    projects: parseProjects(sections.Projects),
    languages: sections.Languages.split(",").map((item) => item.trim()).filter(Boolean)
  };
}

function parseWorkExperience(text: string): ResumeSections["workExperience"] {
  if (!text) return [];
  const items: ResumeSections["workExperience"] = [];
  let current: ResumeSections["workExperience"][number] | null = null;

  text.split("\n").forEach((line) => {
    const cleanLine = line.trim();
    if (!cleanLine) return;
    if (cleanLine.startsWith("-")) {
      current?.highlights.push(cleanLine.replace(/^-\s*/, ""));
      return;
    }
    const [title = "", company = "", location = "", period = ""] = cleanLine.split("|").map((part) => part.trim());
    current = { title, company, location, period, highlights: [] };
    items.push(current);
  });

  return items;
}

function parseProjects(text: string): ResumeSections["projects"] {
  if (!text) return [];
  return text.split("\n").filter(Boolean).map((line) => {
    const [name = "Project", description = line] = line.split(":");
    return { name: name.trim(), description: description.trim(), technologies: [] };
  });
}

function cleanSectionText(value?: string) {
  if (!value) return "";
  return value.replace(/^Summary\s*/i, "").trim();
}
