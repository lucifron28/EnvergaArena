import { useQuery } from '@tanstack/react-query';
import api from '../services/api';

// --- Types ---
export interface Department {
    id: number;
    name: string;
    acronym: string;
    color_code?: string;
}

export interface EventParticipant {
    id: number;
    department: number;
    department_name: string;
    department_acronym: string;
}

export interface EventSchedule {
    id: number;
    event: number;
    event_name: string;
    result_family: string;
    venue: number | null;
    venue_name: string | null;
    venue_area: number | null;
    venue_area_name: string | null;
    scheduled_start: string | null;
    scheduled_end: string | null;
    notes: string;
    participants: EventParticipant[];
    created_at: string;
    updated_at: string;
}

export interface MatchSetScore {
    id: number;
    set_number: number;
    home_score: number;
    away_score: number;
}

export interface MatchResult {
    id: number;
    schedule: number;
    event_name: string;
    home_department: number;
    home_department_name: string;
    away_department: number;
    away_department_name: string;
    home_score: number;
    away_score: number;
    winner: number | null;
    winner_name: string | null;
    is_draw: boolean;
    is_final: boolean;
    sets: MatchSetScore[];
    recorded_at: string;
    updated_at: string;
}

export interface PodiumResult {
    id: number;
    schedule: number;
    event_name: string;
    department: number;
    department_name: string;
    department_acronym: string;
    rank: number;
    medal: 'gold' | 'silver' | 'bronze' | 'none';
    points_awarded: number;
    is_final: boolean;
    recorded_at: string;
    updated_at: string;
}

export interface MedalTally {
    id: number;
    department: number;
    department_name: string;
    department_acronym: string;
    department_color: string;
    gold: number;
    silver: number;
    bronze: number;
    total_points: number;
    last_updated: string;
}

// --- Hooks ---
export const useSchedules = () => {
    return useQuery<EventSchedule[]>({
        queryKey: ['schedules'],
        queryFn: async () => {
            const { data } = await api.get('/public/schedules/');
            return data;
        },
    });
};

export const useMatchResults = () => {
    return useQuery<MatchResult[]>({
        queryKey: ['match-results'],
        queryFn: async () => {
            const { data } = await api.get('/public/match-results/');
            return data;
        },
    });
};

export const usePodiumResults = () => {
    return useQuery<PodiumResult[]>({
        queryKey: ['podium-results'],
        queryFn: async () => {
            const { data } = await api.get('/public/podium-results/');
            return data;
        },
    });
};

export const useMedalTally = () => {
    return useQuery<MedalTally[]>({
        queryKey: ['medal-tally'],
        queryFn: async () => {
            const { data } = await api.get('/public/medal-tally/');
            return data;
        },
    });
};
