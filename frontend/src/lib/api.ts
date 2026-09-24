import type { PredictionResult, ModelInfo } from "@/types";
const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export class ApiError extends Error {
  constructor(public status: number, message: string) { super(message); this.name = "ApiError"; }
}

async function apiFetch<T>(endpoint: string, options: RequestInit = {}, token?: string): Promise<T> {
  const headers: Record<string, string> = { ...(options.headers as Record<string, string>) };
  if (token) headers["Authorization"] = `Bearer ${token}`;
  const res = await fetch(`${API_URL}${endpoint}`, { ...options, headers });
  if (!res.ok) {
    let detail = `HTTP ${res.status}`;
    try { const d = await res.json(); detail = d.detail || detail; } catch {}
    throw new ApiError(res.status, detail);
  }
  return res.json();
}

export const api = {
  health: () => apiFetch<{ status: string; model_available: boolean }>("/health"),
  getModelInfo: (token?: string) => apiFetch<ModelInfo>("/api/model/info", {}, token),
  predict: (file: File, token?: string) => {
    const fd = new FormData(); fd.append("file", file);
    return apiFetch<PredictionResult>("/api/predict", { method: "POST", body: fd }, token);
  },
  predictWebcam: (imageDataUri: string, token?: string) =>
    apiFetch<PredictionResult>("/api/predict/webcam", {
      method: "POST", headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ image: imageDataUri }),
    }, token),
  sort: (command: string, token?: string) =>
    apiFetch("/api/hardware/sort", {
      method: "POST", headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ command }),
    }, token),
  getCategories: () => apiFetch<{ categories: any[] }>("/api/categories"),
};
