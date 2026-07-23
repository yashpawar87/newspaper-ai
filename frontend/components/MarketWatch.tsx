export default function MarketWatch() {
  const data = [
    { label: "SENSEX", value: "74,248.22", change: "+354.45", changePct: "(0.48%)", isPositive: true },
    { label: "NIFTY 50", value: "24,315.90", change: "+124.50", changePct: "(0.51%)", isPositive: true },
    { label: "GOLD", value: "72,450.00", change: "+180.50", changePct: "(0.25%)", isPositive: true },
    { label: "USD/INR", value: "83.42", change: "-0.05", changePct: "(-0.06%)", isPositive: false },
  ];

  return (
    <div className="mb-10 flex flex-col sm:flex-row sm:items-center gap-4 sm:gap-6 border-b border-ink/15 pb-4">
      {/* Label */}
      <div className="font-mono text-[11px] font-semibold uppercase tracking-[0.15em] text-ink/40 shrink-0">
        Market Watch
      </div>

      {/* Grid container for the 4 tickers */}
      <div className="flex flex-1 flex-wrap items-center gap-x-6 gap-y-2 sm:justify-between">
        {data.map((item, index) => (
          <div key={index} className="flex items-baseline gap-2 whitespace-nowrap">
            <span className="font-display font-bold text-ink">
              {item.label}
            </span>
            <span className="font-display font-bold text-ink">
              {item.value}
            </span>
            <span
              className={`font-mono text-[12px] font-medium tracking-tight ${
                item.isPositive ? "text-[#4b7a47]" : "text-ink/60"
              }`}
            >
              {item.change} {item.changePct}
            </span>
          </div>
        ))}
      </div>
    </div>
  );
}
