import { useState, useEffect } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Label } from "@/components/ui/label";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { PortfolioChart } from "@/components/PortfolioChart";
import { CorrelationMatrix } from "@/components/CorrelationMatrix";
import { MetricsCard } from "@/components/MetricsCard";
import { RiskReturnProfile } from "@/components/RiskReturnProfile";
import { PieChart, TrendingUp, RefreshCw, AlertCircle, X, Target } from "lucide-react";
import { usePortfolioAnalysis } from "@/hooks/useFinancialData";
import { Alert, AlertDescription } from "@/components/ui/alert";

const AVAILABLE_ASSETS = [
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
  { value: "ENGI.PA", label: "Engie (Paris)" },
  { value: "TTE.PA", label: "TotalEnergies" },
];

const WEIGHTING_OPTIONS = [
  { value: "equal_weight", label: "Equal Weights" },
  { value: "risk_parity", label: "Risk Parity" },
  { value: "min_variance", label: "Minimum Variance" },
  { value: "max_sharpe", label: "Max Sharpe Ratio" },
];

const REBALANCE_OPTIONS = [
  { value: "daily", label: "Daily" },
  { value: "weekly", label: "Weekly" },
  { value: "monthly", label: "Monthly" },
  { value: "quarterly", label: "Quarterly" },
];

const Portfolio = () => {
  const [selectedAssets, setSelectedAssets] = useState(["AAPL", "MSFT", "GOOGL"]);
  const [weighting, setWeighting] = useState("equal_weight");
  const [rebalanceFrequency, setRebalanceFrequency] = useState("monthly");
  const [lastUpdated, setLastUpdated] = useState<Date>(new Date());

  const {
    data: portfolioData,
    isLoading,
    error,
    refetch
  } = usePortfolioAnalysis(selectedAssets, weighting, rebalanceFrequency);

  useEffect(() => {
    if (portfolioData) {
      setLastUpdated(new Date());
    }
  }, [portfolioData]);

  useEffect(() => {
    const interval = setInterval(() => {
      refetch();
    }, 5 * 60 * 1000);

    return () => clearInterval(interval);
  }, [refetch]);

  const addAsset = (asset: string) => {
    if (!selectedAssets.includes(asset) && selectedAssets.length < 10) {
      setSelectedAssets([...selectedAssets, asset]);
    }
  };

  const removeAsset = (asset: string) => {
    if (selectedAssets.length > 2) {
      setSelectedAssets(selectedAssets.filter(a => a !== asset));
    }
  };

  const portfolioMetrics = portfolioData ? [
    {
      label: "Portfolio Return",
      value: `${portfolioData.metrics.total_return > 0 ? '+' : ''}${portfolioData.metrics.total_return.toFixed(2)}%`,
      trend: portfolioData.metrics.total_return > 0 ? "up" as const : "down" as const
    },
    {
      label: "Portfolio Volatility",
      value: `${portfolioData.metrics.volatility.toFixed(2)}%`,
      trend: "neutral" as const
    },
    {
      label: "Sharpe Ratio",
      value: portfolioData.metrics.sharpe_ratio.toFixed(2),
      trend: portfolioData.metrics.sharpe_ratio > 1 ? "up" as const : "neutral" as const
    },
    {
      label: "Diversification Ratio",
      value: portfolioData.metrics.diversification_ratio.toFixed(2),
      trend: portfolioData.metrics.diversification_ratio > 1 ? "up" as const : "neutral" as const
    },
  ] : [
    { label: "Portfolio Return", value: "-", trend: "neutral" as const },
    { label: "Portfolio Volatility", value: "-", trend: "neutral" as const },
    { label: "Sharpe Ratio", value: "-", trend: "neutral" as const },
    { label: "Diversification Ratio", value: "-", trend: "neutral" as const },
  ];

  return (
    <div className="flex h-screen bg-background">
      <aside className="w-80 border-r border-border bg-card p-6 overflow-y-auto">
        <h2 className="text-2xl font-bold mb-6 text-foreground">Portfolio Controls</h2>

        <div className="space-y-6">
          <div>
            <Label className="text-sm font-medium mb-2 block">
              Selected Assets ({selectedAssets.length}/10)
            </Label>
            <div className="flex flex-wrap gap-2 mb-3">
              {selectedAssets.map((asset) => (
                <Badge key={asset} variant="secondary" className="text-xs flex items-center gap-1">
                  {asset}
                  {selectedAssets.length > 2 && (
                    <button
                      onClick={() => removeAsset(asset)}
                      className="ml-1 hover:text-destructive"
                    >
                      <X className="w-3 h-3" />
                    </button>
                  )}
                </Badge>
              ))}
            </div>
            <Select
              value=""
              onValueChange={addAsset}
            >
              <SelectTrigger>
                <SelectValue placeholder="Add asset..." />
              </SelectTrigger>
              <SelectContent>
                {AVAILABLE_ASSETS.filter(a => !selectedAssets.includes(a.value)).map((asset) => (
                  <SelectItem key={asset.value} value={asset.value}>
                    {asset.label} ({asset.value})
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>

          <div>
            <Label htmlFor="weighting" className="text-sm font-medium mb-2 block">
              Weighting Strategy
            </Label>
            <Select value={weighting} onValueChange={setWeighting}>
              <SelectTrigger id="weighting">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                {WEIGHTING_OPTIONS.map((option) => (
                  <SelectItem key={option.value} value={option.value}>
                    {option.label}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>

          <div>
            <Label htmlFor="rebalance" className="text-sm font-medium mb-2 block">
              Rebalancing Frequency
            </Label>
            <Select value={rebalanceFrequency} onValueChange={setRebalanceFrequency}>
              <SelectTrigger id="rebalance">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                {REBALANCE_OPTIONS.map((option) => (
                  <SelectItem key={option.value} value={option.value}>
                    {option.label}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>

          {portfolioData?.weights && (
            <div>
              <Label className="text-sm font-medium mb-2 block">
                Portfolio Weights
              </Label>
              <div className="space-y-2">
                {Object.entries(portfolioData.weights).map(([asset, weight]) => (
                  <div key={asset} className="flex justify-between text-sm">
                    <span className="text-muted-foreground">{asset}</span>
                    <span className="font-medium">{(weight * 100).toFixed(1)}%</span>
                  </div>
                ))}
              </div>
            </div>
          )}
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
          <Button
            variant="outline"
            size="sm"
            className="mt-2 w-full"
            onClick={() => refetch()}
            disabled={isLoading}
          >
            <RefreshCw className={`w-3 h-3 mr-2 ${isLoading ? 'animate-spin' : ''}`} />
            Refresh Now
          </Button>
        </div>
      </aside>

      <main className="flex-1 overflow-y-auto p-8">
        <div className="max-w-7xl mx-auto space-y-6">
          {error && (
            <Alert variant="destructive">
              <AlertCircle className="h-4 w-4" />
              <AlertDescription>
                Error loading portfolio data. Please try again.
              </AlertDescription>
            </Alert>
          )}

          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold text-foreground flex items-center gap-2">
                <PieChart className="w-8 h-8" />
                Portfolio Analysis
              </h1>
              <p className="text-muted-foreground">
                {selectedAssets.length} assets • {WEIGHTING_OPTIONS.find(w => w.value === weighting)?.label} • {REBALANCE_OPTIONS.find(r => r.value === rebalanceFrequency)?.label} rebalancing
              </p>
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            {portfolioMetrics.map((metric) => (
              <MetricsCard key={metric.label} {...metric} />
            ))}
          </div>

          <Card className="bg-card border-border">
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <TrendingUp className="w-5 h-5" />
                Portfolio Performance
              </CardTitle>
            </CardHeader>
            <CardContent>
              <PortfolioChart
                assets={selectedAssets}
                simulationType={weighting}
                chartData={portfolioData?.chart_data}
                isLoading={isLoading}
              />
            </CardContent>
          </Card>

          <Card className="bg-card border-border">
            <CardHeader>
              <CardTitle>Asset Correlation Matrix</CardTitle>
            </CardHeader>
            <CardContent>
              <CorrelationMatrix
                assets={selectedAssets}
                correlationData={portfolioData?.correlation_matrix}
                isLoading={isLoading}
              />
            </CardContent>
          </Card>

          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {portfolioData?.individual_metrics && (
              <Card className="bg-card border-border">
                <CardHeader>
                  <CardTitle>Individual Asset Performance</CardTitle>
                  <p className="text-sm text-muted-foreground mt-1">
                    From June 11, 2024 to today
                  </p>
                </CardHeader>
                <CardContent>
                  <div className="overflow-x-auto">
                    <table className="w-full text-sm">
                      <thead>
                        <tr className="border-b">
                          <th className="text-left py-2 px-4">Asset</th>
                          <th className="text-right py-2 px-4">Return</th>
                          <th className="text-right py-2 px-4">Volatility</th>
                          <th className="text-right py-2 px-4">Sharpe</th>
                          <th className="text-right py-2 px-4">Max DD</th>
                        </tr>
                      </thead>
                      <tbody>
                        {Object.entries(portfolioData.individual_metrics).map(([asset, metrics]) => (
                          <tr key={asset} className="border-b hover:bg-muted/50">
                            <td className="py-2 px-4 font-medium">{asset}</td>
                            <td className={`text-right py-2 px-4 ${metrics.total_return > 0 ? 'text-green-500' : 'text-red-500'}`}>
                              {metrics.total_return > 0 ? '+' : ''}{metrics.total_return}%
                            </td>
                            <td className="text-right py-2 px-4">{metrics.volatility}%</td>
                            <td className="text-right py-2 px-4">{metrics.sharpe_ratio.toFixed(2)}</td>
                            <td className="text-right py-2 px-4 text-red-500">-{metrics.max_drawdown}%</td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                </CardContent>
              </Card>
            )}

            {portfolioData?.metrics && (
              <Card className="bg-card border-border">
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <Target className="w-5 h-5" />
                    Risk-Return Profile
                  </CardTitle>
                  <p className="text-sm text-muted-foreground mt-1">
                    Portfolio performance vs market benchmark
                  </p>
                  <p className="text-sm text-muted-foreground">
                    From June 11, 2024 to today
                  </p>
                </CardHeader>
                <CardContent>
                  <RiskReturnProfile
                    portfolioMetrics={portfolioData.metrics}
                    isLoading={isLoading}
                  />
                </CardContent>
              </Card>
            )}
          </div>
        </div>
      </main>
    </div>
  );
};

export default Portfolio;
