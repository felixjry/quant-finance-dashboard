import { useEffect, useState } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { TrendingUp, TrendingDown, AlertCircle, RefreshCw, Activity } from "lucide-react";
import { api, TradingSignal } from "@/services/api";
import { toast } from "sonner";
import { cn } from "@/lib/utils";

interface SignalIndicatorProps {
  symbol: string;
  onTrade?: (signal: TradingSignal) => void;
  compact?: boolean;
}

export const SignalIndicator = ({ symbol, onTrade, compact = false }: SignalIndicatorProps) => {
  const [signals, setSignals] = useState<TradingSignal[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [lastScan, setLastScan] = useState<Date | null>(null);

  useEffect(() => {
    if (symbol) {
      scanSignals();
    }
  }, [symbol]);

  const scanSignals = async () => {
    if (!symbol) return;

    try {
      setIsLoading(true);
      const data = await api.getTradingSignals(symbol);
      setSignals(data.signals);
      setLastScan(new Date());

      if (data.signals_count > 0) {
        const buySignals = data.signals.filter((s) => s.signal_type === "buy").length;
        const sellSignals = data.signals.filter((s) => s.signal_type === "sell").length;

        if (buySignals > 0) {
          toast.success(`${buySignals} BUY signal(s) detected for ${symbol}`);
        }
        if (sellSignals > 0) {
          toast.info(`${sellSignals} SELL signal(s) detected for ${symbol}`);
        }
      }
    } catch (error) {
      console.error("Failed to scan signals:", error);
      toast.error("Failed to scan signals");
    } finally {
      setIsLoading(false);
    }
  };

  const getSignalSummary = () => {
    if (signals.length === 0) return { type: "neutral", count: 0, strength: "none" };

    const buySignals = signals.filter((s) => s.signal_type === "buy");
    const sellSignals = signals.filter((s) => s.signal_type === "sell");

    const strongBuy = buySignals.filter((s) => s.strength === "strong").length;
    const strongSell = sellSignals.filter((s) => s.strength === "strong").length;

    if (buySignals.length > sellSignals.length) {
      return {
        type: "buy",
        count: buySignals.length,
        strength: strongBuy > 0 ? "strong" : buySignals.some((s) => s.strength === "moderate") ? "moderate" : "weak",
      };
    } else if (sellSignals.length > buySignals.length) {
      return {
        type: "sell",
        count: sellSignals.length,
        strength: strongSell > 0 ? "strong" : sellSignals.some((s) => s.strength === "moderate") ? "moderate" : "weak",
      };
    }

    return { type: "neutral", count: signals.length, strength: "mixed" };
  };

  const summary = getSignalSummary();

  if (compact) {
    return (
      <div className="flex items-center gap-2">
        <Button
          variant="outline"
          size="sm"
          onClick={scanSignals}
          disabled={isLoading}
          className="gap-2"
        >
          <Activity className={cn("w-4 h-4", isLoading && "animate-spin")} />
          Scan Signals
        </Button>

        {signals.length > 0 && (
          <Badge
            variant={summary.type === "buy" ? "default" : summary.type === "sell" ? "destructive" : "secondary"}
            className="gap-1"
          >
            {summary.type === "buy" ? (
              <TrendingUp className="w-3 h-3" />
            ) : summary.type === "sell" ? (
              <TrendingDown className="w-3 h-3" />
            ) : (
              <AlertCircle className="w-3 h-3" />
            )}
            {summary.count} {summary.type.toUpperCase()} Signal{summary.count !== 1 ? "s" : ""}
          </Badge>
        )}

        {lastScan && (
          <span className="text-xs text-muted-foreground">
            Last scan: {lastScan.toLocaleTimeString()}
          </span>
        )}
      </div>
    );
  }

  return (
    <Card>
      <CardHeader>
        <div className="flex items-center justify-between">
          <CardTitle className="flex items-center gap-2">
            <Activity className="w-5 h-5" />
            Trading Signals for {symbol}
          </CardTitle>
          <Button
            variant="outline"
            size="sm"
            onClick={scanSignals}
            disabled={isLoading}
            className="gap-2"
          >
            <RefreshCw className={cn("w-4 h-4", isLoading && "animate-spin")} />
            Scan
          </Button>
        </div>
        {lastScan && (
          <p className="text-sm text-muted-foreground">
            Last scan: {lastScan.toLocaleString()}
          </p>
        )}
      </CardHeader>
      <CardContent>
        {isLoading && signals.length === 0 ? (
          <div className="flex items-center justify-center py-8">
            <div className="w-8 h-8 border-2 border-primary border-t-transparent rounded-full animate-spin" />
          </div>
        ) : signals.length > 0 ? (
          <div className="space-y-4">
            {/* Summary Badge */}
            <div className="flex items-center gap-3">
              <Badge
                variant={summary.type === "buy" ? "default" : summary.type === "sell" ? "destructive" : "secondary"}
                className="text-base px-4 py-2 gap-2"
              >
                {summary.type === "buy" ? (
                  <TrendingUp className="w-4 h-4" />
                ) : summary.type === "sell" ? (
                  <TrendingDown className="w-4 h-4" />
                ) : (
                  <AlertCircle className="w-4 h-4" />
                )}
                {summary.type.toUpperCase()} SIGNAL
              </Badge>
              <div className="text-sm text-muted-foreground">
                {summary.count} signal{summary.count !== 1 ? "s" : ""} detected • {summary.strength} strength
              </div>
            </div>

            {/* Signal Details */}
            <div className="space-y-3">
              {signals.map((signal, idx) => {
                const isBuy = signal.signal_type === "buy";
                const signalColor = isBuy ? "border-green-500 bg-green-500/5" : "border-red-500 bg-red-500/5";
                const SignalIcon = isBuy ? TrendingUp : TrendingDown;

                return (
                  <div
                    key={idx}
                    className={cn("p-4 border rounded-lg", signalColor)}
                  >
                    <div className="flex items-start justify-between gap-4">
                      <div className="flex items-start gap-3 flex-1">
                        <SignalIcon className="w-5 h-5 mt-0.5 flex-shrink-0" />
                        <div className="flex-1 min-w-0">
                          <div className="flex items-center gap-2 mb-1">
                            <span className="font-semibold">{signal.strategy}</span>
                            <Badge variant="outline" className="text-xs">
                              {signal.strength}
                            </Badge>
                          </div>
                          <p className="text-sm text-muted-foreground mb-2">
                            {signal.message}
                          </p>
                          <div className="flex flex-wrap gap-x-4 gap-y-1 text-xs text-muted-foreground">
                            <span>Price: ${signal.price.toFixed(2)}</span>
                            {Object.entries(signal.indicators).map(([key, value]) => (
                              <span key={key}>
                                {key}: {typeof value === "number" ? value.toFixed(2) : value}
                              </span>
                            ))}
                          </div>
                        </div>
                      </div>
                      {onTrade && (
                        <Button
                          size="sm"
                          variant={isBuy ? "default" : "destructive"}
                          onClick={() => onTrade(signal)}
                          className="flex-shrink-0"
                        >
                          {isBuy ? "Buy" : "Sell"}
                        </Button>
                      )}
                    </div>
                  </div>
                );
              })}
            </div>
          </div>
        ) : (
          <div className="text-center py-8">
            <AlertCircle className="w-12 h-12 mx-auto mb-3 text-muted-foreground opacity-50" />
            <p className="text-muted-foreground">No signals detected</p>
            <p className="text-sm text-muted-foreground mt-1">
              Click "Scan" to analyze {symbol} for trading opportunities
            </p>
          </div>
        )}
      </CardContent>
    </Card>
  );
};
