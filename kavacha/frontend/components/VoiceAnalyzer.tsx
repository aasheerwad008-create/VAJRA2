"use client";
import { useState, useRef } from "react";

interface VoiceAnalyzerProps {
  onScoreUpdate: (data: Record<string, unknown>) => void;
  analyzing: boolean;
  setAnalyzing: (v: boolean) => void;
}

export default function VoiceAnalyzer({ onScoreUpdate, analyzing, setAnalyzing }: VoiceAnalyzerProps) {
  const [recording, setRecording] = useState(false);
  const [enrolled, setEnrolled] = useState(false);
  const [status, setStatus] = useState("Ready");
  const mrRef = useRef<MediaRecorder|null>(null);
  const wsRef = useRef<WebSocket|null>(null);
  const streamRef = useRef<MediaStream|null>(null);

  const start = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      streamRef.current = stream;
      const ws = new WebSocket("ws://localhost:8000/ws/voice/stream/demo");
      wsRef.current = ws;
      ws.onmessage = e => onScoreUpdate(JSON.parse(e.data));
      ws.onopen = () => {
        setRecording(true); setAnalyzing(true); setStatus("🔴 Recording — RAKSHA active");
        const mr = new MediaRecorder(stream, { mimeType: "audio/webm" });
        mrRef.current = mr;
        mr.ondataavailable = async e => {
          if (e.data.size>0 && ws.readyState===1) {
            const ab = await e.data.arrayBuffer();
            const b64 = btoa(String.fromCharCode(...new Uint8Array(ab)));
            ws.send(JSON.stringify({ type:"audio_chunk", audio_b64:b64 }));
          }
        };
        mr.start(2000);
      };
    } catch { setStatus("⚠️ Mic denied — use Demo Scenarios"); }
  };

  const stop = () => {
    mrRef.current?.stop();
    streamRef.current?.getTracks().forEach(t=>t.stop());
    wsRef.current?.close();
    setRecording(false); setAnalyzing(false); setStatus("Analysis complete");
  };

  const enroll = async () => {
    setStatus("Speak for 5 seconds...");
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      const mr = new MediaRecorder(stream); const chunks: Blob[] = [];
      mr.ondataavailable = e => chunks.push(e.data);
      mr.onstop = async () => {
        stream.getTracks().forEach(t=>t.stop());
        const blob = new Blob(chunks);
        const ab = await blob.arrayBuffer();
        const b64 = btoa(String.fromCharCode(...new Uint8Array(ab)));
        const res = await fetch("http://localhost:8000/api/v1/voice/enroll",{
          method:"POST", headers:{"Content-Type":"application/json"},
          body: JSON.stringify({ user_id:"demo_user", audio_base64:b64 })
        });
        const d = await res.json();
        setEnrolled(true); setStatus(`✅ Enrolled: ${d.voice_passport_hash?.slice(0,12)}...`);
      };
      mr.start(); setTimeout(()=>mr.stop(), 5000);
    } catch { setStatus("Enrollment failed"); }
  };

  return (
    <div className="bg-[#0D0D1A] border border-[#1a1a2e] rounded-xl p-4">
      <p className="text-[10px] text-gray-500 mb-3 uppercase tracking-widest">Voice Input</p>
      <div className="mb-3 p-2 bg-[#0A0A0F] rounded border border-[#1a1a2e]">
        <p className="text-[10px] text-gray-400">{status}</p>
      </div>
      <div className="flex gap-2 mb-3">
        <button onClick={enroll} disabled={enrolled||recording}
          className="flex-1 py-2 bg-[#0066FF15] border border-[#0066FF] text-[#0066FF] rounded-lg text-xs disabled:opacity-40 hover:bg-[#0066FF25] transition-all">
          {enrolled ? "✅ Enrolled" : "Enroll Voice"}
        </button>
        <button onClick={recording?stop:start}
          className={`flex-1 py-2 rounded-lg text-xs font-bold transition-all ${recording?"bg-red-900 border border-red-500 text-red-300 animate-pulse":"bg-[#00FF8815] border border-[#00FF88] text-[#00FF88] hover:bg-[#00FF8825]"}`}>
          {recording ? "⏹ Stop" : "▶ Start"}
        </button>
      </div>
      <div className="h-12 bg-[#0A0A0F] rounded border border-[#1a1a2e] flex items-center px-2 gap-0.5">
        {Array.from({length:40}).map((_,i) => (
          <div key={i} className={`flex-1 rounded-full transition-all duration-75 ${recording?"bg-[#00FF88]":"bg-[#1a1a2e]"}`}
            style={{height: recording ? `${15+Math.random()*70}%`:"15%"}} />
        ))}
      </div>
    </div>
  );
}
