export const env = {
  apiUrl: import.meta.env.VITE_API_URL ?? "/api",
  useMockAuth: import.meta.env.VITE_USE_MOCK_AUTH === "true",
  mockClientId: Number(import.meta.env.VITE_MOCK_CLIENT_ID ?? 1),
} as const;