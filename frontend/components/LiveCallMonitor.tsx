'use client';

import React, { useEffect, useState, useRef } from 'react';
import { Mic, Activity, User, Phone, PhoneOff, AlertCircle } from 'lucide-react';

interface TranscriptItem {
    text: string;
    isFinal: boolean;
    speaker: 'user' | 'agent';
}

export default function LiveCallMonitor() {
    const [isCallActive, setIsCallActive] = useState(false);
    const [status, setStatus] = useState<'IDLE' | 'LISTENING' | 'SPEAKING'>('IDLE');
    const [transcripts, setTranscripts] = useState<TranscriptItem[]>([]);
    const [uiError, setUiError] = useState<string | null>(null); // New Error State

    const socketRef = useRef<WebSocket | null>(null);
    const audioContextRef = useRef<AudioContext | null>(null);
    const mediaRecorderRef = useRef<MediaRecorder | null>(null);
    const streamRef = useRef<MediaStream | null>(null);

    // Buffer for incoming audio to ensure smooth playback (simple queue)
    const audioQueueRef = useRef<AudioBuffer[]>([]);
    const isPlayingRef = useRef(false);

    const startCall = async () => {
        setUiError(null); // Clear previous errors
        console.log("Attempting to start call...");

        try {
            // 1. Initialize Audio Context (must be user initiated)
            console.log("Resuming Audio Context...");
            const AudioContextClass = window.AudioContext || (window as any).webkitAudioContext;
            const ctx = new AudioContextClass();
            await ctx.resume();
            audioContextRef.current = ctx;

            // 2. Get Microphone Access
            console.log("Requesting Microphone Access...");
            const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
            streamRef.current = stream;
            console.log("Microphone access granted.");

            // 3. Connect WebSocket
            const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
            const backendUrl = process.env.NEXT_PUBLIC_BACKEND_URL || 'localhost:8000';
            const wsUrl = `${protocol}//${backendUrl}/ws/conversation`;
            console.log("🚀 Connecting to Cloud Backend:", wsUrl);
            const ws = new WebSocket(wsUrl);
            ws.binaryType = 'arraybuffer'; // Crucial for receiving audio chunks
            socketRef.current = ws;

            ws.onopen = () => {
                console.log("✅ WebSocket Connection OPEN!");
                setStatus('LISTENING');
                setIsCallActive(true);
                setTranscripts([]); // Clear previous session

                // 4. Start MediaRecorder
                console.log("Starting MediaRecorder...");
                const recorder = new MediaRecorder(stream, { mimeType: 'audio/webm;codecs=opus' });
                mediaRecorderRef.current = recorder;

                recorder.ondataavailable = (event) => {
                    if (event.data.size > 0 && ws.readyState === WebSocket.OPEN) {
                        ws.send(event.data);
                    }
                };

                recorder.start(250); // Send chunks every 250ms
            };

            ws.onmessage = async (event) => {
                if (event.data instanceof ArrayBuffer) {
                    // Handle Binary Audio (from ElevenLabs via Backend)
                    if (ctx.state === 'suspended') await ctx.resume();
                    try {
                        // Decode asynchronously
                        const audioBuffer = await ctx.decodeAudioData(event.data);
                        playAudioBuffer(ctx, audioBuffer);
                    } catch (err) {
                        console.error("Audio Decode Error", err);
                    }
                } else {
                    // Handle JSON Messages
                    try {
                        const data = JSON.parse(event.data);
                        if (data.type === 'transcript') {
                            const item: TranscriptItem = {
                                text: data.text,
                                isFinal: data.is_final,
                                speaker: 'user'
                            };
                            setTranscripts(prev => [...prev, item]); // Simply append for demo
                        } else if (data.type === 'llm_chunk') {
                            setStatus('SPEAKING');
                            // Typically we'd append text here too if we want to show LLM/Agent text
                            const item: TranscriptItem = {
                                text: data.text,
                                isFinal: false,
                                speaker: 'agent'
                            };
                            // Basic logic: if last was agent and not final, update it, else append.
                            // For safety in this demo, let's just log agent chunks or append them.
                            setTranscripts(prev => {
                                const last = prev[prev.length - 1];
                                if (last && last.speaker === 'agent' && !last.isFinal) {
                                    return [...prev.slice(0, -1), { ...last, text: last.text + data.text }];
                                }
                                return [...prev, item];
                            });
                        }
                    } catch (e) {
                        console.error("WS Parse Error", e);
                    }
                }
            };

            ws.onclose = (ev) => {
                console.warn("⚠️ WebSocket Closed. Code:", ev.code, "Reason:", ev.reason);
                if (ev.code !== 1000 && !ev.wasClean) {
                    setUiError(`Connection closed unexpectedly (Code: ${ev.code})`);
                }
                stopCall();
            };

            ws.onerror = (err) => {
                console.error("❌ WebSocket Error:", err);
                setUiError("WebSocket Connection Failed. Is the backend running?");
                stopCall();
            };

        } catch (err: any) {
            console.error("Failed to start call", err);
            // Detailed error message for user
            let errorMessage = "Could not start call.";
            if (err.name === 'NotAllowedError') {
                errorMessage = "Microphone permission denied. Please allow access.";
            } else if (err.name === 'NotFoundError') {
                errorMessage = "No microphone found.";
            } else {
                errorMessage = `Error: ${err.message || err}`;
            }
            setUiError(errorMessage);
            stopCall();
        }
    };

    const stopCall = () => {
        setIsCallActive(false);
        setStatus('IDLE');

        // Close WS
        if (socketRef.current) {
            if (socketRef.current.readyState === WebSocket.OPEN) {
                socketRef.current.close();
            }
            socketRef.current = null;
        }

        // Stop Recorder
        if (mediaRecorderRef.current && mediaRecorderRef.current.state !== 'inactive') {
            mediaRecorderRef.current.stop();
            mediaRecorderRef.current = null;
        }

        // Stop Mic Stream
        if (streamRef.current) {
            streamRef.current.getTracks().forEach(track => track.stop());
            streamRef.current = null;
        }

        // Close Audio Context
        if (audioContextRef.current) {
            audioContextRef.current.close();
            audioContextRef.current = null;
        }
    };

    // Simple audio queue player to prevent overlapping chunks
    const playAudioBuffer = (ctx: AudioContext, buffer: AudioBuffer) => {
        const source = ctx.createBufferSource();
        source.buffer = buffer;
        source.connect(ctx.destination);
        source.start(0);
        // Note: real implementation needs a proper queue to schedule 'source.start(nextStartTime)'
    };

    // Clean up on unmount
    useEffect(() => {
        return () => stopCall();
    }, []);

    return (
        <div className="bg-white rounded-xl shadow-md p-6 border border-slate-200">
            <div className="flex items-center justify-between mb-4">
                <h2 className="text-xl font-bold text-slate-800 flex items-center gap-2">
                    <Activity className="w-5 h-5 text-blue-500" />
                    Live Monitor
                </h2>
                <div className="flex items-center gap-3">
                    <span className={`px-3 py-1 rounded-full text-xs font-semibold ${status === 'LISTENING' ? 'bg-green-100 text-green-700' :
                        status === 'SPEAKING' ? 'bg-blue-100 text-blue-700' :
                            'bg-slate-100 text-slate-500'
                        }`}>
                        {status}
                    </span>
                </div>
            </div>

            {/* Transcript Log */}
            <div className="h-64 overflow-y-auto bg-slate-50 rounded-lg p-4 border border-slate-100 space-y-3 mb-4">
                {transcripts.length === 0 && (
                    <p className="text-slate-400 text-center italic">Ready to start call...</p>
                )}
                {transcripts.map((t, i) => (
                    <div key={i} className={`flex gap-3 ${t.speaker === 'agent' ? 'flex-row-reverse' : ''}`}>
                        <div className={`w-8 h-8 rounded-full flex items-center justify-center shrink-0 ${t.speaker === 'agent' ? 'bg-blue-100 text-blue-600' : 'bg-slate-200 text-slate-600'
                            }`}>
                            {t.speaker === 'agent' ? <Activity size={14} /> : <User size={14} />}
                        </div>
                        <div className={`p-3 rounded-lg text-sm max-w-[80%] ${t.speaker === 'agent' ? 'bg-blue-50 text-blue-900' : 'bg-white border border-slate-200 text-slate-700'
                            }`}>
                            {t.text}
                        </div>
                    </div>
                ))}
            </div>

            {/* Controls */}
            <div className="flex flex-col items-center gap-3">
                {uiError && (
                    <div className="flex items-center gap-2 text-red-600 bg-red-50 px-4 py-2 rounded-lg text-sm w-full justify-center">
                        <AlertCircle size={16} />
                        <span>{uiError}</span>
                    </div>
                )}

                {!isCallActive ? (
                    <button
                        onClick={startCall}
                        className="flex items-center gap-2 bg-green-600 hover:bg-green-700 text-white px-6 py-3 rounded-full font-semibold shadow-lg transition-all active:scale-95"
                    >
                        <Phone size={20} />
                        Start Call
                    </button>
                ) : (
                    <button
                        onClick={stopCall}
                        className="flex items-center gap-2 bg-red-600 hover:bg-red-700 text-white px-6 py-3 rounded-full font-semibold shadow-lg transition-all active:scale-95 animate-pulse"
                    >
                        <PhoneOff size={20} />
                        End Call
                    </button>
                )}
            </div>
        </div>
    );
}
