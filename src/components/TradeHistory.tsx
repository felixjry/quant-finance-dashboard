import { useEffect, useState } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { TrendingUp, TrendingDown, History, RefreshCw } from "lucide-react";
import { api, PaperTrade } from "@/services/api";
import { toast } from "sonner";

interface TradeHistoryProps {
  userId: string;
  refreshTrigger?: number;
}

export const TradeHistory = ({ userId, refreshTrigger = 0 }: TradeHistoryProps) => {
  const [trades, setTrades] = useState<PaperTrade[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [filterSymbol, setFilterSymbol] = useState<string>("all");
  const [limit, setLimit] = useState(20);

  useEffect(() => {
    loadTrades();
  }, [userId, filterSymbol, limit, refreshTrigger]);

  const loadTrades = async () => {
    try {
      setIsLoading(true);
      const data = await api.getPaperTrades(
        userId,
        limit,
        filterSymbol === "all" ? undefined : filterSymbol
      );
      setTrades(data.trades);
    } catch (error) {
      console.error("Failed to load trades:", error);
      toast.error("Failed to load trade history");
    } finally {
      setIsLoading(false);
    }
  };

  const uniqueSymbols = Array.from(new Set(trades.map((t) => t.symbol))).sort();

  if (isLoading && trades.length === 0) {
    return (
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <History className="w-5 h-5" />
            Trade History
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex items-center justify-center py-12">
            <div className="w-8 h-8 border-2 border-primary border-t-transparent rounded-full animate-spin" />
          </div>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card>
      <CardHeader>
        <div className="flex items-center justify-between">
          <CardTitle className="flex items-center gap-2">
            <History className="w-5 h-5" />
            Trade History
          </CardTitle>
          <div className="flex items-center gap-2">
            <Select value={filterSymbol} onValueChange={setFilterSymbol}>
              <SelectTrigger className="w-32">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">All Symbols</SelectItem>
                {uniqueSymbols.map((symbol) => (
                  <SelectItem key={symbol} value={symbol}>
                    {symbol}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>

            <Select value={limit.toString()} onValueChange={(v) => setLimit(Number(v))}>
              <SelectTrigger className="w-24">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="10">Last 10</SelectItem>
                <SelectItem value="20">Last 20</SelectItem>
                <SelectItem value="50">Last 50</SelectItem>
                <SelectItem value="100">Last 100</SelectItem>
              </SelectContent>
            </Select>

            <Button
              variant="outline"
              size="icon"
              onClick={loadTrades}
              disabled={isLoading}
            >
              <RefreshCw className={`w-4 h-4 ${isLoading ? "animate-spin" : ""}`} />
            </Button>
          </div>
        </div>
      </CardHeader>
      <CardContent>
        {trades.length > 0 ? (
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="border-b text-left text-sm text-muted-foreground">
                  <th className="pb-3 font-medium">Date & Time</th>
                  <th className="pb-3 font-medium">Symbol</th>
                  <th className="pb-3 font-medium">Type</th>
                  <th className="pb-3 font-medium">Quantity</th>
                  <th className="pb-3 font-medium">Price</th>
                  <th className="pb-3 font-medium">Total Amount</th>
                  <th className="pb-3 font-medium">Status</th>
                </tr>
              </thead>
              <tbody>
                {trades.map((trade) => {
                  const isBuy = trade.order_type === "buy";
                  const typeColor = isBuy ? "text-green-500" : "text-red-500";
                  const typeBg = isBuy ? "bg-green-500/10" : "bg-red-500/10";
                  const TypeIcon = isBuy ? TrendingUp : TrendingDown;
                  const statusColor =
                    trade.status === "executed"
                      ? "text-green-500 bg-green-500/10"
                      : trade.status === "pending"
                      ? "text-yellow-500 bg-yellow-500/10"
                      : "text-red-500 bg-red-500/10";

                  return (
                    <tr key={trade.id} className="border-b last:border-0">
                      <td className="py-3 text-sm">
                        {new Date(trade.timestamp).toLocaleString("en-US", {
                          month: "short",
                          day: "numeric",
                          year: "numeric",
                          hour: "2-digit",
                          minute: "2-digit",
                        })}
                      </td>
                      <td className="py-3 font-medium">{trade.symbol}</td>
                      <td className="py-3">
                        <span
                          className={`inline-flex items-center gap-1 px-2 py-1 rounded text-xs font-medium ${typeBg} ${typeColor}`}
                        >
                          <TypeIcon className="w-3 h-3" />
                          {trade.order_type.toUpperCase()}
                        </span>
                      </td>
                      <td className="py-3">{trade.quantity}</td>
                      <td className="py-3">${trade.price.toFixed(2)}</td>
                      <td className="py-3 font-medium">
                        ${trade.total_amount.toLocaleString(undefined, {
                          minimumFractionDigits: 2,
                          maximumFractionDigits: 2,
                        })}
                      </td>
                      <td className="py-3">
                        <span
                          className={`inline-flex px-2 py-1 rounded text-xs font-medium ${statusColor}`}
                        >
                          {trade.status.charAt(0).toUpperCase() + trade.status.slice(1)}
                        </span>
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>

            <div className="mt-4 text-sm text-muted-foreground text-center">
              Showing {trades.length} trade{trades.length !== 1 ? "s" : ""}
              {filterSymbol !== "all" && ` for ${filterSymbol}`}
            </div>
          </div>
        ) : (
          <div className="text-center py-12 text-muted-foreground">
            <History className="w-12 h-12 mx-auto mb-4 opacity-50" />
            <p>No trades yet</p>
            <p className="text-sm">Your trade history will appear here</p>
          </div>
        )}
      </CardContent>
    </Card>
  );
};
