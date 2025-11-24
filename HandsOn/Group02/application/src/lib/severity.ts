type SeverityLevel = "low" | "medium" | "high";

const normalizeSeverity = (severity?: number | null) => {
  if (!severity) return 0;
  return severity;
};

export const getSeverityLevel = (severity?: number | null): SeverityLevel => {
  const value = normalizeSeverity(severity);
  if (value >= 6) return "high";
  if (value >= 4) return "medium";
  return "low";
};

export const matchesSeverityFilter = (filter: string, severity?: number | null) => {
  if (!filter || filter === "All") return true;
  const level = getSeverityLevel(severity);

  if (filter === "Low") return level === "low";
  if (filter === "Medium") return level === "medium";
  if (filter === "High") return level === "high";

  return true;
};

export const getSeverityBadgeConfig = (severity?: number | null) => {
  const level = getSeverityLevel(severity);
  if (level === "high") {
    return { label: "High severity", class: "bg-[hsl(var(--danger))]" };
  }
  if (level === "medium") {
    return { label: "Medium severity", class: "bg-orange-500" };
  }
  return { label: "Low severity", class: "bg-green-500" };
};

export const getSeverityColor = (severity?: number | null) => {
  const level = getSeverityLevel(severity);
  if (level === "high") return "#ef4444";
  if (level === "medium") return "#f97316";
  return "#22c55e";
};

