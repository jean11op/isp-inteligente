export const env = {
  apiUrl: import.meta.env.VITE_API_URL ?? "/api",
  useMockAuth: import.meta.env.VITE_USE_MOCK_AUTH === "true",
} as const;