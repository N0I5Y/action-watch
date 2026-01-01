
import { useAuth } from '../contexts/AuthContext';

export function Login() {
    // eslint-disable-next-line @typescript-eslint/no-unused-vars
    const { login } = useAuth();
    return (
        <div className="flex flex-col items-center justify-center h-screen">
            <h1 className="text-3xl font-bold mb-8">CronWatch</h1>
            <button
                onClick={login}
                className="px-6 py-3 bg-black text-white rounded-lg hover:bg-gray-800 transition"
            >
                Sign in with GitHub
            </button>
        </div>
    );
}
