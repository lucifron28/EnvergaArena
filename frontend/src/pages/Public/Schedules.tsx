import { useSchedules } from '../../hooks/usePublicData';
import { format, parseISO } from 'date-fns';
import { Calendar, MapPin, Users } from 'lucide-react';

export default function Schedules() {
    const { data: schedules, isLoading, isError } = useSchedules();

    if (isLoading) {
        return (
            <div className="flex justify-center py-20">
                <span className="loading loading-spinner loading-lg text-maroon"></span>
            </div>
        );
    }

    if (isError) {
        return (
            <div className="alert alert-error max-w-2xl mx-auto mt-8">
                <span>Failed to load schedules. Please try again later.</span>
            </div>
        );
    }

    return (
        <div className="py-8">
            <h1 className="text-3xl font-bold text-maroon mb-6 flex items-center gap-2">
                <Calendar className="w-8 h-8"/> Event Schedules
            </h1>
            
            {!schedules || schedules.length === 0 ? (
                <div className="card bg-base-100 shadow-sm border border-base-200">
                    <div className="card-body text-center py-12">
                        <p className="text-charcoal/60">No upcoming schedules found.</p>
                    </div>
                </div>
            ) : (
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                    {schedules.map((schedule) => (
                        <div key={schedule.id} className="card bg-base-100 shadow-md border border-base-200 hover:shadow-lg transition">
                            <div className="card-body p-6">
                                <h2 className="card-title text-xl text-maroon">{schedule.event_name}</h2>
                                
                                <div className="space-y-3 mt-4 text-sm text-charcoal/80">
                                    <div className="flex items-start gap-2">
                                        <Calendar className="w-4 h-4 mt-0.5 shrink-0 text-gold" />
                                        <span>
                                            {schedule.scheduled_start 
                                                ? format(parseISO(schedule.scheduled_start), 'MMM d, yyyy h:mm a') 
                                                : 'TBA'}
                                            {schedule.scheduled_end && ` - ${format(parseISO(schedule.scheduled_end), 'h:mm a')}`}
                                        </span>
                                    </div>
                                    
                                    <div className="flex items-start gap-2">
                                        <MapPin className="w-4 h-4 mt-0.5 shrink-0 text-gold" />
                                        <span>
                                            {schedule.venue_name || 'Venue TBA'}
                                            {schedule.venue_area_name && ` (${schedule.venue_area_name})`}
                                        </span>
                                    </div>
                                    
                                    <div className="flex items-start gap-2">
                                        <Users className="w-4 h-4 mt-0.5 shrink-0 text-gold" />
                                        <div className="flex flex-wrap gap-1">
                                            {schedule.participants.length > 0 ? (
                                                schedule.participants.map(p => (
                                                    <span key={p.id} className="badge badge-sm badge-outline">
                                                        {p.department_acronym}
                                                    </span>
                                                ))
                                            ) : (
                                                <span className="text-gray-400 italic">No participants yet</span>
                                            )}
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>
                    ))}
                </div>
            )}
        </div>
    );
}
