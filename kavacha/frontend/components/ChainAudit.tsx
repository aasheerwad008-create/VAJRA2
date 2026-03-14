"use client";

interface ChainAuditProps {
  txHash: string;
}

export default function ChainAudit({ txHash }: ChainAuditProps) {
  return (
    <div className="bg-[#0D0D1A] border border-[#1a1a2e] rounded-xl p-4">
      <div className="flex justify-between mb-3">
        <p className="text-[10px] text-gray-500 uppercase tracking-widest">Polygon Blockchain</p>
        {txHash && <span className="text-[10px] text-purple-400 animate-pulse">● ANCHORED</span>}
      </div>
      {!txHash ? (
        <p className="text-[10px] text-gray-600">Proof hash anchored on Polygon Amoy after verification. Immutable RBI-compliant audit trail.</p>
      ) : (
        <div className="space-y-2">
          <div className="p-2 bg-[#7c3aed20] border border-[#7c3aed50] rounded">
            <p className="text-[9px] text-gray-500">TX Hash</p>
            <p className="text-[9px] text-purple-300 font-mono break-all">{txHash}</p>
          </div>
          <div className="grid grid-cols-2 gap-2 text-[9px]">
            <div className="p-2 bg-[#0A0A0F] rounded"><p className="text-gray-500">Network</p><p className="text-white">Polygon Amoy</p></div>
            <div className="p-2 bg-[#0A0A0F] rounded"><p className="text-gray-500">Status</p><p className="text-[#00FF88]">✓ Confirmed</p></div>
          </div>
          <a href={`https://amoy.polygonscan.com/tx/${txHash}`} target="_blank" rel="noopener noreferrer"
            className="block text-center py-2 bg-[#7c3aed20] border border-[#7c3aed] rounded text-[#a78bfa] text-[10px] hover:bg-[#7c3aed30] transition-all">
            View on Polygonscan →
          </a>
        </div>
      )}
    </div>
  );
}
