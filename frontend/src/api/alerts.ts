import { apiGet, apiPatch } from "./http";

export interface Alert {
    id: number;
    workflow_id: number | null;
    alert_type: string;
    severity: string;
    message: string;
    detected_at: string;
    acknowledged: boolean;
    acknowledged_at: string | null;
    workflow_name: string | null;
    repository_name: string | null;
}

export async function getAlerts(
    installationId: number,
    limit: number = 50,
    alertType?: string,
    acknowledged?: boolean
): Promise<Alert[]> {
    let url = `/api/alerts?installation_id=${installationId}&limit=${limit}`;
    if (alertType) url += `&alert_type=${alertType}`;
    if (acknowledged !== undefined) url += `&acknowledged=${acknowledged}`;
    return apiGet<Alert[]>(url);
}

export async function acknowledgeAlert(alertId: number, acknowledged: boolean): Promise<void> {
    await apiPatch(`/api/alerts/${alertId}/acknowledge`, { acknowledged });
}
