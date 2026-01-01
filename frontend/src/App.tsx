// src/App.tsx
import { useEffect, useMemo, useState } from "react";
import { fetchWorkflows, type Workflow } from "./api/workflows";
import { WorkflowDetailsPanel } from "./components/workflows/WorkflowDetailsPanel";
import { formatDateTime } from "./utils/datetime";
import { useAuth } from "./contexts/AuthContext";
import { Login } from "./components/Login";
import { BillingModal } from "./components/BillingModal";
import { SettingsModal } from "./components/SettingsModal";
import { Analytics } from "./components/Analytics";
import { Alerts } from "./components/Alerts";
import { KeyboardShortcutsModal } from "./components/KeyboardShortcutsModal";
import { useKeyboardShortcuts } from "./hooks/useKeyboardShortcuts";
import { useTimezone } from "./contexts/TimezoneContext";

type CronFilter = "all" | "scheduled" | "unscheduled";
type StatusFilter = "all" | "success" | "failure" | "running" | "pending";
type SortOption = "name" | "lastRun" | "status";

function App() {
  const { user, isLoading: authLoading, selectedInstallationId, installations, setSelectedInstallationId, logout } = useAuth();
  const { timezone } = useTimezone();

  const [workflows, setWorkflows] = useState<Workflow[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const [search, setSearch] = useState("");
  const [cronFilter, setCronFilter] = useState<CronFilter>("all");
  const [sortBy, setSortBy] = useState<SortOption>("lastRun");
  const [selectedWorkflowId, setSelectedWorkflowId] = useState<number | null>(
    null,
  );
  const [isDetailsOpen, setIsDetailsOpen] = useState(false);
  const [isBillingOpen, setIsBillingOpen] = useState(false);
  const [isSettingsOpen, setIsSettingsOpen] = useState(false);
  const [isShortcutsOpen, setIsShortcutsOpen] = useState(false);
  const [currentView, setCurrentView] = useState<"workflows" | "analytics" | "alerts">("workflows");

  useEffect(() => {
    if (!user || !selectedInstallationId) return;

    const load = async () => {
      try {
        setLoading(true);
        setError(null);
        // TODO: Pass selectedInstallationId to fetchWorkflows once API supports it
        const data = await fetchWorkflows(selectedInstallationId);
        setWorkflows(data);
      } catch (err: any) {
        console.error(err);
        setError(err?.message ?? "Failed to load workflows");
      } finally {
        setLoading(false);
      }
    };

    load();
  }, [user, selectedInstallationId]);

  // Keyboard shortcuts
  useKeyboardShortcuts([
    { key: 'k', ctrl: true, handler: () => document.querySelector<HTMLInputElement>('input[placeholder*="Search"]')?.focus(), description: 'Search workflows' },
    { key: 's', ctrl: true, handler: () => setIsSettingsOpen(true), description: 'Open settings' },
    { key: 'b', ctrl: true, handler: () => setIsBillingOpen(true), description: 'Open billing' },
    { key: '1', ctrl: true, handler: () => setCurrentView('workflows'), description: 'Go to Workflows' },
    { key: '2', ctrl: true, handler: () => setCurrentView('analytics'), description: 'Go to Analytics' },
    { key: '3', ctrl: true, handler: () => setCurrentView('alerts'), description: 'Go to Alerts' },
    { key: '?', handler: () => setIsShortcutsOpen(true), description: 'Show keyboard shortcuts' },
  ]);

  const filteredWorkflows = useMemo(() => {
    let filtered = workflows.filter((wf) => {
      if (
        search &&
        !`${wf.name} ${wf.repo_full_name}`
          .toLowerCase()
          .includes(search.toLowerCase())
      ) {
        return false;
      }

      if (cronFilter === "scheduled" && !wf.cron_expression) return false;
      if (cronFilter === "unscheduled" && wf.cron_expression) return false;

      return true;
    });

    // Sort
    filtered.sort((a, b) => {
      if (sortBy === "name") {
        return a.name.localeCompare(b.name);
      } else if (sortBy === "lastRun") {
        const aTime = a.last_run_at ? new Date(a.last_run_at).getTime() : 0;
        const bTime = b.last_run_at ? new Date(b.last_run_at).getTime() : 0;
        return bTime - aTime; // Most recent first
      }
      return 0;
    });

    return filtered;
  }, [workflows, search, cronFilter, sortBy]);

  const total = workflows.length;
  const scheduled = workflows.filter((w) => !!w.cron_expression).length;



  const handleRowClick = (wf: Workflow) => {
    setSelectedWorkflowId(wf.id);
    setIsDetailsOpen(true);
  };

  const handleCloseDetails = () => {
    setIsDetailsOpen(false);
    setSelectedWorkflowId(null);
  };

  if (authLoading) {
    return <div className="min-h-screen bg-slate-950 text-slate-100 flex items-center justify-center">Loading...</div>;
  }

  if (!user) {
    return <Login />;
  }

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 flex">
      {/* Sidebar */}
      <aside className="hidden md:flex w-64 flex-col border-r border-slate-800 bg-slate-950/60 backdrop-blur">
        <div className="px-6 py-4 border-b border-slate-800">
          <div className="flex items-center gap-2 mb-4">
            <div className="h-8 w-8 rounded-2xl bg-indigo-500/20 flex items-center justify-center">
              <span className="text-indigo-400 text-sm font-semibold">AW</span>
            </div>
            <div>
              <div className="text-sm font-semibold">ActionWatch</div>
              <div className="text-[11px] text-slate-400">
                GitHub Actions Monitor
              </div>
            </div>
          </div>

          {/* Org Switcher */}
          <div className="relative">
            <select
              value={selectedInstallationId || ""}
              onChange={(e) => setSelectedInstallationId(Number(e.target.value))}
              className="w-full bg-slate-900 border border-slate-700 text-slate-300 text-xs rounded-lg px-2.5 py-2 outline-none focus:border-indigo-500 appearance-none"
            >
              {installations.map(inst => (
                <option key={inst.id} value={inst.id}>
                  {inst.account_login}
                </option>
              ))}
              {installations.length === 0 && <option disabled>No installations found</option>}
            </select>
            <div className="absolute right-2 top-2.5 pointer-events-none text-slate-500 text-[10px]">▼</div>
          </div>
        </div>

        <nav className="flex-1 px-3 py-4 space-y-1 text-sm">
          <div className="px-2 text-[11px] uppercase tracking-wide text-slate-500 mb-2">
            Main
          </div>
          <button
            onClick={() => setCurrentView("workflows")}
            className={`w-full flex items-center gap-2 px-3 py-2 rounded-xl text-xs font-medium ${currentView === "workflows"
              ? "bg-slate-800 text-slate-50"
              : "text-slate-400 hover:bg-slate-900/70"
              }`}
          >
            <span className="h-6 w-6 rounded-lg bg-indigo-500/20 flex items-center justify-center text-[13px]">
              🕒
            </span>
            <span>Workflows</span>
          </button>
          <button
            onClick={() => setCurrentView("analytics")}
            className={`w-full flex items-center gap-2 px-3 py-2 rounded-xl text-xs font-medium ${currentView === "analytics"
              ? "bg-slate-800 text-slate-50"
              : "text-slate-400 hover:bg-slate-900/70"
              }`}
          >
            <span className="h-6 w-6 rounded-lg bg-slate-800 flex items-center justify-center text-[13px]">
              📊
            </span>
            <span>Analytics</span>
          </button>
          <button
            onClick={() => setCurrentView("alerts")}
            className={`w-full flex items-center gap-2 px-3 py-2 rounded-xl text-xs font-medium ${currentView === "alerts"
              ? "bg-slate-800 text-slate-50"
              : "text-slate-400 hover:bg-slate-900/70"
              }`}
          >
            <span className="h-6 w-6 rounded-lg bg-slate-800 flex items-center justify-center text-[13px]">
              🔔
            </span>
            <span>Alerts</span>
          </button>

          <div className="px-2 pt-4 text-[11px] uppercase tracking-wide text-slate-500 mb-2">
            Filters
          </div>
          <div className="space-y-2 px-1">
            <button
              onClick={() => setCronFilter("all")}
              className={`w-full flex items-center justify-between px-3 py-2 rounded-xl text-xs ${cronFilter === "all"
                ? "bg-slate-800 text-slate-50"
                : "bg-slate-900/40 text-slate-400 hover:bg-slate-900/80"
                }`}
            >
              <span>All workflows</span>
              <span className="text-[11px] text-slate-400">{total}</span>
            </button>
            <button
              onClick={() => setCronFilter("scheduled")}
              className={`w-full flex items-center justify-between px-3 py-2 rounded-xl text-xs ${cronFilter === "scheduled"
                ? "bg-slate-800 text-slate-50"
                : "bg-slate-900/40 text-slate-400 hover:bg-slate-900/80"
                }`}
            >
              <span>Scheduled (cron)</span>
              <span className="text-[11px] text-emerald-400">{scheduled}</span>
            </button>
            <button
              onClick={() => setCronFilter("unscheduled")}
              className={`w-full flex items-center justify-between px-3 py-2 rounded-xl text-xs ${cronFilter === "unscheduled"
                ? "bg-slate-800 text-slate-50"
                : "bg-slate-900/40 text-slate-400 hover:bg-slate-900/80"
                }`}
            >
              <span>Without schedule</span>
              <span className="text-[11px] text-slate-400">
                {total - scheduled}
              </span>
            </button>
          </div>
        </nav>

        <div className="px-4 py-3 border-t border-slate-800 text-[11px] text-slate-500">
          <div className="flex items-center justify-between">
            <span>Slack alerts</span>
            <span className="inline-flex items-center gap-1 text-emerald-400 text-[10px]">
              ● Active
            </span>
          </div>
        </div>
      </aside>

      {/* Main */}
      <div className="flex-1 flex flex-col">
        {/* Top bar */}
        <header className="h-14 border-b border-slate-800 flex items-center px-4 md:px-6 bg-slate-950/70 backdrop-blur">
          <div className="flex-1 flex items-center gap-2 md:gap-4">
            <div className="md:hidden mr-2 text-slate-400 text-xl">☰</div>
            <div className="text-sm md:text-base font-semibold">
              GitHub Actions Monitor
            </div>

            <div className="hidden md:flex items-center ml-4 px-3 py-1.5 rounded-full bg-slate-900 border border-slate-800 text-xs text-slate-400 gap-2">
              <span className="text-[13px]">🔍</span>
              <input
                value={search}
                onChange={(e) => setSearch(e.target.value)}
                placeholder="Search workflows or repos…"
                className="bg-transparent outline-none text-xs placeholder:text-slate-500 w-48"
              />
              {search && (
                <button
                  onClick={() => setSearch("")}
                  className="text-[11px] text-slate-500 hover:text-slate-300"
                >
                  ✕
                </button>
              )}
            </div>
          </div>

          <div className="flex items-center gap-2 text-xs">
            <button
              onClick={() => setIsSettingsOpen(true)}
              className="hidden md:inline-flex items-center gap-1 px-3 py-1.5 rounded-full border border-slate-700 bg-slate-900/70 text-slate-200 hover:bg-slate-900"
            >
              <span>⚙</span>
              <span>Settings</span>
            </button>
            <button
              onClick={() => setIsBillingOpen(true)}
              className="hidden md:inline-flex items-center gap-1 px-3 py-1.5 rounded-full border border-slate-700 bg-slate-900/70 text-slate-200 hover:bg-slate-900"
            >
              <span>⚙</span>
              <span>Billing</span>
            </button>

            <button
              onClick={logout}
              className="hidden md:inline-flex items-center gap-1 px-3 py-1.5 rounded-full border border-slate-700 bg-slate-900/70 text-slate-200 hover:bg-slate-900"
              title="Logout"
            >
              <span>🚪</span>
              <span>Logout</span>
            </button>

            <div className="h-7 w-7 rounded-full bg-gradient-to-tr from-indigo-500 to-sky-400 text-[11px] flex items-center justify-center overflow-hidden">
              {user.avatar_url ? <img src={user.avatar_url} alt={user.login} /> : "AW"}
            </div>
          </div>
        </header>

        {/* Content */}
        {currentView === "analytics" ? (
          <Analytics installationId={selectedInstallationId!} />
        ) : currentView === "alerts" ? (
          <Alerts installationId={selectedInstallationId!} />
        ) : (
          <main className="flex-1 px-4 md:px-6 py-4 md:py-6 space-y-4 md:space-y-6">
            {/* Top metrics */}
            <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 md:gap-4">
              <div className="rounded-2xl border border-slate-800 bg-slate-900/60 p-3.5">
                <div className="flex items-center justify-between mb-2">
                  <span className="text-[11px] uppercase tracking-wide text-slate-500">
                    Total workflows
                  </span>
                  <span className="text-[10px] text-slate-500">All repos</span>
                </div>
                <div className="text-2xl font-semibold">{total}</div>
              </div>

              <div className="rounded-2xl border border-slate-800 bg-slate-900/60 p-3.5">
                <div className="flex items-center justify-between mb-2">
                  <span className="text-[11px] uppercase tracking-wide text-slate-500">
                    Scheduled (cron)
                  </span>
                  <span className="text-[10px] text-emerald-400">Monitoring</span>
                </div>
                <div className="text-2xl font-semibold">{scheduled}</div>
              </div>

              <div className="rounded-2xl border border-slate-800 bg-slate-900/60 p-3.5">
                <div className="flex items-center justify-between mb-2">
                  <span className="text-[11px] uppercase tracking-wide text-slate-500">
                    Unscheduled
                  </span>
                  <span className="text-[10px] text-slate-500">Need cron?</span>
                </div>
                <div className="text-2xl font-semibold">
                  {total - scheduled}
                </div>
              </div>
            </div>

            {/* Main table + side panel */}
            <div className="grid grid-cols-1 lg:grid-cols-[minmax(0,2fr)_minmax(260px,1fr)] gap-4 md:gap-6">
              {/* Workflows table */}
              <section className="rounded-2xl border border-slate-800 bg-slate-900/60 overflow-hidden">
                <div className="px-4 py-3 border-b border-slate-800 flex items-center justify-between">
                  <div>
                    <h2 className="text-sm font-medium">Scheduled workflows</h2>
                    <p className="text-[11px] text-slate-500">
                      Monitoring GitHub Actions cron jobs across your repos.
                    </p>
                  </div>
                </div>

                <div className="overflow-x-auto">
                  <table className="min-w-full text-sm">
                    <thead className="bg-slate-900/80 border-b border-slate-800 text-xs text-slate-400">
                      <tr>
                        <th className="text-left px-4 py-2.5 font-normal">
                          Workflow
                        </th>
                        <th className="text-left px-4 py-2.5 font-normal">
                          Repository
                        </th>
                        <th className="text-left px-4 py-2.5 font-normal">
                          Cron
                        </th>
                        <th className="text-left px-4 py-2.5 font-normal">
                          Last run
                        </th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-slate-800/80">
                      {loading && (
                        <tr>
                          <td
                            colSpan={4}
                            className="px-4 py-6 text-center text-xs text-slate-500"
                          >
                            Loading workflows…
                          </td>
                        </tr>
                      )}

                      {error && !loading && (
                        <tr>
                          <td
                            colSpan={4}
                            className="px-4 py-6 text-center text-xs text-red-400"
                          >
                            {error}
                          </td>
                        </tr>
                      )}

                      {!loading && !error && filteredWorkflows.length === 0 && (
                        <tr>
                          <td
                            colSpan={4}
                            className="px-4 py-6 text-center text-xs text-slate-500"
                          >
                            No workflows match your filters.
                          </td>
                        </tr>
                      )}

                      {!loading &&
                        !error &&
                        filteredWorkflows.map((wf) => (
                          <tr
                            key={wf.id}
                            className="hover:bg-slate-900/80 transition-colors cursor-pointer"
                            onClick={() => handleRowClick(wf)}
                          >
                            <td className="px-4 py-3 align-middle">
                              <div className="flex flex-col">
                                <span className="text-xs font-medium text-slate-50">
                                  {wf.name}
                                </span>
                                <span className="text-[11px] text-slate-500">
                                  ID: {wf.id}
                                </span>
                              </div>
                            </td>
                            <td className="px-4 py-3 align-middle text-xs text-slate-300">
                              {wf.repo_full_name}
                            </td>
                            <td className="px-4 py-3 align-middle text-xs">
                              {wf.cron_expression ? (
                                <span className="inline-flex items-center px-2 py-0.5 rounded-full bg-slate-800 text-[11px] text-emerald-300 border border-emerald-500/30">
                                  {wf.cron_expression}
                                </span>
                              ) : (
                                <span className="inline-flex items-center px-2 py-0.5 rounded-full bg-slate-900 text-[11px] text-slate-400 border border-slate-700">
                                  none
                                </span>
                              )}
                            </td>
                            <td className="px-4 py-3 align-middle text-[11px] text-slate-300">
                              {formatDateTime(wf.last_run_at, timezone)}
                            </td>
                          </tr>
                        ))}
                    </tbody>
                  </table>
                </div>
              </section>

              {/* Right alerts + workflow details */}
              {isDetailsOpen && selectedWorkflowId && (
                <WorkflowDetailsPanel
                  workflowId={selectedWorkflowId}
                  onClose={handleCloseDetails}
                />
              )}
            </div>
          </main>
        )}
      </div>
      {isSettingsOpen && selectedInstallationId && (
        <SettingsModal
          installationId={selectedInstallationId}
          onClose={() => setIsSettingsOpen(false)}
        />
      )}
      {isBillingOpen && selectedInstallationId && (
        <BillingModal
          installationId={selectedInstallationId}
          onClose={() => setIsBillingOpen(false)}
        />
      )}
      {isShortcutsOpen && (
        <KeyboardShortcutsModal onClose={() => setIsShortcutsOpen(false)} />
      )}
    </div>
  );
}

export default App;
