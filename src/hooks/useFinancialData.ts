/**
 * Custom hooks for financial data fetching
 * Uses React Query for caching and automatic refetching
 */

import { useQuery, useMutation } from '@tanstack/react-query';
import { api, PriceInfo, StrategyResult, PortfolioResult, PredictionResult } from '../services/api';

const REFETCH_INTERVAL = 5 * 60 * 1000; // 5 minutes

/**
 * Hook to fetch current price for an asset
 */
export function useCurrentPrice(symbol: string) {
  return useQuery({
    queryKey: ['price', symbol],
    queryFn: () => api.getCurrentPrice(symbol),
    refetchInterval: REFETCH_INTERVAL,
    staleTime: 0,
    enabled: !!symbol,
  });
}

/**
 * Hook to fetch historical data for an asset
 */
export function useAssetHistory(
  symbol: string,
  period: string = '1y',
  interval: string = 'daily'
) {
  return useQuery({
    queryKey: ['history', symbol, period, interval],
    queryFn: () => api.getAssetHistory(symbol, period, interval),
    refetchInterval: REFETCH_INTERVAL,
    staleTime: 60 * 1000,
    enabled: !!symbol,
  });
}

/**
 * Hook to fetch asset metrics
 */
export function useAssetMetrics(symbol: string, period: string = '1y') {
  return useQuery({
    queryKey: ['metrics', symbol, period],
    queryFn: () => api.getAssetMetrics(symbol, period),
    refetchInterval: REFETCH_INTERVAL,
    staleTime: 60 * 1000,
    enabled: !!symbol,
  });
}

/**
 * Hook to run a backtesting strategy
 */
export function useStrategy(
  symbol: string,
  strategy: string,
  period: string = '1y',
  options: {
    interval?: string;
    lookback_period?: number;
    short_window?: number;
    long_window?: number;
  } = {}
) {
  return useQuery({
    queryKey: ['strategy', symbol, strategy, period, options.interval, options.lookback_period, options.short_window, options.long_window],
    queryFn: () => api.runStrategy(symbol, strategy, period, options),
    refetchInterval: REFETCH_INTERVAL,
    staleTime: 0,
    gcTime: 0, // Previously cacheTime, forces no caching
    refetchOnMount: true,
    enabled: !!symbol && !!strategy,
  });
}

/**
 * Hook to analyze a portfolio
 */
export function usePortfolioAnalysis(
  symbols: string[],
  weighting: string = 'equal_weight',
  rebalance: string = 'monthly',
  period: string = '1y'
) {
  return useQuery({
    queryKey: ['portfolio', symbols.sort().join(','), weighting, rebalance, period],
    queryFn: () => api.analyzePortfolio(symbols, weighting, rebalance, period),
    refetchInterval: REFETCH_INTERVAL,
    staleTime: 2 * 60 * 1000,
    enabled: symbols.length >= 2,
  });
}

/**
 * Hook to get efficient frontier
 */
export function useEfficientFrontier(
  symbols: string[],
  period: string = '1y',
  nPortfolios: number = 100
) {
  return useQuery({
    queryKey: ['frontier', symbols.sort().join(','), period, nPortfolios],
    queryFn: () => api.getEfficientFrontier(symbols, period, nPortfolios),
    staleTime: 5 * 60 * 1000,
    enabled: symbols.length >= 2,
  });
}

/**
 * Hook to get market overview
 */
export function useMarketOverview() {
  return useQuery({
    queryKey: ['market-overview'],
    queryFn: () => api.getMarketOverview(),
    refetchInterval: REFETCH_INTERVAL,
    staleTime: 60 * 1000,
  });
}

/**
 * Hook to get available assets
 */
export function useAvailableAssets() {
  return useQuery({
    queryKey: ['available-assets'],
    queryFn: () => api.getAvailableAssets(),
    staleTime: 30 * 60 * 1000,
  });
}

/**
 * Hook to predict future prices using Prophet
 */
export function usePrediction(
  symbol: string,
  period: string = '1y',
  forecastDays: number = 30
) {
  return useQuery({
    queryKey: ['prediction', symbol, period, forecastDays],
    queryFn: () => api.predictPrice(symbol, period, forecastDays),
    staleTime: 0,
    enabled: !!symbol,
  });
}

/**
 * Hook for API health check
 */
export function useHealthCheck() {
  return useQuery({
    queryKey: ['health'],
    queryFn: () => api.healthCheck(),
    refetchInterval: 30 * 1000,
    retry: 3,
  });
}
