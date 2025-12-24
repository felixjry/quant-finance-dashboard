import { Link } from "react-router-dom";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { BarChart3, PieChart, TrendingUp, Activity, ArrowRight, ArrowUp, ArrowDown, RefreshCw } from "lucide-react";
import { useMarketOverview, useHealthCheck } from "@/hooks/useFinancialData";

const Index = () => {
  const { data: marketData, isLoading: marketLoading, refetch } = useMarketOverview();
  const { data: healthData } = useHealthCheck();

  const features = [
    {
      icon: BarChart3,
      title: "Single Asset Analysis",
      description: "Analyze individual assets with multiple backtesting strategies including Buy-and-Hold, Momentum, and Mean Reversion.",
      link: "/single-asset",
      color: "text-blue-500",
    },
    {
      icon: PieChart,
      title: "Portfolio Analysis",
      description: "Simulate multi-asset portfolios with correlation analysis, diversification metrics, and multiple weighting strategies.",
      link: "/portfolio",
      color: "text-green-500",
    },
  ];

  const stats = [
    { label: "Assets Available", value: "15+", icon: TrendingUp },
    { label: "Strategies", value: "4", icon: Activity },
    { label: "Update Frequency", value: "5 min", icon: BarChart3 },
  ];

  return (
    <div className="min-h-screen bg-background">
      <div className="max-w-7xl mx-auto px-6 py-16">
        <div className="text-center mb-16">
          <h1 className="text-5xl font-bold mb-6 text-foreground">
            Quantitative Financial Dashboard
          </h1>
          <p className="text-xl text-muted-foreground max-w-3xl mx-auto mb-8">
            Professional-grade financial analysis tools for single assets and multi-asset portfolios.
            Real-time data updates with advanced backtesting strategies.
          </p>

          <div className="flex justify-center gap-8 mb-12">
            {stats.map((stat) => (
              <div key={stat.label} className="text-center">
                <div className="flex items-center justify-center mb-2">
                  <stat.icon className="w-5 h-5 text-primary mr-2" />
                  <span className="text-3xl font-bold text-foreground">{stat.value}</span>
                </div>
                <p className="text-sm text-muted-foreground">{stat.label}</p>
              </div>
            ))}
          </div>

          {healthData && (
            <div className="inline-flex items-center gap-2 px-3 py-1 bg-green-500/10 text-green-500 rounded-full text-sm mb-8">
              <span className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></span>
              API Connected
            </div>
          )}
        </div>

        {marketData && marketData.assets && marketData.assets.length > 0 && (
          <Card className="bg-card border-border mb-8">
            <CardHeader className="flex flex-row items-center justify-between">
              <div>
                <CardTitle>Market Overview</CardTitle>
                <CardDescription>Real-time prices from major indices and assets</CardDescription>
              </div>
              <Button
                variant="outline"
                size="sm"
                onClick={() => refetch()}
                disabled={marketLoading}
              >
                <RefreshCw className={`w-4 h-4 mr-2 ${marketLoading ? 'animate-spin' : ''}`} />
                Refresh
              </Button>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
                {marketData.assets.map((asset) => (
                  <div key={asset.symbol} className="p-4 bg-muted/50 rounded-lg">
                    <p className="text-sm text-muted-foreground mb-1">{asset.name || asset.symbol}</p>
                    <p className="text-xl font-bold">
                      {asset.currency === 'USD' ? '$' : ''}{asset.price.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
                    </p>
                    <div className={`flex items-center gap-1 text-sm ${asset.change >= 0 ? 'text-green-500' : 'text-red-500'}`}>
                      {asset.change >= 0 ? <ArrowUp className="w-3 h-3" /> : <ArrowDown className="w-3 h-3" />}
                      {asset.change >= 0 ? '+' : ''}{asset.change_percent.toFixed(2)}%
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        )}

        <div className="grid md:grid-cols-2 gap-6 mb-12">
          {features.map((feature) => (
            <Card key={feature.title} className="bg-card border-border hover:shadow-lg transition-shadow">
              <CardHeader>
                <div className="flex items-center gap-3 mb-2">
                  <feature.icon className={`w-8 h-8 ${feature.color}`} />
                  <CardTitle className="text-2xl">{feature.title}</CardTitle>
                </div>
                <CardDescription className="text-base">{feature.description}</CardDescription>
              </CardHeader>
              <CardContent>
                <Link to={feature.link}>
                  <Button className="w-full group">
                    Get Started
                    <ArrowRight className="w-4 h-4 ml-2 group-hover:translate-x-1 transition-transform" />
                  </Button>
                </Link>
              </CardContent>
            </Card>
          ))}
        </div>

        <Card className="bg-card border-border">
          <CardHeader>
            <CardTitle>Key Features</CardTitle>
            <CardDescription>Everything you need for professional quantitative analysis</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="grid md:grid-cols-2 gap-6">
              <div>
                <h3 className="font-semibold mb-2 text-foreground">Real-Time Data</h3>
                <p className="text-sm text-muted-foreground">
                  Live market data from Yahoo Finance with automatic refresh every 5 minutes
                </p>
              </div>
              <div>
                <h3 className="font-semibold mb-2 text-foreground">Multiple Strategies</h3>
                <p className="text-sm text-muted-foreground">
                  Compare Buy-and-Hold, Momentum, Mean Reversion, and MA Crossover strategies
                </p>
              </div>
              <div>
                <h3 className="font-semibold mb-2 text-foreground">Advanced Metrics</h3>
                <p className="text-sm text-muted-foreground">
                  Sharpe Ratio, Sortino Ratio, Max Drawdown, VaR, and more
                </p>
              </div>
              <div>
                <h3 className="font-semibold mb-2 text-foreground">Portfolio Optimization</h3>
                <p className="text-sm text-muted-foreground">
                  Equal Weight, Risk Parity, Min Variance, and Max Sharpe optimization
                </p>
              </div>
              <div>
                <h3 className="font-semibold mb-2 text-foreground">Correlation Analysis</h3>
                <p className="text-sm text-muted-foreground">
                  Visual correlation matrix for portfolio diversification insights
                </p>
              </div>
              <div>
                <h3 className="font-semibold mb-2 text-foreground">Daily Reports</h3>
                <p className="text-sm text-muted-foreground">
                  Automated daily reports generated at 8 PM via cron job
                </p>
              </div>
            </div>
          </CardContent>
        </Card>

        <div className="mt-8 text-center text-sm text-muted-foreground">
          <p>Data provided by Yahoo Finance. Updates every 5 minutes.</p>
        </div>
      </div>
    </div>
  );
};

export default Index;
