import { useState, useEffect } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from "@/components/ui/dialog";
import { Label } from "@/components/ui/label";
import { TrendingUp, TrendingDown, Wallet, LineChart, Activity, AlertCircle } from "lucide-react";
import { api, PaperPortfolio, TradingSignal } from "@/services/api";
import { toast } from "sonner";
import { TradeHistory } from "@/components/TradeHistory";

const DEFAULT_USER_ID = "demo_user";

export default function PaperTrading() {
  const [portfolio, setPortfolio] = useState<PaperPortfolio | null>(null);
  const [signals, setSignals] = useState<TradingSignal[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [selectedSymbol, setSelectedSymbol] = useState("AAPL");
  const [quantity, setQuantity] = useState(10);
  const [isTradeDialogOpen, setIsTradeDialogOpen] = useState(false);
  const [tradeType, setTradeType] = useState<"buy" | "sell">("buy");
  const [refreshTrigger, setRefreshTrigger] = useState(0);

  const SYMBOLS = ["AAPL", "MSFT", "GOOGL", "AMZN", "NVDA", "TSLA", "META", "SPY", "QQQ"];

  useEffect(() => {
    initializeUser();
  }, []);

  const initializeUser = async () => {
    try {
      setIsLoading(true);

      // Try to get user, create if doesn't exist
      try {
        await api.getPaperTradingUser(DEFAULT_USER_ID);
      } catch (error) {
        // User doesn't exist, create one
        await api.createPaperTradingUser(DEFAULT_USER_ID, 1000000);
        toast.success("Paper Trading Account Created!", {
          description: "Starting balance: $1,000,000"
        });
      }

      // Load portfolio and signals
      await Promise.all([
        loadPortfolio(),
        loadSignals()
      ]);
    } catch (error) {
      console.error("Failed to initialize user:", error);
      toast.error("Failed to initialize account");
    } finally {
      setIsLoading(false);
    }
  };

  const loadPortfolio = async () => {
    try {
      const data = await api.getPaperPortfolio(DEFAULT_USER_ID);
      setPortfolio(data);
    } catch (error) {
      console.error("Failed to load portfolio:", error);
    }
  };

  const loadSignals = async () => {
    try {
      const data = await api.getActiveSignals(undefined, 10);
      setSignals(data.signals);
    } catch (error) {
      console.error("Failed to load signals:", error);
    }
  };

  const detectSignals = async () => {
    try {
      toast.info("Scanning for trading signals...");
      const data = await api.getTradingSignals(selectedSymbol);

      if (data.signals_count > 0) {
        toast.success(`Found ${data.signals_count} signal(s) for ${selectedSymbol}`);
        await loadSignals();
      } else {
        toast.info(`No active signals for ${selectedSymbol}`);
      }
    } catch (error) {
      console.error("Failed to detect signals:", error);
      toast.error("Failed to detect signals");
    }
  };

  const executeTrade = async () => {
    if (!selectedSymbol || quantity <= 0) {
      toast.error("Please enter valid trade details");
      return;
    }

    try {
      const result = await api.executePaperTrade(
        DEFAULT_USER_ID,
        selectedSymbol,
        tradeType,
        quantity
      );

      if (result.success) {
        toast.success(result.message, {
          description: `${tradeType === "buy" ? "Bought" : "Sold"} ${quantity} shares at $${result.price.toFixed(2)}`
        });

        // Reload portfolio and trigger trade history refresh
        await loadPortfolio();
        setRefreshTrigger(prev => prev + 1);
        setIsTradeDialogOpen(false);
      }
    } catch (error: any) {
      toast.error(error.message || "Trade failed");
    }
  };

  const openTradeDialog = (type: "buy" | "sell", symbol?: string) => {
    setTradeType(type);
    if (symbol) setSelectedSymbol(symbol);
    setIsTradeDialogOpen(true);
  };

  if (isLoading) {
    return (
      <div className="container mx-auto p-6 flex items-center justify-center min-h-[60vh]">
        <div className="flex flex-col items-center gap-4">
          <div className="w-12 h-12 border-4 border-primary border-t-transparent rounded-full animate-spin" />
          <p className="text-muted-foreground">Loading paper trading account...</p>
        </div>
      </div>
    );
  }

  const totalPnLColor = portfolio && portfolio.total_pnl >= 0 ? "text-green-500" : "text-red-500";
  const totalPnLIcon = portfolio && portfolio.total_pnl >= 0 ? TrendingUp : TrendingDown;
  const TotalPnLIcon = totalPnLIcon;

  return (
    <div className="container mx-auto p-6 space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">Paper Trading</h1>
          <p className="text-muted-foreground mt-1">
            Practice trading with virtual money
          </p>
        </div>
        <Dialog open={isTradeDialogOpen} onOpenChange={setIsTradeDialogOpen}>
          <DialogTrigger asChild>
            <Button size="lg" onClick={() => openTradeDialog("buy")}>
              <Activity className="w-4 h-4 mr-2" />
              New Trade
            </Button>
          </DialogTrigger>
          <DialogContent>
            <DialogHeader>
              <DialogTitle>Execute Trade</DialogTitle>
            </DialogHeader>
            <div className="space-y-4 pt-4">
              <div className="space-y-2">
                <Label>Symbol</Label>
                <Select value={selectedSymbol} onValueChange={setSelectedSymbol}>
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    {SYMBOLS.map((symbol) => (
                      <SelectItem key={symbol} value={symbol}>
                        {symbol}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>

              <div className="space-y-2">
                <Label>Order Type</Label>
                <Select value={tradeType} onValueChange={(v) => setTradeType(v as "buy" | "sell")}>
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="buy">Buy</SelectItem>
                    <SelectItem value="sell">Sell</SelectItem>
                  </SelectContent>
                </Select>
              </div>

              <div className="space-y-2">
                <Label>Quantity</Label>
                <Input
                  type="number"
                  value={quantity}
                  onChange={(e) => setQuantity(Number(e.target.value))}
                  min={1}
                />
              </div>

              <Button onClick={executeTrade} className="w-full" size="lg">
                {tradeType === "buy" ? "Buy" : "Sell"} {quantity} shares of {selectedSymbol}
              </Button>
            </div>
          </DialogContent>
        </Dialog>
      </div>

      {/* Portfolio Summary */}
      {portfolio && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium text-muted-foreground">
                Total Portfolio Value
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">
                ${portfolio.total_value.toLocaleString()}
              </div>
              <div className={`flex items-center gap-1 mt-1 text-sm ${totalPnLColor}`}>
                <TotalPnLIcon className="w-4 h-4" />
                <span>
                  {portfolio.total_pnl >= 0 ? "+" : ""}${Math.abs(portfolio.total_pnl).toLocaleString()} (
                  {portfolio.total_pnl_pct >= 0 ? "+" : ""}{portfolio.total_pnl_pct.toFixed(2)}%)
                </span>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium text-muted-foreground">
                Cash Balance
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">
                ${portfolio.cash_balance.toLocaleString()}
              </div>
              <div className="flex items-center gap-1 mt-1 text-sm text-muted-foreground">
                <Wallet className="w-4 h-4" />
                <span>Available to trade</span>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium text-muted-foreground">
                Total Invested
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">
                ${portfolio.total_invested.toLocaleString()}
              </div>
              <div className="flex items-center gap-1 mt-1 text-sm text-muted-foreground">
                <LineChart className="w-4 h-4" />
                <span>In {portfolio.positions.length} position(s)</span>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium text-muted-foreground">
                Total Trades
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{portfolio.trades_count}</div>
              <div className="flex items-center gap-1 mt-1 text-sm text-muted-foreground">
                <Activity className="w-4 h-4" />
                <span>Executed trades</span>
              </div>
            </CardContent>
          </Card>
        </div>
      )}

      {/* Active Positions */}
      <Card>
        <CardHeader>
          <CardTitle>Active Positions</CardTitle>
        </CardHeader>
        <CardContent>
          {portfolio && portfolio.positions.length > 0 ? (
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead>
                  <tr className="border-b text-left text-sm text-muted-foreground">
                    <th className="pb-3 font-medium">Symbol</th>
                    <th className="pb-3 font-medium">Quantity</th>
                    <th className="pb-3 font-medium">Avg Price</th>
                    <th className="pb-3 font-medium">Current Price</th>
                    <th className="pb-3 font-medium">Total Value</th>
                    <th className="pb-3 font-medium">P&L</th>
                    <th className="pb-3 font-medium">Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {portfolio.positions.map((position) => {
                    const pnlColor = position.unrealized_pnl >= 0 ? "text-green-500" : "text-red-500";
                    return (
                      <tr key={position.symbol} className="border-b last:border-0">
                        <td className="py-3 font-medium">{position.symbol}</td>
                        <td className="py-3">{position.quantity}</td>
                        <td className="py-3">${position.avg_entry_price.toFixed(2)}</td>
                        <td className="py-3">${position.current_price.toFixed(2)}</td>
                        <td className="py-3">${position.total_value.toLocaleString()}</td>
                        <td className={`py-3 ${pnlColor}`}>
                          {position.unrealized_pnl >= 0 ? "+" : ""}${position.unrealized_pnl.toFixed(2)} (
                          {position.unrealized_pnl_pct >= 0 ? "+" : ""}{position.unrealized_pnl_pct.toFixed(2)}%)
                        </td>
                        <td className="py-3">
                          <Button
                            size="sm"
                            variant="outline"
                            onClick={() => openTradeDialog("sell", position.symbol)}
                          >
                            Sell
                          </Button>
                        </td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>
          ) : (
            <div className="text-center py-12 text-muted-foreground">
              <Activity className="w-12 h-12 mx-auto mb-4 opacity-50" />
              <p>No active positions</p>
              <p className="text-sm">Execute your first trade to get started</p>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Trading Signals */}
      <Card>
        <CardHeader className="flex flex-row items-center justify-between">
          <div>
            <CardTitle>Trading Signals</CardTitle>
            <p className="text-sm text-muted-foreground mt-1">Recent signals detected</p>
          </div>
          <Button variant="outline" onClick={detectSignals}>
            <AlertCircle className="w-4 h-4 mr-2" />
            Scan Signals
          </Button>
        </CardHeader>
        <CardContent>
          {signals.length > 0 ? (
            <div className="space-y-3">
              {signals.slice(0, 5).map((signal, idx) => {
                const signalColor =
                  signal.signal_type === "buy" ? "bg-green-500/10 border-green-500" : "bg-red-500/10 border-red-500";
                const signalIcon = signal.signal_type === "buy" ? TrendingUp : TrendingDown;
                const SignalIcon = signalIcon;

                return (
                  <div
                    key={idx}
                    className={`p-4 border rounded-lg ${signalColor}`}
                  >
                    <div className="flex items-start justify-between">
                      <div className="flex items-start gap-3">
                        <SignalIcon className="w-5 h-5 mt-0.5" />
                        <div>
                          <div className="font-semibold">
                            {signal.symbol} - {signal.strategy}
                          </div>
                          <p className="text-sm text-muted-foreground mt-1">{signal.message}</p>
                          <div className="flex items-center gap-3 mt-2 text-xs text-muted-foreground">
                            <span>Price: ${signal.price.toFixed(2)}</span>
                            <span>•</span>
                            <span>Strength: {signal.strength}</span>
                            <span>•</span>
                            <span>{new Date(signal.timestamp).toLocaleString()}</span>
                          </div>
                        </div>
                      </div>
                      <Button
                        size="sm"
                        variant={signal.signal_type === "buy" ? "default" : "destructive"}
                        onClick={() => openTradeDialog(signal.signal_type as "buy" | "sell", signal.symbol)}
                      >
                        {signal.signal_type === "buy" ? "Buy" : "Sell"}
                      </Button>
                    </div>
                  </div>
                );
              })}
            </div>
          ) : (
            <div className="text-center py-12 text-muted-foreground">
              <AlertCircle className="w-12 h-12 mx-auto mb-4 opacity-50" />
              <p>No active signals</p>
              <p className="text-sm">Click "Scan Signals" to detect trading opportunities</p>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Trade History */}
      <TradeHistory userId={DEFAULT_USER_ID} refreshTrigger={refreshTrigger} />
    </div>
  );
}
