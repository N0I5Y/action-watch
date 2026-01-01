import { useEffect } from 'react';


export interface Shortcut {
    key: string;
    ctrl?: boolean;
    meta?: boolean;
    shift?: boolean;
    alt?: boolean;
    handler: () => void;
    description?: string;
}

export function useKeyboardShortcuts(shortcuts: Shortcut[] = []) {
    // Placeholder hook for MVP
    useEffect(() => {
        const handleKeyDown = (_e: KeyboardEvent) => {
            // Implement actual shortcut logic here if needed
            // For now just logging that we received shortcuts
            console.debug('Shortcuts registered:', shortcuts.length);
        };
        window.addEventListener('keydown', handleKeyDown);
        return () => window.removeEventListener('keydown', handleKeyDown);
    }, [shortcuts]);
}
