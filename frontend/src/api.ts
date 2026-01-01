// src/api.ts
export interface WorkflowStatus {
  id: number;
  repo_full_name: string;
  name: string;
  cron_expression: string | null;
  last_run_at: string | null;
  last_missed_at: string | null;
  missed_count_24h: number;
  status: 'HEALTHY' | 'MISSED' | 'AT_RISK' | string;
}

export interface SummaryStats {
  total_workflows: number;
  healthy_workflows: number;
  workflows_with_misses_24h: number;
  last_missed_at: string | null;
}

const API_BASE = 'http://127.0.0.1:8000/api';

export async function fetchSummary(): Promise<SummaryStats> {
  const res = await fetch(`${API_BASE}/summary`);
  if (!res.ok) throw new Error('Failed to load summary');
  return res.json();
}

export async function fetchWorkflowsStatus(
  q: string,
): Promise<WorkflowStatus[]> {
  const url = new URL(`${API_BASE}/workflows/status`);
  if (q) url.searchParams.set('q', q);
  const res = await fetch(url.toString());
  if (!res.ok) throw new Error('Failed to load workflows');
  return res.json();
}
