import { useAuth } from '../../context/AuthContext';

export default function Dashboard() {
    const { user } = useAuth();

    return (
        <div className="py-8">
            <h1 className="text-3xl font-bold text-charcoal mb-2">Admin Dashboard</h1>
            <p className="text-gray-500 mb-8">Welcome back, <span className="font-semibold text-maroon">{user?.username}</span>!</p>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                <div className="card bg-base-100 shadow-md border border-base-300">
                    <div className="card-body">
                        <h2 className="card-title">Manage Schedules</h2>
                        <p className="text-sm text-gray-500">Add or edit event schedules and venues.</p>
                    </div>
                </div>
                <div className="card bg-base-100 shadow-md border border-base-300">
                    <div className="card-body">
                        <h2 className="card-title">Post Results</h2>
                        <p className="text-sm text-gray-500">Record match and podium results.</p>
                    </div>
                </div>
                {user?.role === 'admin' && (
                    <div className="card bg-base-100 shadow-md border border-base-300">
                        <div className="card-body">
                            <h2 className="card-title">Medal Ledger</h2>
                            <p className="text-sm text-gray-500">Verify and resolve medal conflicts.</p>
                        </div>
                    </div>
                )}
            </div>
        </div>
    );
}
