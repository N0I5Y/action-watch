import { useState, useEffect } from 'react';
import {
    AreaChart,
    Area,
    XAxis,
    YAxis,
    CartesianGrid,
    Tooltip,
    ResponsiveContainer,
    BarChart,
    Bar,
    Legend
} from 'recharts';

interface AnalyticsProps {
    installationId: number;
}

interface SuccessRateData {
    date: string;
    success: number;
    failure: number;
    total: number;
}

interface RuntimeTrendData {
    date: string;
    avg_duration_seconds: number;
    run_count: number;
}

interface DurationStats {
    min_duration_ms: number | null;
    max_duration_ms: number | null;
    avg_duration_ms: number | null;
    p50_duration_ms: number | null;
    p95_duration_ms: number | null;
    total_runs: number;
}

const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000/api';

export function Analytics({ installationId }: AnalyticsProps) {
    const [days, setDays] = useState(30);
    const [loading, setLoading] = useState(true);
    const [successData, setSuccessData] = useState<SuccessRateData[]>([]);
    const [trendData, setTrendData] = useState<RuntimeTrendData[]>([]);
    const [stats, setStats] = useState<DurationStats | null>(null);

    useEffect(() => {
        if (installationId) {
            fetchData();
        }
        // eslint-disable-next-line react-hooks/exhaustive-deps
    }, [installationId, days]);

    const fetchData = async () => {
        setLoading(true);
        try {
            const [successRes, trendRes, statsRes] = await Promise.all([
                fetch(`${API_BASE}/analytics/success-rate?installation_id=${installationId}&days=${days}`, { credentials: 'include' }),
                fetch(`${API_BASE}/analytics/runtime-trends?installation_id=${installationId}&days=${days}`, { credentials: 'include' }),
                fetch(`${API_BASE}/analytics/duration-stats?installation_id=${installationId}&days=${days}`, { credentials: 'include' })
            ]);

            if (successRes.ok) setSuccessData(await successRes.json());
            if (trendRes.ok) setTrendData(await trendRes.json());
            if (statsRes.ok) setStats(await statsRes.json());

        } catch (error) {
            console.error("Failed to fetch analytics", error);
        } finally {
            setLoading(false);
        }
    };

    const formatDuration = (ms: number | null) => {
        if (!ms) return '-';
        if (ms < 1000) return `${Math.round(ms)}ms`;
        return `${(ms / 1000).toFixed(1)}s`;
    };

    if (loading) {
        return (
            <div className="flex items-center justify-center h-96">
                <div className="w-8 h-8 border-4 border-blue-500 border-t-transparent rounded-full animate-spin" />
            </div>
        );
    }

    return (
        <div className="p-8 space-y-8 max-w-7xl mx-auto">
            {/* Header */}
            <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
                <div>
                    <h2 className="text-2xl font-bold text-white">Analytics Dashboard</h2>
                    <p className="text-slate-400">Insights into your GitHub Actions performance.</p>
                </div>
                <select
                    value={days}
                    onChange={(e) => setDays(Number(e.target.value))}
                    className="bg-slate-900 border border-slate-700 text-slate-200 text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 block p-2.5"
                >
                    <option value={7}>Last 7 Days</option>
                    <option value={30}>Last 30 Days</option>
                    <option value={90}>Last 90 Days</option>
                </select>
            </div>

            {/* Stats Grid */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
                <div className="bg-slate-900/50 border border-slate-800 p-6 rounded-xl backdrop-blur-sm">
                    <h3 className="text-sm font-medium text-slate-400 uppercase tracking-wider mb-2">Total Runs</h3>
                    <div className="text-3xl font-bold text-white">{stats?.total_runs || 0}</div>
                </div>
                <div className="bg-slate-900/50 border border-slate-800 p-6 rounded-xl backdrop-blur-sm">
                    <h3 className="text-sm font-medium text-slate-400 uppercase tracking-wider mb-2">Avg Duration</h3>
                    <div className="text-3xl font-bold text-blue-400">{formatDuration(stats?.avg_duration_ms || 0)}</div>
                </div>
                <div className="bg-slate-900/50 border border-slate-800 p-6 rounded-xl backdrop-blur-sm">
                    <h3 className="text-sm font-medium text-slate-400 uppercase tracking-wider mb-2">P50 Duration</h3>
                    <div className="text-3xl font-bold text-emerald-400">{formatDuration(stats?.p50_duration_ms || 0)}</div>
                </div>
                <div className="bg-slate-900/50 border border-slate-800 p-6 rounded-xl backdrop-blur-sm">
                    <h3 className="text-sm font-medium text-slate-400 uppercase tracking-wider mb-2">P95 Duration</h3>
                    <div className="text-3xl font-bold text-purple-400">{formatDuration(stats?.p95_duration_ms || 0)}</div>
                </div>
            </div>

            {/* Charts Grid */}
            <div className="grid lg:grid-cols-2 gap-8">
                {/* Success/Failure Rate */}
                <div className="bg-slate-900/50 border border-slate-800 p-6 rounded-xl backdrop-blur-sm h-[400px]">
                    <h3 className="text-lg font-semibold text-white mb-6">Execution Status</h3>
                    <ResponsiveContainer width="100%" height="100%">
                        <BarChart data={successData}>
                            <CartesianGrid strokeDasharray="3 3" stroke="#334155" vertical={false} />
                            <XAxis
                                dataKey="date"
                                stroke="#94a3b8"
                                tickFormatter={(str) => new Date(str).toLocaleDateString(undefined, { month: 'short', day: 'numeric' })}
                                tick={{ fontSize: 12 }}
                            />
                            <YAxis stroke="#94a3b8" tick={{ fontSize: 12 }} />
                            <Tooltip
                                contentStyle={{ backgroundColor: '#0f172a', borderColor: '#1e293b', color: '#f8fafc' }}
                                cursor={{ fill: '#1e293b' }}
                            />
                            <Legend />
                            <Bar dataKey="success" stackId="a" fill="#10b981" name="Success" radius={[0, 0, 4, 4]} />
                            <Bar dataKey="failure" stackId="a" fill="#ef4444" name="Failure" radius={[4, 4, 0, 0]} />
                        </BarChart>
                    </ResponsiveContainer>
                </div>

                {/* Runtime Trends */}
                <div className="bg-slate-900/50 border border-slate-800 p-6 rounded-xl backdrop-blur-sm h-[400px]">
                    <h3 className="text-lg font-semibold text-white mb-6">Avg Runtime (Seconds)</h3>
                    <ResponsiveContainer width="100%" height="100%">
                        <AreaChart data={trendData}>
                            <CartesianGrid strokeDasharray="3 3" stroke="#334155" vertical={false} />
                            <XAxis
                                dataKey="date"
                                stroke="#94a3b8"
                                tickFormatter={(str) => new Date(str).toLocaleDateString(undefined, { month: 'short', day: 'numeric' })}
                                tick={{ fontSize: 12 }}
                            />
                            <YAxis stroke="#94a3b8" tick={{ fontSize: 12 }} />
                            <Tooltip
                                contentStyle={{ backgroundColor: '#0f172a', borderColor: '#1e293b', color: '#f8fafc' }}
                            />
                            <Area
                                type="monotone"
                                dataKey="avg_duration_seconds"
                                stroke="#3b82f6"
                                fill="#3b82f6"
                                fillOpacity={0.1}
                                name="Avg Duration (s)"
                            />
                        </AreaChart>
                    </ResponsiveContainer>
                </div>
            </div>
        </div>
    );
}
