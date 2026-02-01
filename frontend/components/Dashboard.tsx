'use client';

import React, { useEffect, useState } from 'react';
import { Calendar, Phone, Play } from 'lucide-react';
import { api, Appointment, CallLog } from '../lib/api';

export default function Dashboard() {
    const [appointments, setAppointments] = useState<string[]>([]);
    const [calls, setCalls] = useState<CallLog[]>([]);

    useEffect(() => {
        async function loadData() {
            try {
                const aptData = await api.getAppointments();
                setAppointments(aptData);

                const callData = await api.getCalls();
                setCalls(callData);
            } catch (e) {
                console.error("Failed to fetch dashboard data", e);
            }
        }
        loadData();
    }, []);

    return (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mt-6">
            {/* Appointments */}
            <div className="bg-white rounded-xl shadow-sm border border-slate-200 p-6">
                <h3 className="text-lg font-bold text-slate-800 mb-4 flex items-center gap-2">
                    <Calendar className="w-5 h-5 text-blue-600" />
                    Available Slots
                </h3>
                <div className="overflow-hidden rounded-lg border border-slate-100">
                    <table className="w-full text-left text-sm">
                        <thead className="bg-slate-50 text-slate-600">
                            <tr>
                                <th className="p-3">Time</th>
                                <th className="p-3">Status</th>
                            </tr>
                        </thead>
                        <tbody className="divide-y divide-slate-100">
                            {appointments.map((slot, i) => (
                                <tr key={i} className="hover:bg-slate-50 transition">
                                    <td className="p-3 font-medium text-slate-700">
                                        {new Date(slot).toLocaleString()}
                                    </td>
                                    <td className="p-3">
                                        <span className="bg-green-100 text-green-700 px-2 py-0.5 rounded text-xs">open</span>
                                    </td>
                                </tr>
                            ))}
                            {appointments.length === 0 && (
                                <tr><td colSpan={2} className="p-4 text-center text-slate-400">No slots available</td></tr>
                            )}
                        </tbody>
                    </table>
                </div>
            </div>

            {/* Recent Calls */}
            <div className="bg-white rounded-xl shadow-sm border border-slate-200 p-6">
                <h3 className="text-lg font-bold text-slate-800 mb-4 flex items-center gap-2">
                    <Phone className="w-5 h-5 text-blue-600" />
                    Recent Calls
                </h3>
                <div className="overflow-hidden rounded-lg border border-slate-100">
                    <table className="w-full text-left text-sm">
                        <thead className="bg-slate-50 text-slate-600">
                            <tr>
                                <th className="p-3">Summary</th>
                                <th className="p-3">Duration</th>
                                <th className="p-3">Rec</th>
                            </tr>
                        </thead>
                        <tbody className="divide-y divide-slate-100">
                            {calls.map((call) => (
                                <tr key={call.id} className="hover:bg-slate-50 transition">
                                    <td className="p-3 text-slate-700 truncate max-w-[200px]" title={call.transcript_summary}>
                                        {call.transcript_summary || 'No summary'}
                                    </td>
                                    <td className="p-3 text-slate-500">
                                        {call.duration}s
                                    </td>
                                    <td className="p-3">
                                        {call.recording_url && (
                                            <button className="text-blue-500 hover:text-blue-700">
                                                <Play size={16} />
                                            </button>
                                        )}
                                    </td>
                                </tr>
                            ))}
                            {calls.length === 0 && (
                                <tr><td colSpan={3} className="p-4 text-center text-slate-400">No call history</td></tr>
                            )}
                        </tbody>
                    </table>
                </div>
            </div>
        </div>
    );
}
