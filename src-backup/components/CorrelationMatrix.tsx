import { useMemo } from "react";

interface CorrelationData {
  asset1: string;
  asset2: string;
  correlation: number;
}

interface CorrelationMatrixProps {
  assets: string[];
  correlationData?: CorrelationData[];
  isLoading?: boolean;
}

export const CorrelationMatrix = ({ assets, correlationData, isLoading }: CorrelationMatrixProps) => {
  const correlationMatrix = useMemo(() => {
    const matrix: { [key: string]: { [key: string]: number } } = {};

    if (correlationData && correlationData.length > 0) {
      assets.forEach(asset1 => {
        matrix[asset1] = {};
        assets.forEach(asset2 => {
          const found = correlationData.find(
            d => d.asset1 === asset1 && d.asset2 === asset2
          );
          matrix[asset1][asset2] = found ? found.correlation : (asset1 === asset2 ? 1 : 0);
        });
      });
    } else {
      assets.forEach(asset1 => {
        matrix[asset1] = {};
        assets.forEach(asset2 => {
          if (asset1 === asset2) {
            matrix[asset1][asset2] = 1;
          } else {
            if (matrix[asset2] && matrix[asset2][asset1] !== undefined) {
              matrix[asset1][asset2] = matrix[asset2][asset1];
            } else {
              matrix[asset1][asset2] = parseFloat((Math.random() * 0.8 + 0.1).toFixed(2));
            }
          }
        });
      });
    }

    return matrix;
  }, [assets, correlationData]);

  const getColorForCorrelation = (value: number) => {
    if (value === 1) return "bg-blue-500";
    if (value >= 0.7) return "bg-green-500";
    if (value >= 0.4) return "bg-yellow-500";
    if (value >= 0.2) return "bg-orange-500";
    if (value >= 0) return "bg-red-400";
    if (value >= -0.2) return "bg-red-500";
    if (value >= -0.5) return "bg-red-600";
    return "bg-red-700";
  };

  const getTextColorForCorrelation = (value: number) => {
    if (Math.abs(value) >= 0.4) return "text-white";
    return "text-foreground";
  };

  if (isLoading) {
    return (
      <div className="w-full h-[300px] flex items-center justify-center bg-muted/20 rounded-lg">
        <div className="flex flex-col items-center gap-2">
          <div className="w-8 h-8 border-2 border-primary border-t-transparent rounded-full animate-spin" />
          <p className="text-sm text-muted-foreground">Loading correlation matrix...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="overflow-x-auto">
      <table className="w-full border-collapse">
        <thead>
          <tr>
            <th className="p-3 border border-border bg-muted"></th>
            {assets.map(asset => (
              <th key={asset} className="p-3 border border-border bg-muted text-sm font-semibold">
                {asset}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {assets.map(asset1 => (
            <tr key={asset1}>
              <td className="p-3 border border-border bg-muted text-sm font-semibold">
                {asset1}
              </td>
              {assets.map(asset2 => {
                const value = correlationMatrix[asset1]?.[asset2] ?? 0;
                return (
                  <td
                    key={asset2}
                    className={`p-3 border border-border text-center font-medium transition-colors ${getColorForCorrelation(value)} ${getTextColorForCorrelation(value)}`}
                  >
                    {value.toFixed(2)}
                  </td>
                );
              })}
            </tr>
          ))}
        </tbody>
      </table>

      <div className="mt-4 flex items-center justify-center gap-4 text-xs text-muted-foreground flex-wrap">
        <div className="flex items-center gap-2">
          <div className="w-4 h-4 bg-blue-500 rounded"></div>
          <span>Perfect (1.0)</span>
        </div>
        <div className="flex items-center gap-2">
          <div className="w-4 h-4 bg-green-500 rounded"></div>
          <span>Strong (0.7+)</span>
        </div>
        <div className="flex items-center gap-2">
          <div className="w-4 h-4 bg-yellow-500 rounded"></div>
          <span>Moderate (0.4+)</span>
        </div>
        <div className="flex items-center gap-2">
          <div className="w-4 h-4 bg-orange-500 rounded"></div>
          <span>Weak (0.2+)</span>
        </div>
        <div className="flex items-center gap-2">
          <div className="w-4 h-4 bg-red-500 rounded"></div>
          <span>Negative</span>
        </div>
      </div>
    </div>
  );
};
