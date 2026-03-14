"use client";
import { useState, useRef } from "react";

export default function AdversarialShield() {
  const [active, setActive] = useState(false);
  const [method, setMethod] = useState<"fgsm"|"pgd">("pgd");
  const [stats, setStats] = useState<Record<string, unknown> | null>(null);
  const vidRef = useRef<HTMLVideoElement>(null);
  const canRef = useRef<HTMLCanvasElement>(null);
  const itvRef = useRef<ReturnType<typeof setInterval> | undefined>(undefined);

  const start = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ video: true });
      if (vidRef.current) vidRef.current.srcObject = stream;
      setActive(true);
      itvRef.current = setInterval(async () => {
        if (!vidRef.current||!canRef.current) return;
        const ctx = canRef.current.getContext("2d")!;
        canRef.current.width = vidRef.current.videoWidth||320;
        canRef.current.height = vidRef.current.videoHeight||240;
        ctx.drawImage(vidRef.current,0,0);
        const b64 = canRef.current.toDataURL("image/jpeg").split(",")[1];
        const res = await fetch("http://localhost:8000/api/v1/video/perturb",{
          method:"POST", headers:{"Content-Type":"application/json"},
          body: JSON.stringify({ frame_base64:b64, method })
        });
        const d = await res.json(); setStats(d);
        if (d.perturbed_frame) {
          const img = new Image();
          img.onload = () => ctx.drawImage(img,0,0);
          img.src = `data:image/jpeg;base64,${d.perturbed_frame}`;
        }
      }, 500);
    } catch { setActive(false); }
  };

  const stop = () => {
    clearInterval(itvRef.current); setActive(false);
    const s = vidRef.current?.srcObject as MediaStream;
    s?.getTracks().forEach(t=>t.stop());
  };

  return (
    <div className="bg-[#0D0D1A] border border-[#1a1a2e] rounded-xl p-4">
      <div className="flex justify-between mb-3">
        <p className="text-[10px] text-gray-500 uppercase tracking-widest">Adversarial Shield</p>
        {active && <span className="text-[10px] text-orange-400 animate-pulse">● ACTIVE</span>}
      </div>
      <div className="relative bg-black rounded overflow-hidden mb-3" style={{height:"100px"}}>
        <video ref={vidRef} autoPlay muted className="hidden" />
        <canvas ref={canRef} className="w-full h-full object-cover" />
        {!active && <div className="absolute inset-0 flex items-center justify-center text-[10px] text-gray-600">Camera + adversarial noise</div>}
        {active && <div className="absolute top-1 left-1 bg-orange-900/80 border border-orange-500 rounded px-1.5 py-0.5"><p className="text-[9px] text-orange-300">{method.toUpperCase()} ε={method==="pgd"?"10":"8"}/255</p></div>}
      </div>
      <div className="flex gap-2 mb-2">
        {(["fgsm","pgd"] as const).map(m=>(
          <button key={m} onClick={()=>setMethod(m)}
            className={`flex-1 py-1 rounded text-[10px] border transition-all ${method===m?"bg-orange-900/50 border-orange-500 text-orange-300":"border-[#1a1a2e] text-gray-500"}`}>
            {m.toUpperCase()}
          </button>
        ))}
      </div>
      <button onClick={active?stop:start}
        className={`w-full py-2 rounded-lg text-xs font-bold transition-all ${active?"bg-red-900/50 border border-red-500 text-red-300":"bg-orange-900/30 border border-orange-600 text-orange-300 hover:bg-orange-900/50"}`}>
        {active ? "⏹ Stop" : "⚡ Activate Shield"}
      </button>
      {stats && <p className="text-[9px] text-gray-500 mt-2">{(stats.message as string)?.slice(0,50)} | Faces: {stats.faces_detected as number}</p>}
    </div>
  );
}
