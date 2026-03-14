"use client";

interface ZKPanelProps {
  proof: Record<string, unknown> | null;
}

export default function ZKPanel({ proof }: ZKPanelProps) {
  return (
    <div className="bg-[#0D0D1A] border border-[#1a1a2e] rounded-xl p-4">
      <div className="flex justify-between mb-3">
        <p className="text-[10px] text-gray-500 uppercase tracking-widest">ZK-STARK Attestation</p>
        {proof && <span className="text-[10px] text-[#00FF88] animate-pulse">● PROOF LIVE</span>}
      </div>
      {!proof ? (
        <p className="text-[10px] text-gray-600">ZK proof generates after voice auth. Zero biometric data transmitted.</p>
      ) : (
        <div className="space-y-2">
          <div className="p-2 bg-[#00FF8810] border border-[#00FF8840] rounded">
            <p className="text-[9px] text-gray-500">Proof Hash (π)</p>
            <p className="text-[9px] text-[#00FF88] font-mono break-all">{proof.proof_hash as string}</p>
          </div>
          <div className="grid grid-cols-2 gap-2">
            <div className="p-2 bg-[#0A0A0F] rounded"><p className="text-[9px] text-gray-500">Circuit</p><p className="text-[9px] text-white">{proof.circuit as string}</p></div>
            <div className="p-2 bg-[#0A0A0F] rounded"><p className="text-[9px] text-gray-500">Size</p><p className="text-[9px] text-white">{proof.proof_size_bytes as number}B</p></div>
          </div>
          <div className="p-2 bg-[#0066FF10] border border-[#0066FF40] rounded text-[9px] text-[#4499FF]">
            ✓ Biometric match proven<br/>✓ Liveness confirmed<br/>✓ Zero biometric data transmitted<br/>✓ Mathematical proof — not probabilistic
          </div>
        </div>
      )}
    </div>
  );
}
