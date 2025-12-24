

import { useQuery } from '@tanstack/react-query';

interface TickerAsset {
  symbol: string;
  price: number;
  changePercent: number;
}

const API_BASE_URL = '/api';

export function MarketTicker() {
  const { data: quotes, isLoading } = useQuery({
    queryKey: ['tickerQuotes'],
    queryFn: async () => {
      const response = await fetch(`${API_BASE_URL}/quotes`);
      const data = await response.json();
      return data.assets || data;
    },
    refetchInterval: 60000,
    staleTime: 30000,
  });

  if (isLoading || !quotes || !Array.isArray(quotes) || quotes.length === 0) {
    return (
      <div className="bg-slate-900 text-slate-400 py-3 overflow-hidden">
        <div className="flex items-center justify-center text-sm">
          Chargement des données de marché...
        </div>
      </div>
    );
  }

  const duplicatedItems = [...quotes, ...quotes];

  return (
    <div className="bg-slate-900 py-3 overflow-hidden border-b border-slate-800">
      <div className="ticker-container">
        <div className="ticker-content">
          {duplicatedItems.map((asset, index) => (
            <TickerItem key={`${asset.symbol}-${index}`} asset={asset} />
          ))}
        </div>
      </div>
      <style>{`
        .ticker-container {
          overflow: hidden;
          width: 100%;
        }
        .ticker-content {
          display: flex;
          gap: 3rem;
          animation: ticker-scroll 40s linear infinite;
          width: max-content;
        }
        @keyframes ticker-scroll {
          0% {
            transform: translateX(0);
          }
          100% {
            transform: translateX(-50%);
          }
        }
        .ticker-content:hover {
          animation-play-state: paused;
        }
      `}</style>
    </div>
  );
}

function TickerItem({ asset }: { asset: TickerAsset }) {
  const isPositive = asset.changePercent >= 0;
  const colorClass = isPositive ? 'text-green-400' : 'text-red-400';
  const arrow = isPositive ? '▲' : '▼';

  const formatSymbol = (symbol: string) => {
    if (symbol === 'EURUSD=X') return 'EUR/USD';
    if (symbol.endsWith('-USD')) return symbol.replace('-USD', '');
    return symbol;
  };

  return (
    <div className="flex items-center gap-3 text-base whitespace-nowrap px-4">
      <span className="text-slate-300 font-medium">{formatSymbol(asset.symbol)}</span>
      <span className="text-slate-100">${asset.price.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}</span>
      <span className={`${colorClass} font-medium`}>
        {arrow} {Math.abs(asset.changePercent).toFixed(2)}%
      </span>
    </div>
  );
}
