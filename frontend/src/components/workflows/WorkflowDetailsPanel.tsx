import type { Workflow } from '../../api/workflows';

interface WorkflowDetailsPanelProps {
    workflow: Workflow | undefined;
    onClose: () => void;
}

export function WorkflowDetailsPanel({ workflow, onClose }: WorkflowDetailsPanelProps) {
    if (!workflow) return null;

    const githubUrl = `https://github.com/${workflow.repo_full_name}/blob/main/${workflow.path}`;

    return (
        <div className="fixed inset-y-0 right-0 w-[480px] bg-slate-950/95 backdrop-blur-xl shadow-2xl p-0 transform transition-transform overflow-y-auto z-40 border-l border-slate-800 flex flex-col">
            {/* Header */}
            <div className="flex justify-between items-start p-6 border-b border-slate-800 bg-slate-900/50">
                <div>
                    <h2 className="text-xl font-bold text-white leading-tight mb-1">{workflow.name}</h2>
                    <p className="text-sm text-blue-400 font-medium">{workflow.repo_full_name}</p>
                </div>
                <button
                    onClick={onClose}
                    className="p-2 -mr-2 text-slate-400 hover:text-white bg-transparent hover:bg-slate-800 rounded-lg transition-colors"
                >
                    <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                    </svg>
                </button>
            </div>

            {/* Content */}
            <div className="p-6 space-y-8">

                {/* Status Section */}
                <div className="flex items-center gap-4 p-4 bg-slate-900 border border-slate-800 rounded-xl">
                    <div className={`w-3 h-3 rounded-full shadow-lg ${workflow.state === 'active' ? 'bg-emerald-500 shadow-emerald-500/50' : 'bg-slate-500'}`} />
                    <div>
                        <div className="text-xs font-medium text-slate-500 uppercase tracking-wider">Current State</div>
                        <div className="text-sm font-semibold text-slate-200 capitalize">{workflow.state || 'Unknown'}</div>
                    </div>
                </div>

                {/* Details Grid */}
                <div className="grid gap-6">
                    <div>
                        <label className="text-xs font-medium text-slate-500 uppercase tracking-wider block mb-2">Cron Schedule</label>
                        <div className="flex items-center gap-2">
                            <span className="px-3 py-1.5 bg-slate-900 border border-slate-700 rounded-lg text-sm font-mono text-purple-300">
                                {workflow.cron_expression || 'No Schedule'}
                            </span>
                        </div>
                    </div>

                    <div>
                        <label className="text-xs font-medium text-slate-500 uppercase tracking-wider block mb-2">Workflow File</label>
                        <a
                            href={githubUrl}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="group flex items-center gap-2 p-3 bg-slate-900/50 border border-slate-800 rounded-lg hover:border-blue-500/50 transition-colors"
                        >
                            <svg className="w-5 h-5 text-slate-500 group-hover:text-blue-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                            </svg>
                            <span className="text-sm text-slate-300 font-mono truncate flex-1">{workflow.path}</span>
                            <svg className="w-4 h-4 text-slate-600 group-hover:text-slate-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
                            </svg>
                        </a>
                    </div>

                    <div>
                        <label className="text-xs font-medium text-slate-500 uppercase tracking-wider block mb-2">Last Run Info</label>
                        <div className="p-4 bg-slate-900/50 rounded-xl border border-slate-800">
                            <div className="flex justify-between items-center mb-1">
                                <span className="text-sm text-slate-400">Timestamp</span>
                                <span className="text-sm text-slate-200">{workflow.last_run_at ? new Date(workflow.last_run_at).toLocaleString() : 'Never'}</span>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
}
