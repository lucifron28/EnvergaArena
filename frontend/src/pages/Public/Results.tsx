import { useState } from 'react';
import { useMedalTally, useMatchResults, usePodiumResults } from '../../hooks/usePublicData';
import { Trophy, Medal, Swords, Hash } from 'lucide-react';
import { format, parseISO } from 'date-fns';

export default function Results() {
    const [activeTab, setActiveTab] = useState<'tally' | 'recent'>('tally');

    return (
        <div className="py-8">
            <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center mb-8 gap-4">
                <h1 className="text-3xl font-bold text-maroon flex items-center gap-2">
                    <Trophy className="w-8 h-8 text-gold"/> Official Results
                </h1>
                
                <div className="tabs tabs-boxed bg-base-200">
                    <a 
                        className={`tab ${activeTab === 'tally' ? 'tab-active bg-maroon text-white' : ''}`}
                        onClick={() => setActiveTab('tally')}
                    >
                        Medal Tally
                    </a>
                    <a 
                        className={`tab ${activeTab === 'recent' ? 'tab-active bg-maroon text-white' : ''}`}
                        onClick={() => setActiveTab('recent')}
                    >
                        Recent Matches
                    </a>
                </div>
            </div>

            {activeTab === 'tally' ? <MedalTallyTab /> : <RecentResultsTab />}
        </div>
    );
}

function MedalTallyTab() {
    const { data: tally, isLoading, isError } = useMedalTally();

    if (isLoading) return <LoadingSpinner />;
    if (isError) return <ErrorMessage text="Failed to load medal tally." />;

    return (
        <div className="overflow-x-auto bg-base-100 rounded-xl shadow-lg border border-base-200">
            <table className="table table-zebra w-full text-center">
                <thead className="bg-maroon text-white text-sm">
                    <tr>
                        <th className="w-16">Rank</th>
                        <th className="text-left">Department</th>
                        <th className="text-yellow-400"><Medal className="w-5 h-5 mx-auto"/> Gold</th>
                        <th className="text-gray-300"><Medal className="w-5 h-5 mx-auto"/> Silver</th>
                        <th className="text-amber-600"><Medal className="w-5 h-5 mx-auto"/> Bronze</th>
                        <th className="text-gold font-bold">Total Points</th>
                    </tr>
                </thead>
                <tbody>
                    {tally?.map((row, idx) => (
                        <tr key={row.id} className="hover">
                            <td className="font-bold text-lg">{idx + 1}</td>
                            <td className="text-left font-semibold flex items-center gap-2">
                                {row.department_color && (
                                    <span 
                                        className="w-3 h-3 rounded-full" 
                                        style={{ backgroundColor: row.department_color }}
                                    ></span>
                                )}
                                {row.department_acronym}
                                <span className="text-xs font-normal text-gray-500 hidden sm:inline">
                                    - {row.department_name}
                                </span>
                            </td>
                            <td className="font-bold text-yellow-600">{row.gold}</td>
                            <td className="font-bold text-gray-500">{row.silver}</td>
                            <td className="font-bold text-amber-700">{row.bronze}</td>
                            <td className="font-bold text-maroon text-lg">{row.total_points}</td>
                        </tr>
                    ))}
                    {(!tally || tally.length === 0) && (
                        <tr>
                            <td colSpan={6} className="text-center py-10 text-gray-500">
                                No medal records found.
                            </td>
                        </tr>
                    )}
                </tbody>
            </table>
        </div>
    );
}

function RecentResultsTab() {
    const { data: matches, isLoading: matchesLoading } = useMatchResults();
    const { data: podiums, isLoading: podiumsLoading } = usePodiumResults();

    const isLoading = matchesLoading || podiumsLoading;

    if (isLoading) return <LoadingSpinner />;

    return (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
            {/* Match Results */}
            <div>
                <h2 className="text-xl font-bold text-charcoal mb-4 flex items-center gap-2">
                    <Swords className="w-5 h-5 text-maroon"/> Match Results
                </h2>
                <div className="space-y-4">
                    {matches?.map(match => (
                        <div key={`match-${match.id}`} className="card bg-base-100 shadow-sm border border-base-200">
                            <div className="card-body p-4">
                                <div className="flex justify-between items-center mb-2">
                                    <span className="text-xs font-bold text-maroon uppercase tracking-wider">{match.event_name}</span>
                                    {match.is_final && <span className="badge badge-error badge-sm text-white">Final</span>}
                                </div>
                                <div className="flex justify-between items-center text-lg font-bold">
                                    <div className={`w-1/3 text-center ${match.winner === match.home_department ? 'text-green-600' : ''}`}>
                                        {match.home_department_name}
                                    </div>
                                    <div className="w-1/3 text-center text-2xl tracking-widest bg-base-200 py-1 rounded">
                                        {match.home_score} - {match.away_score}
                                    </div>
                                    <div className={`w-1/3 text-center ${match.winner === match.away_department ? 'text-green-600' : ''}`}>
                                        {match.away_department_name}
                                    </div>
                                </div>
                                <div className="text-xs text-center text-gray-400 mt-2">
                                    {format(parseISO(match.recorded_at), 'MMM d, h:mm a')}
                                </div>
                            </div>
                        </div>
                    ))}
                    {(!matches || matches.length === 0) && <p className="text-gray-500 italic">No matches recorded yet.</p>}
                </div>
            </div>

            {/* Podium Results */}
            <div>
                <h2 className="text-xl font-bold text-charcoal mb-4 flex items-center gap-2">
                    <Hash className="w-5 h-5 text-maroon"/> Ranked Results
                </h2>
                <div className="space-y-4">
                    {podiums?.map(podium => (
                        <div key={`podium-${podium.id}`} className="card bg-base-100 shadow-sm border border-base-200">
                            <div className="card-body p-4 flex flex-row items-center justify-between">
                                <div>
                                    <div className="text-xs font-bold text-maroon uppercase tracking-wider mb-1">{podium.event_name}</div>
                                    <div className="font-bold text-lg">{podium.department_name}</div>
                                </div>
                                <div className="text-right">
                                    <div className="text-2xl font-black text-charcoal">Rank {podium.rank}</div>
                                    {podium.medal !== 'none' && (
                                        <div className="badge badge-warning text-xs uppercase">{podium.medal}</div>
                                    )}
                                </div>
                            </div>
                        </div>
                    ))}
                    {(!podiums || podiums.length === 0) && <p className="text-gray-500 italic">No rankings recorded yet.</p>}
                </div>
            </div>
        </div>
    );
}

function LoadingSpinner() {
    return (
        <div className="flex justify-center py-20">
            <span className="loading loading-spinner loading-lg text-maroon"></span>
        </div>
    );
}

function ErrorMessage({ text }: { text: string }) {
    return (
        <div className="alert alert-error max-w-2xl mx-auto mt-8">
            <span>{text}</span>
        </div>
    );
}
