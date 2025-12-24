import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, Area, ComposedChart } from "recharts";
import { useMemo } from "react";

interface PredictionDataPoint {
  date: string;
  predicted: number;
  lower_bound: number;
  upper_bound: number;
}

interface PredictionChartProps {
  symbol: string;
  historicalData?: Array<{ date: string; close: number }>;
  predictionData?: Array<PredictionDataPoint>;
  isLoading?: boolean;
}

export const PredictionChart = ({ symbol, historicalData, predictionData, isLoading }: PredictionChartProps) => {
  const chartData = useMemo(() => {
    const data: Array<{
      date: string;
      actual?: number;
      predicted?: number;
      lower?: number;
      upper?: number;
    }> = [];

    if (historicalData && historicalData.length > 0) {
      historicalData.forEach(point => {
        data.push({
          date: point.date,
          actual: point.close,
        });
      });
    }

    if (predictionData && predictionData.length > 0) {
      predictionData.forEach(point => {
        data.push({
          date: point.date,
          predicted: point.predicted,
          lower: point.lower_bound,
          upper: point.upper_bound,
        });
      });
    }

    return data;
  }, [historicalData, predictionData]);

  const formatXAxis = (tickItem: string) => {
    if (tickItem.includes('-')) {
      const date = new Date(tickItem);
      return date.toLocaleDateString('fr-FR', { day: '2-digit', month: '2-digit' });
    }
    return tickItem;
  };

  if (isLoading) {
    return (
      <div className="w-full h-[400px] flex items-center justify-center bg-muted/20 rounded-lg">
        <div className="flex flex-col items-center gap-2">
          <div className="w-8 h-8 border-2 border-primary border-t-transparent rounded-full animate-spin" />
          <p className="text-sm text-muted-foreground">Génération des prédictions...</p>
        </div>
      </div>
    );
  }

  if (!chartData || chartData.length === 0) {
    return (
      <div className="w-full h-[400px] flex items-center justify-center bg-muted/20 rounded-lg">
        <p className="text-sm text-muted-foreground">Aucune donnée de prédiction disponible</p>
      </div>
    );
  }

  return (
    <ResponsiveContainer width="100%" height={400}>
      <ComposedChart data={chartData}>
        <CartesianGrid strokeDasharray="3 3" stroke="hsl(var(--border))" />
        <XAxis
          dataKey="date"
          stroke="hsl(var(--muted-foreground))"
          tick={{ fill: 'hsl(var(--muted-foreground))', fontSize: 10 }}
          tickFormatter={formatXAxis}
          interval="preserveStartEnd"
        />
        <YAxis
          stroke="hsl(var(--muted-foreground))"
          tick={{ fill: 'hsl(var(--muted-foreground))', fontSize: 12 }}
          tickFormatter={(value) => `$${value.toFixed(0)}`}
          domain={['auto', 'auto']}
        />
        <Tooltip
          contentStyle={{
            backgroundColor: 'hsl(var(--card))',
            border: '1px solid hsl(var(--border))',
            borderRadius: '8px',
          }}
          formatter={(value: number, name: string) => {
            const labels: Record<string, string> = {
              actual: 'Prix réel',
              predicted: 'Prix prédit',
              lower: 'Borne inférieure',
              upper: 'Borne supérieure',
            };
            return [`$${value.toFixed(2)}`, labels[name] || name];
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
        <Legend
          formatter={(value) => {
            const labels: Record<string, string> = {
              actual: 'Prix historique',
              predicted: 'Prédiction Prophet',
              lower: 'Intervalle de confiance 95%',
            };
            return labels[value] || value;
          }}
        />
        <defs>
          <linearGradient id="confidenceArea" x1="0" y1="0" x2="0" y2="1">
            <stop offset="5%" stopColor="#4ade80" stopOpacity={0.3}/>
            <stop offset="95%" stopColor="#4ade80" stopOpacity={0.1}/>
          </linearGradient>
        </defs>
        <Area
          type="monotone"
          dataKey="lower"
          stroke="none"
          fill="url(#confidenceArea)"
          fillOpacity={1}
          legendType="rect"
        />
        <Area
          type="monotone"
          dataKey="upper"
          stroke="none"
          fill="url(#confidenceArea)"
          fillOpacity={1}
          legendType="none"
        />
        <Line
          type="monotone"
          dataKey="actual"
          stroke="#60a5fa"
          strokeWidth={2}
          dot={false}
          name="actual"
        />
        <Line
          type="monotone"
          dataKey="predicted"
          stroke="#4ade80"
          strokeWidth={2}
          dot={false}
          strokeDasharray="5 5"
          name="predicted"
        />
      </ComposedChart>
    </ResponsiveContainer>
  );
};
