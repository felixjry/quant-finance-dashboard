import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from "recharts";
import { useMemo } from "react";

interface PortfolioChartProps {
  assets: string[];
  simulationType: string;
  chartData?: Array<Record<string, string | number>>;
  isLoading?: boolean;
}

export const PortfolioChart = ({ assets, simulationType, chartData, isLoading }: PortfolioChartProps) => {
  const displayData = useMemo(() => {
    if (chartData && chartData.length > 0) {
      return chartData.map(point => {
        const formattedPoint: Record<string, string | number> = {
          date: point.date as string,
        };

        assets.forEach(asset => {
          if (point[asset] !== undefined) {
            formattedPoint[asset] = Number((Number(point[asset]) * 100).toFixed(2));
          }
        });

        if (point.portfolio !== undefined) {
          formattedPoint.portfolio = Number((Number(point.portfolio) * 100).toFixed(2));
        }

        return formattedPoint;
      });
    }

    const data = [];
    const assetPrices: { [key: string]: number } = {};

    assets.forEach(asset => {
      assetPrices[asset] = 100;
    });

    for (let i = 0; i < 252; i++) {
      const dataPoint: Record<string, string | number> = {
        date: `Day ${i + 1}`,
      };

      assets.forEach(asset => {
        const change = (Math.random() - 0.48) * 2;
        assetPrices[asset] = assetPrices[asset] * (1 + change / 100);
        dataPoint[asset] = parseFloat(assetPrices[asset].toFixed(2));
      });

      const avgReturn = assets.reduce((sum, asset) => sum + assetPrices[asset], 0) / assets.length;
      dataPoint.portfolio = parseFloat(avgReturn.toFixed(2));

      data.push(dataPoint);
    }
    return data;
  }, [chartData, assets]);

  const colors = [
    "hsl(var(--chart-1))",
    "hsl(var(--chart-2))",
    "hsl(var(--chart-3))",
    "hsl(var(--chart-4))",
    "hsl(var(--chart-5))"
  ];

  const formatXAxis = (tickItem: string) => {
    if (tickItem && tickItem.includes('-')) {
      const date = new Date(tickItem);
      return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
    }
    return tickItem;
  };

  if (isLoading) {
    return (
      <div className="w-full h-[400px] flex items-center justify-center bg-muted/20 rounded-lg">
        <div className="flex flex-col items-center gap-2">
          <div className="w-8 h-8 border-2 border-primary border-t-transparent rounded-full animate-spin" />
          <p className="text-sm text-muted-foreground">Loading portfolio data...</p>
        </div>
      </div>
    );
  }

  return (
    <ResponsiveContainer width="100%" height={400}>
      <LineChart data={displayData}>
        <CartesianGrid strokeDasharray="3 3" stroke="hsl(var(--border))" />
        <XAxis
          dataKey="date"
          stroke="hsl(var(--muted-foreground))"
          tick={{ fill: 'hsl(var(--muted-foreground))', fontSize: 12 }}
          tickFormatter={formatXAxis}
          interval="preserveStartEnd"
        />
        <YAxis
          stroke="hsl(var(--muted-foreground))"
          tick={{ fill: 'hsl(var(--muted-foreground))', fontSize: 12 }}
          tickFormatter={(value) => `${value}%`}
          domain={['auto', 'auto']}
        />
        <Tooltip
          contentStyle={{
            backgroundColor: 'hsl(var(--card))',
            border: '1px solid hsl(var(--border))',
            borderRadius: '8px',
          }}
          formatter={(value: number, name: string) => [`${value.toFixed(2)}%`, name]}
          labelFormatter={(label) => {
            if (typeof label === 'string' && label.includes('-')) {
              return new Date(label).toLocaleDateString('en-US', {
                year: 'numeric',
                month: 'long',
                day: 'numeric'
              });
            }
            return label;
          }}
        />
        <Legend />
        {assets.map((asset, index) => (
          <Line
            key={asset}
            type="monotone"
            dataKey={asset}
            stroke={colors[index % colors.length]}
            strokeWidth={1.5}
            dot={false}
            opacity={0.6}
          />
        ))}
        <Line
          type="monotone"
          dataKey="portfolio"
          stroke="#8b5cf6"
          name="Portfolio"
          strokeWidth={3}
          dot={false}
        />
      </LineChart>
    </ResponsiveContainer>
  );
};
