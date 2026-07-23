export default function MarketWatch() {
  const data = [
    { label: "SENSEX", value: "74,248.22", change: "+354.45", changePct: "(0.48%)", isPositive: true },
    { label: "NIFTY 50", value: "24,315.90", change: "+124.50", changePct: "(0.51%)", isPositive: true },
    { label: "GOLD", value: "72,450.00", change: "+180.50", changePct: "(0.25%)", isPositive: true },
    { label: "USD/INR", value: "83.42", change: "-0.05", changePct: "(-0.06%)", isPositive: false },
  ];

  return (
    <div className="flex h-12 w-full items-center gap-8 border-y border-ink/20 bg-paper px-12 sm:px-20">
      {/* Label */}
      <div className="font-mono text-[10px] uppercase tracking-[0.15em] text-ink/60 shrink-0">
        MARKET WATCH
      </div>

      {/* Grid container for the 4 tickers */}
      <div className="flex flex-1 items-center gap-8 overflow-hidden">
        {data.map((item, index) => (
          <div key={index} className="flex items-center gap-1.5 whitespace-nowrap">
            <span className="font-mono text-[10px] uppercase text-ink">
              {item.label}
            </span>
            <span className="font-mono text-[12px] font-bold text-ink">
              {item.value}
            </span>
            <span
              className={`font-mono text-[10px] font-medium tracking-tight ${
                item.isPositive ? "text-[#2e7d32]" : "text-[#c62828]"
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
