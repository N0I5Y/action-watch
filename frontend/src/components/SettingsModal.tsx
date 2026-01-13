

import { useState, useEffect } from 'react';
import { useAuth } from '../contexts/AuthContext';

interface SettingsModalProps {
    isOpen: boolean;
    onClose: () => void;
    installationId: number;
}

interface SettingsData {
    slack_webhook_url: string | null;
    teams_webhook_url: string | null;
    alert_threshold_minutes: number;
    alert_on_delayed: boolean;
    alert_on_stuck: boolean;
    alert_on_anomaly: boolean;
    stuck_threshold_multiplier: number;
    anomaly_threshold_stddev: number;
}

export function SettingsModal({ isOpen, onClose, installationId }: SettingsModalProps) {
    const { } = useAuth(); // Removed token
    const [loading, setLoading] = useState(false);
    const [saving, setSaving] = useState(false);
    const [settings, setSettings] = useState<SettingsData>({
        slack_webhook_url: '',
        teams_webhook_url: '',
        alert_threshold_minutes: 10,
        alert_on_delayed: true,
        alert_on_stuck: true,
        alert_on_anomaly: true,
        stuck_threshold_multiplier: 2.0,
        anomaly_threshold_stddev: 2.0
    });

    useEffect(() => {
        if (isOpen && installationId) {
            fetchSettings();
        }
        // eslint-disable-next-line react-hooks/exhaustive-deps
    }, [isOpen, installationId]);

    const fetchSettings = async () => {
        setLoading(true);
        try {
            const res = await fetch(`${import.meta.env.VITE_API_URL || 'http://localhost:8000'}/api/settings/${installationId}`, {
                credentials: 'include' // Use cookie
            });
            if (res.ok) {
                const data = await res.json();
                setSettings(data);
            }
        } catch (error) {
            console.error("Failed to fetch settings", error);
        } finally {
            setLoading(false);
        }
    };

    const handleSave = async () => {
        setSaving(true);
        try {
            const res = await fetch(`${import.meta.env.VITE_API_URL || 'http://localhost:8000'}/api/settings/${installationId}`, {
                method: 'PATCH',
                headers: {
                    'Content-Type': 'application/json'
                },
                credentials: 'include', // Use cookie
                body: JSON.stringify(settings)
            });
            if (res.ok) {
                onClose();
            }
        } catch (error) {
            console.error("Failed to save settings", error);
        } finally {
            setSaving(false);
        }
    };

    if (!isOpen) return null;

    return (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm p-4">
            <div className="bg-slate-900 border border-slate-800 w-full max-w-2xl rounded-2xl shadow-2xl overflow-hidden flex flex-col max-h-[90vh]">
                {/* Header */}
                <div className="flex items-center justify-between px-6 py-4 border-b border-slate-800 bg-slate-900/50">
                    <h2 className="text-xl font-semibold text-white">Installation Settings</h2>
                    <button onClick={onClose} className="text-slate-400 hover:text-white transition-colors">
                        <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                        </svg>
                    </button>
                </div>

                {/* Content */}
                <div className="flex-1 overflow-y-auto p-6 space-y-8">
                    {loading ? (
                        <div className="flex items-center justify-center h-40">
                            <div className="w-8 h-8 border-4 border-blue-500 border-t-transparent rounded-full animate-spin" />
                        </div>
                    ) : (
                        <>
                            {/* Notifications Section */}
                            <section className="space-y-4">
                                <div>
                                    <h3 className="text-sm font-medium text-blue-400 uppercase tracking-wider mb-1">Notifications</h3>
                                    <p className="text-xs text-slate-500">Where should we send alerts?</p>
                                </div>
                                <div className="grid gap-4">
                                    <div className="space-y-2">
                                        <label className="text-sm font-medium text-slate-300">Slack Webhook URL</label>
                                        <input
                                            type="text"
                                            value={settings.slack_webhook_url || ''}
                                            onChange={(e) => setSettings({ ...settings, slack_webhook_url: e.target.value })}
                                            placeholder="https://hooks.slack.com/services/..."
                                            className="w-full px-4 py-2 bg-slate-950 border border-slate-800 rounded-lg text-slate-200 placeholder-slate-600 focus:outline-none focus:ring-2 focus:ring-blue-500/50"
                                        />
                                    </div>
                                    <div className="space-y-2">
                                        <label className="text-sm font-medium text-slate-300">Microsoft Teams Webhook URL</label>
                                        <input
                                            type="text"
                                            value={settings.teams_webhook_url || ''}
                                            onChange={(e) => setSettings({ ...settings, teams_webhook_url: e.target.value })}
                                            placeholder="https://outlook.office.com/webhook/..."
                                            className="w-full px-4 py-2 bg-slate-950 border border-slate-800 rounded-lg text-slate-200 placeholder-slate-600 focus:outline-none focus:ring-2 focus:ring-blue-500/50"
                                        />
                                    </div>
                                </div>
                            </section>

                            <hr className="border-slate-800" />

                            {/* Sensitivity Section */}
                            <section className="space-y-6">
                                <div>
                                    <h3 className="text-sm font-medium text-purple-400 uppercase tracking-wider mb-1">Alert Sensitivity</h3>
                                    <p className="text-xs text-slate-500">Configure when alerts are triggered.</p>
                                </div>

                                <div className="grid md:grid-cols-2 gap-6">
                                    {/* Delay Threshold */}
                                    <div className="space-y-2">
                                        <label className="text-sm font-medium text-slate-300">Grace Period (Minutes)</label>
                                        <p className="text-xs text-slate-500 mb-2">How late can a job be before alerting?</p>
                                        <input
                                            type="number"
                                            value={settings.alert_threshold_minutes}
                                            onChange={(e) => setSettings({ ...settings, alert_threshold_minutes: parseInt(e.target.value) || 0 })}
                                            className="w-full px-4 py-2 bg-slate-950 border border-slate-800 rounded-lg text-slate-200 focus:outline-none focus:ring-2 focus:ring-purple-500/50"
                                        />
                                    </div>

                                    {/* Stuck Threshold */}
                                    <div className="space-y-2">
                                        <label className="text-sm font-medium text-slate-300">Stuck Multiplier (x Avg)</label>
                                        <p className="text-xs text-slate-500 mb-2">Alert if runtime exceeds AVG x Multiplier</p>
                                        <input
                                            type="number"
                                            step="0.1"
                                            value={settings.stuck_threshold_multiplier}
                                            onChange={(e) => setSettings({ ...settings, stuck_threshold_multiplier: parseFloat(e.target.value) || 0 })}
                                            className="w-full px-4 py-2 bg-slate-950 border border-slate-800 rounded-lg text-slate-200 focus:outline-none focus:ring-2 focus:ring-purple-500/50"
                                        />
                                    </div>
                                </div>
                            </section>

                            <hr className="border-slate-800" />

                            {/* Toggles */}
                            <section className="space-y-4">
                                <div>
                                    <h3 className="text-sm font-medium text-emerald-400 uppercase tracking-wider mb-1">Detection Rules</h3>
                                </div>
                                <div className="space-y-3">
                                    <label className="flex items-center justify-between p-3 bg-slate-950/50 border border-slate-800 rounded-lg cursor-pointer hover:border-slate-700 transition-colors">
                                        <div>
                                            <span className="block text-sm font-medium text-slate-200">Late / Delayed Jobs</span>
                                            <span className="block text-xs text-slate-500">Alert when a cron schedule is missed.</span>
                                        </div>
                                        <input
                                            type="checkbox"
                                            checked={settings.alert_on_delayed}
                                            onChange={(e) => setSettings({ ...settings, alert_on_delayed: e.target.checked })}
                                            className="w-5 h-5 rounded border-slate-700 text-blue-600 focus:ring-blue-500/50 bg-slate-900"
                                        />
                                    </label>

                                    <label className="flex items-center justify-between p-3 bg-slate-950/50 border border-slate-800 rounded-lg cursor-pointer hover:border-slate-700 transition-colors">
                                        <div>
                                            <span className="block text-sm font-medium text-slate-200">Stuck / Long Running</span>
                                            <span className="block text-xs text-slate-500">Alert when runtime is significantly longer than average.</span>
                                        </div>
                                        <input
                                            type="checkbox"
                                            checked={settings.alert_on_stuck}
                                            onChange={(e) => setSettings({ ...settings, alert_on_stuck: e.target.checked })}
                                            className="w-5 h-5 rounded border-slate-700 text-blue-600 focus:ring-blue-500/50 bg-slate-900"
                                        />
                                    </label>

                                    <label className="flex items-center justify-between p-3 bg-slate-950/50 border border-slate-800 rounded-lg cursor-pointer hover:border-slate-700 transition-colors">
                                        <div>
                                            <span className="block text-sm font-medium text-slate-200">Anomaly Detection</span>
                                            <span className="block text-xs text-slate-500">Smart statistical outlier detection (experimental).</span>
                                        </div>
                                        <input
                                            type="checkbox"
                                            checked={settings.alert_on_anomaly}
                                            onChange={(e) => setSettings({ ...settings, alert_on_anomaly: e.target.checked })}
                                            className="w-5 h-5 rounded border-slate-700 text-blue-600 focus:ring-blue-500/50 bg-slate-900"
                                        />
                                    </label>
                                </div>
                            </section>
                        </>
                    )}
                </div>

                {/* Footer */}
                <div className="px-6 py-4 bg-slate-900/50 border-t border-slate-800 flex justify-end gap-3">
                    <button
                        onClick={onClose}
                        className="px-4 py-2 text-sm font-medium text-slate-400 hover:text-white transition-colors"
                    >
                        Cancel
                    </button>
                    <button
                        onClick={handleSave}
                        disabled={saving}
                        className="px-4 py-2 text-sm font-medium text-white bg-blue-600 hover:bg-blue-500 rounded-lg shadow-lg shadow-blue-500/20 disabled:opacity-50 disabled:cursor-not-allowed transition-all"
                    >
                        {saving ? 'Saving...' : 'Save Configuration'}
                    </button>
                </div>
            </div>
        </div>
    );
}
