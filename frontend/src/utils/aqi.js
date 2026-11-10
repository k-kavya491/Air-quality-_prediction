export const CATEGORIES = [
  { name: "Good", color: "#22c55e", range: "0–50" },
  { name: "Moderate", color: "#eab308", range: "51–100" },
  { name: "Unhealthy for Sensitive Groups", color: "#f97316", range: "101–150" },
  { name: "Unhealthy", color: "#ef4444", range: "151–200" },
  { name: "Very Unhealthy", color: "#a855f7", range: "201–300" },
  { name: "Hazardous", color: "#be123c", range: "301+" },
];

export function colorFor(categoryName) {
  const found = CATEGORIES.find((c) => c.name === categoryName);
  return found ? found.color : "#64748b";
}

export function categoryFor(aqi) {
  if (aqi <= 50) return "Good";
  if (aqi <= 100) return "Moderate";
  if (aqi <= 150) return "Unhealthy for Sensitive Groups";
  if (aqi <= 200) return "Unhealthy";
  if (aqi <= 300) return "Very Unhealthy";
  return "Hazardous";
}