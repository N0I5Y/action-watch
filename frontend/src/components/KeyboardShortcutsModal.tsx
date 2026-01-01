

export function KeyboardShortcutsModal({ isOpen, onClose }: { isOpen: boolean; onClose: () => void }) {
    if (!isOpen) return null;
    return (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-50">
            <div className="bg-white p-6 rounded-lg w-full max-w-md">
                <h2 className="text-xl font-bold mb-4">Keyboard Shortcuts</h2>
                <p>Shortcuts list coming soon.</p>
                <button onClick={onClose} className="mt-4 px-4 py-2 border rounded">Close</button>
            </div>
        </div>
    );
}
