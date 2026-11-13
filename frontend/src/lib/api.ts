/**
 * Centralized Resilient Analytics API Client
 * Uses relative `/api/*` endpoints proxied through Next.js rewrite
 * with retry logic, timeouts, and graceful error envelopes.
 */

const DEFAULT_TIMEOUT_MS = 6000;

export async function fetchWithTimeout<T>(
  endpoint: string,
  options: RequestInit = {},
  timeoutMs: number = DEFAULT_TIMEOUT_MS,
  retries: number = 2
): Promise<{ data: T | null; error: string | null }> {
  for (let attempt = 0; attempt <= retries; attempt++) {
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), timeoutMs);

    try {
      const response = await fetch(endpoint, {
        ...options,
        signal: controller.signal,
        headers: {
          Accept: "application/json",
          ...(options.headers || {}),
        },
      });

      clearTimeout(timeoutId);

      if (!response.ok) {
        if (attempt < retries) {
          await new Promise((r) => setTimeout(r, 200));
          continue;
        }
        return {
          data: null,
          error: `HTTP ${response.status}: ${response.statusText}`,
        };
      }

      const data = (await response.json()) as T;
      return { data, error: null };
    } catch (err: any) {
      clearTimeout(timeoutId);
      if (attempt < retries) {
        await new Promise((r) => setTimeout(r, 200));
        continue;
      }
      const message =
        err.name === "AbortError"
          ? "Request timed out after 6 seconds"
          : err.message || "Failed to connect to analytics engine";
      return { data: null, error: message };
    }
  }
  return { data: null, error: "Max retries reached" };
}

export const api = {
  getOverview: () => fetchWithTimeout<any>("/api/overview"),
  getBatters: (limit: number = 200) => fetchWithTimeout<any[]>(`/api/rankings/batters?limit=${limit}`),
  getBowlers: (limit: number = 200) => fetchWithTimeout<any[]>(`/api/rankings/bowlers?limit=${limit}`),
  getPlayerProfile: (id: number) => fetchWithTimeout<any>(`/api/players/${id}`),
  getPlayerMatchHistory: (id: number, limit: number = 15) =>
    fetchWithTimeout<any[]>(`/api/players/${id}/match-history?limit=${limit}`),
  getDataAudit: () => fetchWithTimeout<any>("/api/data-audit"),
  getHealth: () => fetchWithTimeout<any>("/api/health", {}, 3000),
};
