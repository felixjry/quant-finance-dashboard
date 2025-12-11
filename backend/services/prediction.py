

import pandas as pd
import numpy as np
from prophet import Prophet
from typing import Dict, Optional
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

class PricePrediction:
    

    def __init__(self, historical_data: pd.DataFrame):
        
        self.data = historical_data.copy()
        self.model = None
        self.forecast = None

    def prepare_data(self) -> pd.DataFrame:
        
        df = pd.DataFrame({
            'ds': pd.to_datetime(self.data['date']),
            'y': self.data['close']
        })

        df = df.dropna()
        df = df.sort_values('ds')

        return df

    def train_model(self,
                   changepoint_prior_scale: float = 0.05,
                   seasonality_prior_scale: float = 10.0) -> None:
        
        try:
            df_prophet = self.prepare_data()

            if len(df_prophet) < 30:
                raise ValueError(f"Insufficient data: {len(df_prophet)} rows (minimum 30 required)")

            self.model = Prophet(
                changepoint_prior_scale=changepoint_prior_scale,
                seasonality_prior_scale=seasonality_prior_scale,
                interval_width=0.95,
                daily_seasonality=False,
                weekly_seasonality=True,
                yearly_seasonality=True
            )

            logger.info(f"Training Prophet model on {len(df_prophet)} data points...")
            self.model.fit(df_prophet)
            logger.info("Prophet model trained successfully")

        except Exception as e:
            logger.error(f"Error training Prophet model: {str(e)}")
            raise

    def predict(self, forecast_days: int = 30) -> pd.DataFrame:
        
        if self.model is None:
            raise ValueError("Model not trained. Call train_model() first.")

        try:
            future = self.model.make_future_dataframe(periods=forecast_days, freq='D')

            self.forecast = self.model.predict(future)

            forecast_result = self.forecast[['ds', 'yhat', 'yhat_lower', 'yhat_upper']].copy()
            forecast_result.columns = ['date', 'predicted', 'lower_bound', 'upper_bound']

            last_historical_date = pd.to_datetime(self.data['date'].max())
            forecast_only = forecast_result[forecast_result['date'] > last_historical_date].copy()

            return forecast_only

        except Exception as e:
            logger.error(f"Error generating predictions: {str(e)}")
            raise

    def calculate_metrics(self) -> Dict[str, float]:
        
        if self.forecast is None:
            return {}

        try:
            df_prophet = self.prepare_data()

            historical_forecast = self.forecast[self.forecast['ds'].isin(df_prophet['ds'])]

            y_true = df_prophet.set_index('ds')['y']
            y_pred = historical_forecast.set_index('ds')['yhat']

            common_index = y_true.index.intersection(y_pred.index)
            y_true = y_true.loc[common_index]
            y_pred = y_pred.loc[common_index]

            if len(y_true) == 0:
                return {}

            mae = np.mean(np.abs(y_true - y_pred))

            mape = np.mean(np.abs((y_true - y_pred) / y_true)) * 100

            rmse = np.sqrt(np.mean((y_true - y_pred) ** 2))

            mse = np.mean((y_true - y_pred) ** 2)

            ss_res = np.sum((y_true - y_pred) ** 2)
            ss_tot = np.sum((y_true - np.mean(y_true)) ** 2)
            r2 = 1 - (ss_res / ss_tot) if ss_tot != 0 else 0

            return {
                'mae': round(float(mae), 2),
                'mape': round(float(mape), 2),
                'rmse': round(float(rmse), 2),
                'mse': round(float(mse), 2),
                'r2_score': round(float(r2), 3)
            }

        except Exception as e:
            logger.error(f"Error calculating metrics: {str(e)}")
            return {}

    def get_forecast_summary(self, forecast_days: int = 30) -> Dict:
        
        self.train_model()

        predictions = self.predict(forecast_days)

        metrics = self.calculate_metrics()

        forecast_list = []
        for _, row in predictions.iterrows():
            forecast_list.append({
                'date': row['date'].strftime('%Y-%m-%d'),
                'predicted': round(float(row['predicted']), 2),
                'lower_bound': round(float(row['lower_bound']), 2),
                'upper_bound': round(float(row['upper_bound']), 2)
            })

        return {
            'forecast': forecast_list,
            'metrics': metrics,
            'forecast_days': forecast_days,
            'model': 'Prophet',
            'last_historical_date': self.data['date'].max().strftime('%Y-%m-%d'),
            'last_price': round(float(self.data['close'].iloc[-1]), 2)
        }

def predict_price(historical_data: pd.DataFrame, forecast_days: int = 30) -> Optional[Dict]:
    
    try:
        if len(historical_data) < 30:
            logger.warning(f"Insufficient data for prediction: {len(historical_data)} rows")
            return None

        predictor = PricePrediction(historical_data)
        result = predictor.get_forecast_summary(forecast_days)

        return result

    except Exception as e:
        logger.error(f"Price prediction failed: {str(e)}")
        return None
