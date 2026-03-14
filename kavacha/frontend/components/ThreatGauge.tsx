"use client";
import { useEffect, useRef } from "react";

interface ThreatGaugeProps {
  score: number;
  verdict: string;
  analyzing: boolean;
}

export default function ThreatGauge({ score, verdict, analyzing }: ThreatGaugeProps) {
  const ref = useRef<HTMLCanvasElement>(null);
  useEffect(() => {
    const c = ref.current; if (!c) return;
    const ctx = c.getContext("2d")!;
    const W=c.width, H=c.height, cx=W/2, cy=H*0.62, r=Math.min(W,H)*0.38;
    ctx.clearRect(0,0,W,H);
    ctx.beginPath(); ctx.arc(cx,cy,r,Math.PI,2*Math.PI);
    ctx.strokeStyle="#1a1a2e"; ctx.lineWidth=18; ctx.stroke();
    const g = ctx.createLinearGradient(0,0,W,0);
    g.addColorStop(0,"#FF0040"); g.addColorStop(0.5,"#FF8C00"); g.addColorStop(1,"#00FF88");
    ctx.beginPath(); ctx.arc(cx,cy,r,Math.PI,Math.PI+(score/100)*Math.PI);
    ctx.strokeStyle=g; ctx.lineWidth=18; ctx.lineCap="round"; ctx.stroke();
    const color = score>70?"#00FF88":score>40?"#FF8C00":"#FF0040";
    ctx.fillStyle=color; ctx.font=`bold ${W*0.16}px monospace`;
    ctx.textAlign="center"; ctx.textBaseline="middle";
    ctx.fillText(Math.round(score).toString(), cx, cy-8);
    ctx.fillStyle="#666"; ctx.font=`${W*0.055}px monospace`;
    ctx.fillText("TRUST SCORE", cx, cy+22);
    ctx.fillStyle=color; ctx.font=`bold ${W*0.065}px monospace`;
    ctx.fillText(analyzing?"ANALYZING...":verdict, cx, cy+48);
  }, [score, verdict, analyzing]);
  return (
    <div className="bg-[#0D0D1A] border border-[#1a1a2e] rounded-xl p-4">
      <p className="text-[10px] text-gray-500 mb-2 uppercase tracking-widest">RAKSHA Threat Engine</p>
      <canvas ref={ref} width={300} height={190} className="w-full" />
    </div>
  );
}
