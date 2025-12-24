import { RadarChart, PolarGrid, PolarAngleAxis, PolarRadiusAxis, Radar, Legend, ResponsiveContainer, Tooltip } from "recharts";
import { useMemo } from "react";

interface RiskReturnProfileProps {
  portfolioMetrics: {
    total_return: number;
    volatility: number;
    sharpe_ratio: number;
    diversification_ratio: number;
  };
  isLoading?: boolean;
}

export const RiskReturnProfile = ({ portfolioMetrics, isLoading }: RiskReturnProfileProps) => {
  const chartData = useMemo(() => {
    if (!portfolioMetrics) return [];

    const portfolioReturn = portfolioMetrics.total_return;
    const portfolioVolatility = portfolioMetrics.volatility;
    const portfolioSharpe = portfolioMetrics.sharpe_ratio;
    const portfolioDiversification = portfolioMetrics.diversification_ratio;

    const marketReturn = 15;
    const marketVolatility = 18;
    const marketSharpe = 0.75;
    const marketDiversification = 1.0;

    const portfolioRiskAdjusted = portfolioSharpe > 0 ? (portfolioReturn / portfolioVolatility) * 10 : 0;
    const marketRiskAdjusted = (marketReturn / marketVolatility) * 10;

    return [
      {
        metric: 'Returns (%)',
        Portfolio: Math.max(0, portfolioReturn),
        Market: marketReturn,
        portfolioValue: portfolioReturn,
        marketValue: marketReturn,
      },
      {
        metric: 'Low Volatility',
        Portfolio: Math.max(0, 50 - portfolioVolatility),
        Market: 50 - marketVolatility,
        portfolioValue: portfolioVolatility,
        marketValue: marketVolatility,
      },
      {
        metric: 'Sharpe Ratio',
        Portfolio: Math.max(0, portfolioSharpe * 10),
        Market: marketSharpe * 10,
        portfolioValue: portfolioSharpe,
        marketValue: marketSharpe,
      },
      {
        metric: 'Diversification',
        Portfolio: Math.max(0, portfolioDiversification * 10),
        Market: marketDiversification * 10,
        portfolioValue: portfolioDiversification,
        marketValue: marketDiversification,
      },
      {
        metric: 'Risk-Adjusted',
        Portfolio: Math.max(0, portfolioRiskAdjusted),
        Market: marketRiskAdjusted,
        portfolioValue: (portfolioReturn / portfolioVolatility).toFixed(2),
        marketValue: (marketReturn / marketVolatility).toFixed(2),
      },
    ];
  }, [portfolioMetrics]);

  if (isLoading) {
    return (
      <div className="w-full h-[400px] flex items-center justify-center bg-muted/20 rounded-lg">
        <div className="flex flex-col items-center gap-2">
          <div className="w-8 h-8 border-2 border-primary border-t-transparent rounded-full animate-spin" />
          <p className="text-sm text-muted-foreground">Loading risk-return profile...</p>
        </div>
      </div>
    );
  }

  if (!chartData || chartData.length === 0) {
    return (
      <div className="w-full h-[400px] flex items-center justify-center bg-muted/20 rounded-lg">
        <p className="text-sm text-muted-foreground">No data available for risk-return profile</p>
      </div>
    );
  }

  return (
    <ResponsiveContainer width="100%" height={500}>
      <RadarChart data={chartData} cx="50%" cy="50%" outerRadius="75%">
        <PolarGrid stroke="hsl(var(--border))" />
        <PolarAngleAxis
          dataKey="metric"
          tick={{ fill: 'hsl(var(--foreground))', fontSize: 13 }}
        />
        <PolarRadiusAxis
          angle={90}
          domain={[0, 'auto']}
          tick={{ fill: 'hsl(var(--muted-foreground))', fontSize: 11 }}
        />
        <Radar
          name="Portfolio"
          dataKey="Portfolio"
          stroke="#4ade80"
          fill="#4ade80"
          fillOpacity={0.4}
          strokeWidth={2}
        />
        <Radar
          name="Market"
          dataKey="Market"
          stroke="#60a5fa"
          fill="#60a5fa"
          fillOpacity={0.3}
          strokeWidth={2}
        />
        <Tooltip
          contentStyle={{
            backgroundColor: 'hsl(var(--card))',
            border: '1px solid hsl(var(--border))',
            borderRadius: '8px',
          }}
          formatter={(_value: number, name: string, props: any) => {
            const metric = props.payload.metric;
            const realValue = name === 'Portfolio' ? props.payload.portfolioValue : props.payload.marketValue;

            if (metric === 'Returns (%)') {
              return [`${typeof realValue === 'number' ? realValue.toFixed(2) : realValue}%`, name];
            } else if (metric === 'Low Volatility') {
              return [`${typeof realValue === 'number' ? realValue.toFixed(2) : realValue}% vol`, name];
            } else if (metric === 'Sharpe Ratio') {
              return [`${typeof realValue === 'number' ? realValue.toFixed(2) : realValue}`, name];
            } else if (metric === 'Diversification') {
              return [`${typeof realValue === 'number' ? realValue.toFixed(2) : realValue}`, name];
            } else {
              return [`${realValue}`, name];
            }
          }}
        />
        <Legend
          wrapperStyle={{
            paddingTop: '20px',
          }}
        />
      </RadarChart>
    </ResponsiveContainer>
  );
};
