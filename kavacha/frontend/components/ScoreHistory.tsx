"use client";
import { useEffect, useRef } from "react";

interface ScoreHistoryProps {
  history: number[];
}

export default function ScoreHistory({ history }: ScoreHistoryProps) {
  const ref = useRef<HTMLCanvasElement>(null);
  useEffect(() => {
    const c = ref.current; if (!c) return;
    const ctx = c.getContext("2d")!;
    const W=c.width, H=c.height;
    ctx.clearRect(0,0,W,H);
    ctx.fillStyle="#0A0A0F"; ctx.fillRect(0,0,W,H);
    if (!history.length) { ctx.strokeStyle="#1a1a2e"; ctx.beginPath(); ctx.moveTo(0,H/2); ctx.lineTo(W,H/2); ctx.stroke(); return; }
    const step = W/Math.max(history.length-1,1);
    const g = ctx.createLinearGradient(0,0,W,0);
    g.addColorStop(0,"#FF0040"); g.addColorStop(0.5,"#FF8C00"); g.addColorStop(1,"#00FF88");
    ctx.strokeStyle=g; ctx.lineWidth=2; ctx.shadowBlur=6; ctx.shadowColor="#00FF88";
    ctx.beginPath();
    history.forEach((s,i)=>{ const x=i*step, y=H-(s/100)*H*0.88-H*0.06; i===0?ctx.moveTo(x,y):ctx.lineTo(x,y); });
    ctx.stroke();
    ctx.shadowBlur=0;
    [40,70].forEach(t=>{ const y=H-(t/100)*H*0.88-H*0.06; ctx.strokeStyle=t===40?"#FF004050":"#00FF8850"; ctx.lineWidth=1; ctx.setLineDash([3,3]); ctx.beginPath(); ctx.moveTo(0,y); ctx.lineTo(W,y); ctx.stroke(); ctx.setLineDash([]); });
  }, [history]);
  return (
    <div className="bg-[#0D0D1A] border border-[#1a1a2e] rounded-xl p-4">
      <p className="text-[10px] text-gray-500 mb-2 uppercase tracking-widest">Trust Score History</p>
      <canvas ref={ref} width={360} height={90} className="w-full rounded" />
      <div className="flex justify-between text-[9px] text-gray-600 mt-1">
        <span>← 20 samples</span><span className="text-[#FF0040]">Block:40</span><span className="text-[#00FF88]">Verify:70</span>
      </div>
    </div>
  );
}
