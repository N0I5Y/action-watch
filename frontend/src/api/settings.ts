import { apiGet, apiPatch } from "./http";

interface Settings {
    slack_webhook_url: string | null;
    teams_webhook_url: string | null;
    alert_threshold_minutes: number;
    alert_on_delayed: boolean;
    alert_on_stuck: boolean;
    alert_on_anomaly: boolean;
    stuck_threshold_multiplier: number;
    anomaly_threshold_stddev: number;
}

export async function getSettings(installationId: number): Promise<Settings> {
    return apiGet<Settings>(`/api/settings/${installationId}`);
}

export async function updateSettings(installationId: number, settings: Partial<Settings>): Promise<Settings> {
    return apiPatch<Settings>(`/api/settings/${installationId}`, settings);
}
