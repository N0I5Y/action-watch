// src/api/http.ts
const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8000";

function getAuthToken(): string | undefined {
  const value = `; ${document.cookie}`;
  const parts = value.split(`; gh_token=`);
  if (parts.length === 2) return parts.pop()?.split(';').shift();
  return undefined;
}

function getHeaders(headers: Record<string, string> = {}): Record<string, string> {
  const token = getAuthToken();
  const authHeaders: Record<string, string> = {
    "Content-Type": "application/json",
    ...headers,
  };

  if (token) {
    authHeaders["Authorization"] = `Bearer ${token}`;
  }

  return authHeaders;
}

export async function apiGet<T>(path: string): Promise<T> {
  const res = await fetch(`${API_BASE_URL}${path}`, {
    headers: getHeaders(),
  });

  if (!res.ok) {
    const text = await res.text().catch(() => "");
    throw new Error(
      `API GET ${path} failed: ${res.status} ${res.statusText} ${text}`,
    );
  }

  return (await res.json()) as T;
}

export async function apiPost<T>(path: string, body: any): Promise<T> {
  const res = await fetch(`${API_BASE_URL}${path}`, {
    method: "POST",
    headers: getHeaders(),
    body: JSON.stringify(body),
  });

  if (!res.ok) {
    const text = await res.text().catch(() => "");
    throw new Error(
      `API POST ${path} failed: ${res.status} ${res.statusText} ${text}`,
    );
  }

  return (await res.json()) as T;
}

export async function apiPatch<T>(path: string, body: any): Promise<T> {
  const res = await fetch(`${API_BASE_URL}${path}`, {
    method: "PATCH",
    headers: getHeaders(),
    body: JSON.stringify(body),
  });

  if (!res.ok) {
    const text = await res.text().catch(() => "");
    throw new Error(
      `API PATCH ${path} failed: ${res.status} ${res.statusText} ${text}`,
    );
  }

  return (await res.json()) as T;
}
