import { format, formatDistanceToNow, parseISO } from 'date-fns';


export function formatDateTime(dateStr: string | null | undefined, _timezone: string = 'UTC'): string {
    if (!dateStr) return 'Never';
    try {
        const date = parseISO(dateStr);
        return format(date, 'MMM d, yyyy HH:mm:ss'); // Simplified for MVP, ignoring timezone conversion complexity for now
    } catch (e) {
        return 'Invalid Date';
    }
}

export function formatRelativeTime(dateStr: string | null | undefined): string {
    if (!dateStr) return '';
    try {
        const date = parseISO(dateStr);
        return formatDistanceToNow(date, { addSuffix: true });
    } catch (e) {
        return '';
    }
}
