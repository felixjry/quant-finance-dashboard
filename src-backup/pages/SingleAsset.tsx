import { useState, useEffect } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Label } from "@/components/ui/label";
import { Slider } from "@/components/ui/slider";
import { AssetChart } from "@/components/AssetChart";
import { PredictionChart } from "@/components/PredictionChart";
import { MetricsCard } from "@/components/MetricsCard";
import { ArrowUp, ArrowDown, TrendingUp, RefreshCw, AlertCircle, LineChart } from "lucide-react";
import { useCurrentPrice, useStrategy, useAssetHistory, usePrediction } from "@/hooks/useFinancialData";
import { Alert, AlertDescription } from "@/components/ui/alert";

const ASSETS = [
  { value: "AAPL", label: "Apple Inc." },
  { value: "MSFT", label: "Microsoft" },
  { value: "GOOGL", label: "Alphabet" },
  { value: "TSLA", label: "Tesla" },
  { value: "AMZN", label: "Amazon" },
  { value: "NVDA", label: "NVIDIA" },
  { value: "META", label: "Meta" },
  { value: "JPM", label: "JPMorgan" },
  { value: "SPY", label: "S&P 500 ETF" },
  { value: "QQQ", label: "Nasdaq ETF" },
  { value: "BTC-USD", label: "Bitcoin" },
  { value: "ETH-USD", label: "Ethereum" },
  { value: "EURUSD=X", label: "EUR/USD" },
  { value: "ENGI.PA", label: "Engie (Paris)" },
  { value: "TTE.PA", label: "TotalEnergies" },
];

const STRATEGIES = [
  { value: "buy_and_hold", label: "Buy and Hold" },
  { value: "momentum", label: "Momentum" },
  { value: "mean_reversion", label: "Mean Reversion" },
  { value: "ma_crossover", label: "MA Crossover" },
];

const SingleAsset = () => {
  const [selectedAsset, setSelectedAsset] = useState("AAPL");
  const [strategy, setStrategy] = useState("buy_and_hold");
  const [lookbackPeriod, setLookbackPeriod] = useState(20);
  const [periodicity, setPeriodicity] = useState("daily");
  const [forecastDays, setForecastDays] = useState(30);
  const [lastUpdated, setLastUpdated] = useState<Date>(new Date());

  const {
    data: priceData,
    isLoading: priceLoading,
    error: priceError,
    refetch: refetchPrice
  } = useCurrentPrice(selectedAsset);

  const {
    data: strategyData,
    isLoading: strategyLoading,
    error: strategyError,
    refetch: refetchStrategy
  } = useStrategy(selectedAsset, strategy, "1y", {
    interval: periodicity,
    lookback_period: lookbackPeriod,
    short_window: Math.min(lookbackPeriod, 20),
    long_window: Math.max(lookbackPeriod, 50),
  });

  const {
    data: historyData,
    isLoading: historyLoading,
  } = useAssetHistory(selectedAsset, "1y", "daily");

  const {
    data: predictionData,
    isLoading: predictionLoading,
    error: predictionError,
  } = usePrediction(selectedAsset, "1y", forecastDays);

  useEffect(() => {
    setLastUpdated(new Date());
  }, [priceData, strategyData]);

  useEffect(() => {
    const interval = setInterval(() => {
      refetchPrice();
      refetchStrategy();
    }, 5 * 60 * 1000);

    return () => clearInterval(interval);
  }, [refetchPrice, refetchStrategy]);

  const currentPrice = priceData?.price ?? 0;
  const priceChange = priceData?.change ?? 0;
  const priceChangePercent = priceData?.change_percent ?? 0;
  const assetName = priceData?.name ?? selectedAsset;

  const metrics = strategyData ? [
    {
      label: "Max Drawdown",
      value: `-${strategyData.metrics.max_drawdown}%`,
      trend: "down" as const
    },
    {
      label: "Sharpe Ratio",
      value: strategyData.metrics.sharpe_ratio.toFixed(2),
      trend: strategyData.metrics.sharpe_ratio > 1 ? "up" as const : "neutral" as const
    },
    {
      label: "Total Return",
      value: `${strategyData.metrics.total_return > 0 ? '+' : ''}${strategyData.metrics.total_return}%`,
      trend: strategyData.metrics.total_return > 0 ? "up" as const : "down" as const
    },
    {
      label: "Volatility",
      value: `${strategyData.metrics.volatility}%`,
      trend: "neutral" as const
    },
  ] : [
    { label: "Max Drawdown", value: "-", trend: "neutral" as const },
    { label: "Sharpe Ratio", value: "-", trend: "neutral" as const },
    { label: "Total Return", value: "-", trend: "neutral" as const },
    { label: "Volatility", value: "-", trend: "neutral" as const },
  ];

  const isLoading = priceLoading || strategyLoading;
  const hasError = priceError || strategyError;

  return (
    <div className="flex h-screen bg-background">
      <aside className="w-80 border-r border-border bg-card p-6 overflow-y-auto">
        <h2 className="text-2xl font-bold mb-6 text-foreground">Analysis Controls</h2>

        <div className="space-y-6">
          <div>
            <Label htmlFor="asset" className="text-sm font-medium mb-2 block">
              Select Asset
            </Label>
            <Select value={selectedAsset} onValueChange={setSelectedAsset}>
              <SelectTrigger id="asset">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                {ASSETS.map((asset) => (
                  <SelectItem key={asset.value} value={asset.value}>
                    {asset.label} ({asset.value})
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>

          <div>
            <Label htmlFor="strategy" className="text-sm font-medium mb-2 block">
              Backtesting Strategy
            </Label>
            <Select value={strategy} onValueChange={setStrategy}>
              <SelectTrigger id="strategy">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                {STRATEGIES.map((s) => (
                  <SelectItem key={s.value} value={s.value}>
                    {s.label}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>

          <div>
            <Label htmlFor="period" className="text-sm font-medium mb-2 block">
              Lookback Period: {lookbackPeriod} days
            </Label>
            <Slider
              id="period"
              min={5}
              max={200}
              step={5}
              value={[lookbackPeriod]}
              onValueChange={(value) => setLookbackPeriod(value[0])}
              className="mt-2"
            />
          </div>

          <div>
            <Label htmlFor="periodicity" className="text-sm font-medium mb-2 block">
              Periodicity
            </Label>
            <Select value={periodicity} onValueChange={setPeriodicity}>
              <SelectTrigger id="periodicity">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="daily">Daily</SelectItem>
                <SelectItem value="weekly">Weekly</SelectItem>
                <SelectItem value="monthly">Monthly</SelectItem>
              </SelectContent>
            </Select>
          </div>

          <div>
            <Label htmlFor="forecast" className="text-sm font-medium mb-2 block">
              Forecast Period: {forecastDays} days
            </Label>
            <Slider
              id="forecast"
              min={7}
              max={90}
              step={1}
              value={[forecastDays]}
              onValueChange={(value) => setForecastDays(value[0])}
              className="mt-2"
            />
          </div>
        </div>

        <div className="mt-8 p-4 bg-muted rounded-lg">
          <div className="flex items-center gap-2">
            {isLoading && <RefreshCw className="w-3 h-3 animate-spin" />}
            <p className="text-xs text-muted-foreground">
              Last updated: {lastUpdated.toLocaleTimeString()}
            </p>
          </div>
          <p className="text-xs text-muted-foreground mt-1">
            Auto-refresh: Every 5 minutes
          </p>
        </div>
      </aside>

      <main className="flex-1 overflow-y-auto p-8">
        <div className="max-w-7xl mx-auto space-y-6">
          {hasError && (
            <Alert variant="destructive">
              <AlertCircle className="h-4 w-4" />
              <AlertDescription>
                Error loading data. Using cached values if available.
              </AlertDescription>
            </Alert>
          )}

          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold text-foreground">{assetName}</h1>
              <p className="text-muted-foreground">Single Asset Analysis - {selectedAsset}</p>
            </div>
          </div>

          <Card className="bg-card border-border">
            <CardContent className="pt-6">
              <div className="flex items-baseline gap-4">
                <div className="text-4xl font-bold text-foreground">
                  {priceLoading ? (
                    <span className="animate-pulse">Loading...</span>
                  ) : (
                    `${priceData?.currency === 'USD' ? '$' : ''}${currentPrice.toFixed(2)}`
                  )}
                </div>
                {!priceLoading && (
                  <div className={`flex items-center gap-1 text-lg font-semibold ${priceChange >= 0 ? 'text-green-500' : 'text-red-500'}`}>
                    {priceChange >= 0 ? <ArrowUp className="w-5 h-5" /> : <ArrowDown className="w-5 h-5" />}
                    {priceChange >= 0 ? '+' : ''}{priceChange.toFixed(2)} ({priceChangePercent >= 0 ? '+' : ''}{priceChangePercent.toFixed(2)}%)
                  </div>
                )}
              </div>
              <p className="text-sm text-muted-foreground mt-2">Current Price</p>
            </CardContent>
          </Card>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            {metrics.map((metric) => (
              <MetricsCard key={metric.label} {...metric} />
            ))}
          </div>

          <Card className="bg-card border-border">
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <TrendingUp className="w-5 h-5" />
                Price & Strategy Performance
                {strategyData && (
                  <span className="text-sm font-normal text-muted-foreground ml-2">
                    ({strategyData.strategy})
                  </span>
                )}
              </CardTitle>
            </CardHeader>
            <CardContent>
              <AssetChart
                strategy={strategy}
                period={lookbackPeriod}
                asset={selectedAsset}
                chartData={strategyData?.chart_data}
                isLoading={strategyLoading}
              />
            </CardContent>
          </Card>

          {strategyData && (
            <Card className="bg-card border-border">
              <CardHeader>
                <CardTitle>Strategy Details</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
                  <div>
                    <p className="text-muted-foreground">Win Rate</p>
                    <p className="font-semibold">{strategyData.metrics.win_rate}%</p>
                  </div>
                  <div>
                    <p className="text-muted-foreground">Number of Trades</p>
                    <p className="font-semibold">{strategyData.metrics.num_trades}</p>
                  </div>
                  <div>
                    <p className="text-muted-foreground">Annualized Return</p>
                    <p className="font-semibold">{strategyData.metrics.annualized_return}%</p>
                  </div>
                  <div>
                    <p className="text-muted-foreground">Strategy</p>
                    <p className="font-semibold">{strategyData.strategy}</p>
                  </div>
                </div>
              </CardContent>
            </Card>
          )}

          <Card className="bg-card border-border">
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <LineChart className="w-5 h-5" />
                Price Prediction (Prophet)
                {predictionData && (
                  <span className="text-sm font-normal text-muted-foreground ml-2">
                    ({forecastDays} days forecast)
                  </span>
                )}
              </CardTitle>
            </CardHeader>
            <CardContent>
              {predictionError && (
                <Alert variant="destructive" className="mb-4">
                  <AlertCircle className="h-4 w-4" />
                  <AlertDescription>
                    Erreur lors du chargement des prédictions. Vérifiez que l'actif a suffisamment de données historiques.
                  </AlertDescription>
                </Alert>
              )}
              <PredictionChart
                symbol={selectedAsset}
                historicalData={historyData?.data}
                predictionData={predictionData?.prediction.forecast}
                isLoading={predictionLoading || historyLoading}
              />
              {predictionData && (
                <div className="mt-4 grid grid-cols-2 md:grid-cols-5 gap-4 text-sm border-t border-border pt-4">
                  <div>
                    <p className="text-muted-foreground">MAE</p>
                    <p className="font-semibold">${predictionData.prediction.metrics.mae}</p>
                  </div>
                  <div>
                    <p className="text-muted-foreground">MAPE</p>
                    <p className="font-semibold">{predictionData.prediction.metrics.mape}%</p>
                  </div>
                  <div>
                    <p className="text-muted-foreground">RMSE</p>
                    <p className="font-semibold">${predictionData.prediction.metrics.rmse}</p>
                  </div>
                  <div>
                    <p className="text-muted-foreground">R² Score</p>
                    <p className="font-semibold">{predictionData.prediction.metrics.r2_score}</p>
                  </div>
                  <div>
                    <p className="text-muted-foreground">Model</p>
                    <p className="font-semibold">{predictionData.prediction.model}</p>
                  </div>
                </div>
              )}
            </CardContent>
          </Card>
        </div>
      </main>
    </div>
  );
};

export default SingleAsset;
