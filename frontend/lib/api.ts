import axios from 'axios';

const API_BASE_URL = 'http://localhost:8000/api/dashboard';

export interface Appointment {
    id: number;
    patient_id: number;
    time: string;
    status: string;
}

export interface CallLog {
    id: number;
    recording_url: string;
    transcript_summary: string;
    duration: number;
    created_at: string;
}

export interface Patient {
    id: number;
    first_name: string; // Encrypted on backend, decrypted on read? 
    // Actually, the backend API should return decrypted values if the user is authorized.
    // But for this demo, let's assume the backend handles it.
}

export const api = {
    getAppointments: async (): Promise<string[]> => {
        // The mock service currently returns a list of strings (datetimes)
        const response = await axios.get<string[]>(`${API_BASE_URL}/appointments`);
        return response.data;
    },

    getCalls: async (): Promise<CallLog[]> => {
        const response = await axios.get<CallLog[]>(`${API_BASE_URL}/calls`);
        return response.data;
    }
};
