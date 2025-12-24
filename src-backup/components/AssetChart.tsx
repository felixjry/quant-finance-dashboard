import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from "recharts";
import { useMemo } from "react";

interface ChartDataPoint {
  date: string;
  price: number;
  strategy: number;
}

interface AssetChartProps {
  strategy: string;
  period: number;
  asset: string;
  chartData?: ChartDataPoint[];
  isLoading?: boolean;
}

export const AssetChart = ({ strategy, period, asset, chartData, isLoading }: AssetChartProps) => {
  const displayData = useMemo(() => {
    if (chartData && chartData.length > 0) {
      return chartData.map(point => ({
        date: point.date,
        price: Number(point.price.toFixed(2)), // Raw price in $
        strategy: Number((point.strategy * 100).toFixed(2)), // Performance base 100
      }));
    }

    // Fallback demo data with real dates
    const data = [];
    let price = 150;
    let strategyValue = 100;
    const today = new Date();

    for (let i = 0; i < 252; i++) {
      const change = (Math.random() - 0.48) * 2;
      price = price * (1 + change / 100);

      let strategyChange = change;
      if (strategy === "momentum") {
        strategyChange = change * 1.2 + (Math.random() - 0.5) * 0.5;
      } else if (strategy === "mean_reversion") {
        strategyChange = -change * 0.8 + (Math.random() - 0.5) * 0.5;
      }
      strategyValue = strategyValue * (1 + strategyChange / 100);

      // Generate real dates going back from today
      const date = new Date(today);
      date.setDate(date.getDate() - (251 - i));

      data.push({
        date: date.toISOString().split('T')[0],
        price: parseFloat(price.toFixed(2)),
        strategy: parseFloat(strategyValue.toFixed(2)),
      });
    }
    return data;
  }, [chartData, strategy]);

  const formatXAxis = (tickItem: string) => {
    if (tickItem.includes('-')) {
      const date = new Date(tickItem);
      return date.toLocaleDateString('fr-FR', { day: '2-digit', month: '2-digit', year: 'numeric' });
    }
    return tickItem;
  };

  if (isLoading) {
    return (
      <div className="w-full h-[400px] flex items-center justify-center bg-muted/20 rounded-lg">
        <div className="flex flex-col items-center gap-2">
          <div className="w-8 h-8 border-2 border-primary border-t-transparent rounded-full animate-spin" />
          <p className="text-sm text-muted-foreground">Loading chart data...</p>
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
          tick={{ fill: 'hsl(var(--muted-foreground))', fontSize: 10 }}
          tickFormatter={formatXAxis}
          interval="preserveStartEnd"
        />
        <YAxis
          yAxisId="left"
          stroke="#60a5fa"
          tick={{ fill: '#60a5fa', fontSize: 12 }}
          tickFormatter={(value) => `$${value}`}
          domain={['auto', 'auto']}
          label={{ value: 'Asset Price ($)', angle: -90, position: 'insideLeft', fill: '#60a5fa', fontSize: 12 }}
        />
        <YAxis
          yAxisId="right"
          orientation="right"
          stroke="#4ade80"
          tick={{ fill: '#4ade80', fontSize: 12 }}
          tickFormatter={(value) => `${value}`}
          domain={['auto', 'auto']}
          label={{ value: 'Performance (Base 100)', angle: 90, position: 'insideRight', fill: '#4ade80', fontSize: 12 }}
        />
        <Tooltip
          contentStyle={{
            backgroundColor: 'hsl(var(--card))',
            border: '1px solid hsl(var(--border))',
            borderRadius: '8px',
          }}
          formatter={(value: number, name: string) => {
            if (name.includes('Price')) {
              return [`$${value.toFixed(2)}`, name];
            }
            return [value.toFixed(2), name];
          }}
          labelFormatter={(label) => {
            if (typeof label === 'string' && label.includes('-')) {
              return new Date(label).toLocaleDateString('fr-FR', {
                year: 'numeric',
                month: 'long',
                day: 'numeric'
              });
            }
            return label;
          }}
        />
        <Legend />
        <Line
          yAxisId="left"
          type="monotone"
          dataKey="price"
          stroke="#60a5fa"
          name={`Asset Price ($)`}
          strokeWidth={2}
          dot={false}
        />
        <Line
          yAxisId="right"
          type="monotone"
          dataKey="strategy"
          stroke="#4ade80"
          name="Strategy Performance (Base 100)"
          strokeWidth={2}
          dot={false}
        />
      </LineChart>
    </ResponsiveContainer>
  );
};
