// Define Workflow interface locally to avoid circular/ambiguous imports
export interface Workflow {
    id: number;
    name: string;
    path: string;
    state: string;
    last_run_at: string | null;
    status?: string; // Add status for UI compatibility
    repo_full_name: string;
    cron_expression: string | null;
}

const API_BASE = import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000/api';

export async function fetchWorkflows(
    _installationId: number,
): Promise<Workflow[]> {
    const url = new URL(`${API_BASE}/workflows`);
    // In a real app we might use installationId param, 
    // but for now the backend determines access via cookies/token
    // url.searchParams.set('installationId', String(installationId));

    const res = await fetch(url.toString());
    if (!res.ok) throw new Error('Failed to load workflows');
    return res.json();
}
