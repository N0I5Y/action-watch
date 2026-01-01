
import type { Workflow } from '../../api/workflows';

interface WorkflowDetailsPanelProps {
    workflow: Workflow | undefined;
    onClose: () => void;
}

export function WorkflowDetailsPanel({ workflow, onClose }: WorkflowDetailsPanelProps) {
    if (!workflow) return null;
    return (
        <div className="fixed inset-y-0 right-0 w-96 bg-white shadow-xl p-6 transform transition-transform overflow-y-auto z-40 border-l">
            <div className="flex justify-between items-center mb-6">
                <h2 className="text-xl font-bold truncate">{workflow.name}</h2>
                <button onClick={onClose} className="text-gray-500 hover:text-gray-700">×</button>
            </div>
            <div className="space-y-4">
                <div>
                    <label className="block text-sm font-medium text-gray-500">Status</label>
                    <div className="mt-1">{workflow.status || 'Unknown'}</div>
                </div>
                <div>
                    <label className="block text-sm font-medium text-gray-500">Last Run</label>
                    <div className="mt-1">{workflow.last_run_at || 'Never'}</div>
                </div>
            </div>
        </div>
    );
}
