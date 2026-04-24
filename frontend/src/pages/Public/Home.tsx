import { Link } from 'react-router-dom';
import { useMedalTally } from '../../hooks/usePublicData';
import { Trophy, ArrowRight, Activity } from 'lucide-react';

export default function Home() {
    return (
        <div className="space-y-16 py-8">
            {/* Hero Section */}
            <section className="flex flex-col items-center justify-center py-12 lg:py-24 text-center px-4 bg-gradient-to-b from-maroon/5 to-transparent rounded-3xl border border-maroon/10">
                <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-gold/20 text-yellow-800 text-sm font-semibold mb-6">
                    <Activity className="w-4 h-4"/> Live Intramurals 2026
                </div>
                <h1 className="text-5xl md:text-6xl font-black text-maroon tracking-tight mb-6 drop-shadow-sm">
                    Enverga Arena
                </h1>
                <p className="text-xl md:text-2xl max-w-3xl text-charcoal/80 mb-10 leading-relaxed">
                    The official tournament portal for the Manuel S. Enverga University Foundation intramurals.
                </p>
                <div className="flex flex-col sm:flex-row gap-4">
                    <Link to="/schedules" className="btn btn-lg bg-maroon hover:bg-maroon-dark text-white border-none shadow-lg">
                        View Schedules
                    </Link>
                    <Link to="/results" className="btn btn-lg btn-outline border-maroon text-maroon hover:bg-maroon hover:text-white bg-white">
                        Live Results & Tally
                    </Link>
                </div>
            </section>

            {/* Top 3 Leaderboard Widget */}
            <section className="max-w-4xl mx-auto">
                <div className="flex items-center justify-between mb-8 px-2">
                    <h2 className="text-3xl font-bold text-charcoal flex items-center gap-2">
                        <Trophy className="w-8 h-8 text-gold"/> Current Leaders
                    </h2>
                    <Link to="/results" className="text-maroon font-semibold hover:underline flex items-center gap-1">
                        Full Tally <ArrowRight className="w-4 h-4"/>
                    </Link>
                </div>
                
                <Top3Widget />
            </section>
        </div>
    );
}

function Top3Widget() {
    const { data: tally, isLoading } = useMedalTally();

    if (isLoading) {
        return <div className="text-center py-10"><span className="loading loading-spinner text-maroon"></span></div>;
    }

    if (!tally || tally.length === 0) {
        return (
            <div className="bg-base-200 rounded-2xl p-8 text-center text-gray-500">
                Waiting for the first results to be recorded.
            </div>
        );
    }

    const top3 = tally.slice(0, 3);

    return (
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            {top3.map((dept, index) => (
                <div 
                    key={dept.id} 
                    className={`card bg-base-100 shadow-xl border-t-4 ${
                        index === 0 ? 'border-yellow-400 scale-105 z-10' : 
                        index === 1 ? 'border-gray-300' : 
                        'border-amber-700'
                    }`}
                >
                    <div className="card-body items-center text-center p-8">
                        <div className="text-5xl font-black mb-2 opacity-20 absolute top-4 left-4">
                            #{index + 1}
                        </div>
                        <h3 className="card-title text-3xl font-black text-maroon mt-4">{dept.department_acronym}</h3>
                        <p className="text-sm text-gray-500 mb-4">{dept.department_name}</p>
                        
                        <div className="flex gap-4 justify-center mt-2">
                            <div className="text-center">
                                <div className="text-xl font-bold text-yellow-600">{dept.gold}</div>
                                <div className="text-xs font-bold uppercase">Gold</div>
                            </div>
                            <div className="text-center">
                                <div className="text-xl font-bold text-gray-500">{dept.silver}</div>
                                <div className="text-xs font-bold uppercase">Silver</div>
                            </div>
                            <div className="text-center">
                                <div className="text-xl font-bold text-amber-700">{dept.bronze}</div>
                                <div className="text-xs font-bold uppercase">Bronze</div>
                            </div>
                        </div>
                        
                        <div className="mt-6 pt-4 border-t w-full">
                            <div className="text-sm uppercase font-bold text-gray-400">Total Points</div>
                            <div className="text-3xl font-black text-charcoal">{dept.total_points}</div>
                        </div>
                    </div>
                </div>
            ))}
        </div>
    );
}
