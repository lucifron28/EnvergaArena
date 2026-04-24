import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import api from '../services/api';

// Types
export interface Athlete {
    id?: number;
    student_number: string;
    full_name: string;
    department: number;
    program_course: string;
    year_level: string;
    is_enrolled: boolean;
    medical_cleared: boolean;
}

export interface RosterEntry {
    id?: number;
    athlete: number;
    athlete_name?: string;
    student_number?: string;
    is_eligible?: boolean;
}

export interface EventRegistration {
    id?: number;
    schedule: number;
    department: number;
    department_name?: string;
    department_acronym?: string;
    status: 'submitted' | 'pending' | 'needs_revision' | 'approved' | 'rejected';
    admin_notes?: string;
    roster: RosterEntry[];
    created_at?: string;
    updated_at?: string;
}

// Hooks
export const useAthletes = () => {
    return useQuery<Athlete[]>({
        queryKey: ['athletes'],
        queryFn: async () => {
            const { data } = await api.get('/public/athletes/');
            return data;
        },
    });
};

export const useCreateAthlete = () => {
    const queryClient = useQueryClient();
    return useMutation({
        mutationFn: async (athlete: Athlete) => {
            const { data } = await api.post('/public/athletes/', athlete);
            return data;
        },
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ['athletes'] });
        },
    });
};

export const useRegistrations = () => {
    return useQuery<EventRegistration[]>({
        queryKey: ['registrations'],
        queryFn: async () => {
            const { data } = await api.get('/public/registrations/');
            return data;
        },
    });
};

export const useUpdateRegistrationStatus = () => {
    const queryClient = useQueryClient();
    return useMutation({
        mutationFn: async ({ id, status, admin_notes }: { id: number, status: string, admin_notes?: string }) => {
            const { data } = await api.patch(`/public/registrations/${id}/`, { status, admin_notes });
            return data;
        },
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ['registrations'] });
        },
    });
};
