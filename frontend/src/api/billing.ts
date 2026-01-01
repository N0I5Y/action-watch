import { apiPost } from "./http";

export async function createCheckoutSession(installationId: number): Promise<{ url: string }> {
    return apiPost<{ url: string }>("/api/billing/checkout", {
        installation_id: installationId,
        success_url: window.location.href,
        cancel_url: window.location.href,
    });
}

export async function createPortalSession(installationId: number): Promise<{ url: string }> {
    return apiPost<{ url: string }>("/api/billing/portal", {
        installation_id: installationId,
        return_url: window.location.href,
    });
}
