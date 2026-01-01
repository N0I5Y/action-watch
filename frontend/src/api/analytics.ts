import { apiGet } from "./http";

export interface SuccessRateDataPoint {
    date: string;
    success: number;
    failure: number;
    total: number;
}

export interface RuntimeTrendDataPoint {
    date: string;
    avg_duration_seconds: number;
    run_count: number;
}

export interface DurationStats {
    min_duration_ms: number | null;
    max_duration_ms: number | null;
    avg_duration_ms: number | null;
    p50_duration_ms: number | null;
    p95_duration_ms: number | null;
    total_runs: number;
}

export async function getSuccessRate(installationId: number, days: number = 30): Promise<SuccessRateDataPoint[]> {
    return apiGet<SuccessRateDataPoint[]>(`/api/analytics/success-rate?installation_id=${installationId}&days=${days}`);
}

export async function getRuntimeTrends(installationId: number, days: number = 30): Promise<RuntimeTrendDataPoint[]> {
    return apiGet<RuntimeTrendDataPoint[]>(`/api/analytics/runtime-trends?installation_id=${installationId}&days=${days}`);
}

export async function getDurationStats(installationId: number, days: number = 30): Promise<DurationStats> {
    return apiGet<DurationStats>(`/api/analytics/duration-stats?installation_id=${installationId}&days=${days}`);
}
