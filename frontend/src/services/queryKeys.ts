export const queryKeys = {
  tickets: ["tickets"] as const,
  ticket: (id: number) => ["tickets", "detail", id] as const,
  visits: ["visits"] as const,
  history: ["history"] as const,
  inventory: ["inventory"] as const,
  evaluations: ["evaluations"] as const,
  people: (kind: string) => ["people", kind] as const,
};
