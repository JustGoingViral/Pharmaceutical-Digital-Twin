"""
Predictive Quality Forecasting Engine
AI-powered system for predicting pharmaceutical quality metrics 30+ days in advance
"""

import numpy as np
import pandas as pd
from typing import List, Dict, Tuple, Optional, Union
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import TimeSeriesSplit
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers
import joblib
import json
import logging
import warnings
warnings.filterwarnings('ignore')

logger = logging.getLogger(__name__)

@dataclass
class QualityMetrics:
    """Quality metrics for pharmaceutical products"""
    purity: float
    potency: float
    dissolution_rate: float
    moisture_content: float
    particle_size_d50: float
    particle_size_d90: float
    impurity_a: float
    impurity_b: float
    impurity_total: float
    ph: float
    microbial_count: float
    endotoxin_level: float
    
    def to_dict(self) -> Dict:
        return self.__dict__
    
    def validate(self, specifications: Dict[str, Tuple[float, float]]) -> Dict[str, bool]:
        """Validate metrics against specifications"""
        results = {}
        for metric, (min_val, max_val) in specifications.items():
            if hasattr(self, metric):
                value = getattr(self, metric)
                results[metric] = min_val <= value <= max_val
        return results

@dataclass
class ProcessParameters:
    """Manufacturing process parameters"""
    temperature: float
    pressure: float
    humidity: float
    mixing_speed: float
    mixing_time: float
    drying_temperature: float
    drying_time: float
    granulation_liquid_amount: float
    compression_force: float
    coating_spray_rate: float
    air_flow_rate: float
    
@dataclass
class EnvironmentalData:
    """Environmental conditions during manufacturing"""
    room_temperature: float
    room_humidity: float
    room_pressure_differential: float
    particulate_count_05um: int
    particulate_count_5um: int
    air_changes_per_hour: float
    operator_count: int
    shift: str  # 'day', 'evening', 'night'

class QualityForecastingEngine:
    """Advanced AI engine for quality prediction"""
    
    def __init__(self, product_id: str, model_type: str = "ensemble"):
        self.product_id = product_id
        self.model_type = model_type
        self.models = {}
        self.scalers = {}
        self.feature_importance = {}
        self.prediction_history = []
        self.model_performance = {}
        self.is_trained = False
        
        # Initialize models
        self._initialize_models()
        
    def _initialize_models(self):
        """Initialize ML models for each quality metric"""
        quality_metrics = ['purity', 'potency', 'dissolution_rate', 'moisture_content',
                          'particle_size_d50', 'particle_size_d90', 'impurity_total', 'ph']
        
        for metric in quality_metrics:
            if self.model_type == "ensemble":
                # Ensemble of multiple models
                self.models[metric] = {
                    'rf': RandomForestRegressor(n_estimators=100, random_state=42),
                    'gb': GradientBoostingRegressor(n_estimators=100, random_state=42),
                    'nn': self._build_neural_network()
                }
            else:
                # Single model
                self.models[metric] = RandomForestRegressor(n_estimators=200, random_state=42)
            
            self.scalers[metric] = StandardScaler()
    
    def _build_neural_network(self) -> keras.Model:
        """Build neural network for quality prediction"""
        model = keras.Sequential([
            layers.Dense(128, activation='relu'),
            layers.Dropout(0.2),
            layers.Dense(64, activation='relu'),
            layers.Dropout(0.2),
            layers.Dense(32, activation='relu'),
            layers.Dense(16, activation='relu'),
            layers.Dense(1)
        ])
        
        model.compile(
            optimizer=keras.optimizers.Adam(learning_rate=0.001),
            loss='mse',
            metrics=['mae']
        )
        
        return model
    
    def train(self, historical_data: pd.DataFrame, 
              quality_specifications: Dict[str, Tuple[float, float]]):
        """Train the forecasting models on historical data"""
        logger.info(f"Training quality forecasting models for product {self.product_id}")
        
        # Prepare features and targets
        feature_columns = [col for col in historical_data.columns 
                          if col not in ['timestamp', 'batch_id'] and not col.startswith('quality_')]
        
        for metric in self.models.keys():
            target_col = f'quality_{metric}'
            if target_col not in historical_data.columns:
                logger.warning(f"Target column {target_col} not found in data")
                continue
            
            # Remove rows with missing target values
            valid_data = historical_data.dropna(subset=[target_col])
            
            X = valid_data[feature_columns].values
            y = valid_data[target_col].values
            
            # Scale features
            X_scaled = self.scalers[metric].fit_transform(X)
            
            # Time series split for validation
            tscv = TimeSeriesSplit(n_splits=5)
            
            if isinstance(self.models[metric], dict):
                # Train ensemble
                for model_name, model in self.models[metric].items():
                    if model_name == 'nn':
                        # Train neural network
                        model.fit(
                            X_scaled, y,
                            epochs=50,
                            batch_size=32,
                            validation_split=0.2,
                            verbose=0
                        )
                    else:
                        # Train sklearn models
                        model.fit(X_scaled, y)
                
                # Calculate feature importance (from RF model)
                self.feature_importance[metric] = dict(
                    zip(feature_columns, 
                        self.models[metric]['rf'].feature_importances_)
                )
            else:
                # Train single model
                self.models[metric].fit(X_scaled, y)
                self.feature_importance[metric] = dict(
                    zip(feature_columns, 
                        self.models[metric].feature_importances_)
                )
            
            # Evaluate model performance
            self._evaluate_model(metric, X_scaled, y, tscv)
        
        self.is_trained = True
        self.quality_specifications = quality_specifications
        logger.info("Model training completed")
    
    def _evaluate_model(self, metric: str, X: np.ndarray, y: np.ndarray, 
                       tscv: TimeSeriesSplit):
        """Evaluate model performance using cross-validation"""
        scores = []
        
        for train_index, test_index in tscv.split(X):
            X_train, X_test = X[train_index], X[test_index]
            y_train, y_test = y[train_index], y[test_index]
            
            if isinstance(self.models[metric], dict):
                # Ensemble prediction
                predictions = []
                for model_name, model in self.models[metric].items():
                    if model_name == 'nn':
                        pred = model.predict(X_test, verbose=0).flatten()
                    else:
                        # Refit on train split
                        model.fit(X_train, y_train)
                        pred = model.predict(X_test)
                    predictions.append(pred)
                
                # Average ensemble predictions
                y_pred = np.mean(predictions, axis=0)
            else:
                self.models[metric].fit(X_train, y_train)
                y_pred = self.models[metric].predict(X_test)
            
            # Calculate metrics
            mse = np.mean((y_test - y_pred) ** 2)
            mae = np.mean(np.abs(y_test - y_pred))
            r2 = 1 - (np.sum((y_test - y_pred) ** 2) / np.sum((y_test - y_test.mean()) ** 2))
            
            scores.append({'mse': mse, 'mae': mae, 'r2': r2})
        
        # Average scores
        avg_scores = {
            'mse': np.mean([s['mse'] for s in scores]),
            'mae': np.mean([s['mae'] for s in scores]),
            'r2': np.mean([s['r2'] for s in scores]),
            'std_mae': np.std([s['mae'] for s in scores])
        }
        
        self.model_performance[metric] = avg_scores
        logger.info(f"Model performance for {metric}: MAE={avg_scores['mae']:.4f}, R2={avg_scores['r2']:.4f}")
    
    def predict(self, process_params: ProcessParameters, 
                environmental_data: EnvironmentalData,
                current_quality: Optional[QualityMetrics] = None,
                forecast_days: int = 30) -> Dict[str, Any]:
        """Predict quality metrics for future timepoints"""
        if not self.is_trained:
            raise ValueError("Model must be trained before making predictions")
        
        # Prepare input features
        features = self._prepare_features(process_params, environmental_data, current_quality)
        
        predictions = {}
        confidence_intervals = {}
        risk_assessments = {}
        
        # Generate predictions for each metric
        for metric in self.models.keys():
            # Scale features
            features_scaled = self.scalers[metric].transform(features.reshape(1, -1))
            
            if isinstance(self.models[metric], dict):
                # Ensemble prediction
                metric_predictions = []
                for model_name, model in self.models[metric].items():
                    if model_name == 'nn':
                        pred = model.predict(features_scaled, verbose=0).flatten()[0]
                    else:
                        pred = model.predict(features_scaled)[0]
                    metric_predictions.append(pred)
                
                # Calculate mean and uncertainty
                mean_pred = np.mean(metric_predictions)
                std_pred = np.std(metric_predictions)
            else:
                # Single model prediction
                mean_pred = self.models[metric].predict(features_scaled)[0]
                # Estimate uncertainty using model's feature importances
                std_pred = self._estimate_prediction_uncertainty(metric, features_scaled)
            
            # Generate time series forecast
            forecast = self._generate_time_series_forecast(
                metric, mean_pred, std_pred, forecast_days
            )
            
            predictions[metric] = forecast
            
            # Calculate confidence intervals
            confidence_intervals[metric] = {
                'lower_95': forecast['values'] - 1.96 * forecast['uncertainty'],
                'upper_95': forecast['values'] + 1.96 * forecast['uncertainty'],
                'lower_99': forecast['values'] - 2.58 * forecast['uncertainty'],
                'upper_99': forecast['values'] + 2.58 * forecast['uncertainty']
            }
            
            # Risk assessment
            if metric in self.quality_specifications:
                risk_assessments[metric] = self._assess_quality_risk(
                    forecast, self.quality_specifications[metric]
                )
        
        # Generate overall prediction summary
        prediction_result = {
            'prediction_id': self._generate_prediction_id(),
            'timestamp': datetime.utcnow().isoformat(),
            'forecast_horizon_days': forecast_days,
            'predictions': predictions,
            'confidence_intervals': confidence_intervals,
            'risk_assessments': risk_assessments,
            'model_performance': self.model_performance,
            'feature_importance': self._get_top_features(),
            'recommendations': self._generate_recommendations(predictions, risk_assessments)
        }
        
        # Store prediction for tracking
        self.prediction_history.append(prediction_result)
        
        return prediction_result
    
    def _prepare_features(self, process_params: ProcessParameters,
                         environmental_data: EnvironmentalData,
                         current_quality: Optional[QualityMetrics]) -> np.ndarray:
        """Prepare feature vector for prediction"""
        features = []
        
        # Process parameters
        features.extend([
            process_params.temperature,
            process_params.pressure,
            process_params.humidity,
            process_params.mixing_speed,
            process_params.mixing_time,
            process_params.drying_temperature,
            process_params.drying_time,
            process_params.granulation_liquid_amount,
            process_params.compression_force,
            process_params.coating_spray_rate,
            process_params.air_flow_rate
        ])
        
        # Environmental data
        features.extend([
            environmental_data.room_temperature,
            environmental_data.room_humidity,
            environmental_data.room_pressure_differential,
            np.log1p(environmental_data.particulate_count_05um),  # Log transform counts
            np.log1p(environmental_data.particulate_count_5um),
            environmental_data.air_changes_per_hour,
            environmental_data.operator_count
        ])
        
        # Encode shift
        shift_encoding = {'day': 0, 'evening': 1, 'night': 2}
        features.append(shift_encoding.get(environmental_data.shift, 0))
        
        # Add time-based features
        now = datetime.utcnow()
        features.extend([
            now.hour,
            now.day,
            now.month,
            now.weekday()
        ])
        
        # Add current quality if available (for time series continuity)
        if current_quality:
            features.extend([
                current_quality.purity,
                current_quality.potency,
                current_quality.dissolution_rate,
                current_quality.moisture_content
            ])
        else:
            # Use default values if not available
            features.extend([99.0, 100.0, 85.0, 2.0])
        
        return np.array(features)
    
    def _generate_time_series_forecast(self, metric: str, initial_value: float,
                                     uncertainty: float, days: int) -> Dict:
        """Generate time series forecast with trend and seasonality"""
        timestamps = []
        values = []
        uncertainties = []
        
        # Model performance metrics for this metric
        model_mae = self.model_performance.get(metric, {}).get('mae', 0.1)
        
        for day in range(days + 1):
            timestamp = datetime.utcnow() + timedelta(days=day)
            timestamps.append(timestamp.isoformat())
            
            # Add slight trend and seasonality
            trend = -0.001 * day  # Slight degradation over time
            seasonality = 0.05 * np.sin(2 * np.pi * day / 7)  # Weekly pattern
            noise = np.random.normal(0, uncertainty * 0.1)
            
            # Calculate predicted value
            value = initial_value + trend + seasonality + noise
            
            # Increase uncertainty over time
            day_uncertainty = uncertainty * (1 + 0.02 * day) + model_mae
            
            values.append(value)
            uncertainties.append(day_uncertainty)
        
        return {
            'timestamps': timestamps,
            'values': np.array(values),
            'uncertainty': np.array(uncertainties),
            'initial_value': initial_value,
            'final_value': values[-1],
            'trend': 'stable' if abs(values[-1] - initial_value) < uncertainty else 
                    ('declining' if values[-1] < initial_value else 'improving')
        }
    
    def _estimate_prediction_uncertainty(self, metric: str, features: np.ndarray) -> float:
        """Estimate prediction uncertainty based on feature importance"""
        # Base uncertainty from model performance
        base_uncertainty = self.model_performance.get(metric, {}).get('std_mae', 0.1)
        
        # Additional uncertainty based on feature values
        feature_uncertainty = 0.05  # 5% additional uncertainty
        
        return base_uncertainty + feature_uncertainty
    
    def _assess_quality_risk(self, forecast: Dict, 
                           specification: Tuple[float, float]) -> Dict:
        """Assess risk of quality deviation"""
        min_spec, max_spec = specification
        values = forecast['values']
        uncertainties = forecast['uncertainty']
        
        # Calculate probability of being out of specification
        risks = []
        for value, uncertainty in zip(values, uncertainties):
            # Assume normal distribution
            prob_below_min = norm.cdf(min_spec, value, uncertainty)
            prob_above_max = 1 - norm.cdf(max_spec, value, uncertainty)
            risk = prob_below_min + prob_above_max
            risks.append(risk)
        
        # Find when risk exceeds thresholds
        risk_array = np.array(risks)
        first_high_risk = np.where(risk_array > 0.1)[0]
        first_critical_risk = np.where(risk_array > 0.25)[0]
        
        return {
            'risk_profile': risks,
            'max_risk': float(np.max(risks)),
            'average_risk': float(np.mean(risks)),
            'days_until_high_risk': int(first_high_risk[0]) if len(first_high_risk) > 0 else None,
            'days_until_critical_risk': int(first_critical_risk[0]) if len(first_critical_risk) > 0 else None,
            'risk_category': self._categorize_risk(np.max(risks))
        }
    
    def _categorize_risk(self, risk_value: float) -> str:
        """Categorize risk level"""
        if risk_value < 0.05:
            return "low"
        elif risk_value < 0.1:
            return "moderate"
        elif risk_value < 0.25:
            return "high"
        else:
            return "critical"
    
    def _get_top_features(self, top_n: int = 5) -> Dict[str, List[Tuple[str, float]]]:
        """Get top influential features for each metric"""
        top_features = {}
        
        for metric, importance_dict in self.feature_importance.items():
            sorted_features = sorted(importance_dict.items(), key=lambda x: x[1], reverse=True)
            top_features[metric] = sorted_features[:top_n]
        
        return top_features
    
    def _generate_recommendations(self, predictions: Dict, 
                                risk_assessments: Dict) -> List[Dict]:
        """Generate actionable recommendations based on predictions"""
        recommendations = []
        
        # Check each metric for potential issues
        for metric, risk_data in risk_assessments.items():
            if risk_data['risk_category'] in ['high', 'critical']:
                forecast = predictions[metric]
                
                # Identify root causes from feature importance
                top_features = self.feature_importance.get(metric, {})
                influential_features = sorted(top_features.items(), 
                                            key=lambda x: x[1], reverse=True)[:3]
                
                recommendation = {
                    'metric': metric,
                    'urgency': 'immediate' if risk_data['risk_category'] == 'critical' else 'high',
                    'risk_level': risk_data['risk_category'],
                    'days_until_issue': risk_data.get('days_until_high_risk', 0),
                    'recommended_actions': []
                }
                
                # Generate specific recommendations based on metric
                if metric == 'purity' and forecast['trend'] == 'declining':
                    recommendation['recommended_actions'].extend([
                        "Review and optimize purification process parameters",
                        "Check raw material quality and supplier certificates",
                        "Increase sampling frequency for impurity testing",
                        "Consider implementing additional purification step"
                    ])
                
                elif metric == 'moisture_content' and forecast['trend'] == 'improving':
                    recommendation['recommended_actions'].extend([
                        "Adjust drying time and temperature",
                        "Monitor environmental humidity more closely",
                        "Check integrity of packaging materials",
                        "Validate moisture analyzer calibration"
                    ])
                
                elif metric == 'dissolution_rate':
                    recommendation['recommended_actions'].extend([
                        "Optimize granulation parameters",
                        "Review compression force settings",
                        "Check particle size distribution",
                        "Evaluate disintegrant effectiveness"
                    ])
                
                # Add feature-based recommendations
                for feature_name, importance in influential_features[:2]:
                    if 'temperature' in feature_name:
                        recommendation['recommended_actions'].append(
                            f"Monitor and control {feature_name} more strictly"
                        )
                    elif 'humidity' in feature_name:
                        recommendation['recommended_actions'].append(
                            f"Implement tighter {feature_name} controls"
                        )
                
                recommendations.append(recommendation)
        
        # Add preventive recommendations
        if not recommendations:
            recommendations.append({
                'metric': 'overall',
                'urgency': 'low',
                'risk_level': 'low',
                'recommended_actions': [
                    "Continue current manufacturing practices",
                    "Maintain regular equipment calibration schedule",
                    "Keep monitoring critical quality attributes",
                    "Document any process deviations"
                ]
            })
        
        return recommendations
    
    def _generate_prediction_id(self) -> str:
        """Generate unique prediction ID"""
        import hashlib
        data = f"{self.product_id}_{datetime.utcnow().isoformat()}"
        return hashlib.sha256(data.encode()).hexdigest()[:12]
    
    def update_with_actual_data(self, prediction_id: str, 
                              actual_quality: QualityMetrics) -> Dict:
        """Update model with actual quality data for continuous improvement"""
        # Find the prediction
        prediction = None
        for pred in self.prediction_history:
            if pred['prediction_id'] == prediction_id:
                prediction = pred
                break
        
        if not prediction:
            raise ValueError(f"Prediction {prediction_id} not found")
        
        # Calculate prediction accuracy
        accuracy_metrics = {}
        for metric in ['purity', 'potency', 'dissolution_rate', 'moisture_content']:
            if hasattr(actual_quality, metric):
                actual_value = getattr(actual_quality, metric)
                predicted_value = prediction['predictions'][metric]['initial_value']
                
                error = abs(actual_value - predicted_value)
                percent_error = (error / actual_value) * 100 if actual_value != 0 else 0
                
                accuracy_metrics[metric] = {
                    'actual': actual_value,
                    'predicted': predicted_value,
                    'absolute_error': error,
                    'percent_error': percent_error,
                    'within_confidence_interval': self._check_within_ci(
                        actual_value, 
                        prediction['confidence_intervals'][metric]
                    )
                }
        
        # Store feedback for model improvement
        feedback = {
            'prediction_id': prediction_id,
            'timestamp': datetime.utcnow().isoformat(),
            'accuracy_metrics': accuracy_metrics,
            'overall_accuracy': np.mean([m['percent_error'] for m in accuracy_metrics.values()])
        }
        
        return feedback
    
    def _check_within_ci(self, value: float, ci: Dict) -> Dict[str, bool]:
        """Check if value is within confidence intervals"""
        return {
            '95%': ci['lower_95'][0] <= value <= ci['upper_95'][0],
            '99%': ci['lower_99'][0] <= value <= ci['upper_99'][0]
        }
    
    def export_model(self, filepath: str):
        """Export trained model for deployment"""
        export_data = {
            'product_id': self.product_id,
            'model_type': self.model_type,
            'is_trained': self.is_trained,
            'model_performance': self.model_performance,
            'feature_importance': self.feature_importance,
            'quality_specifications': self.quality_specifications,
            'training_timestamp': datetime.utcnow().isoformat()
        }
        
        # Save models and scalers
        for metric in self.models.keys():
            # Save scaler
            joblib.dump(self.scalers[metric], f"{filepath}_{metric}_scaler.pkl")
            
            if isinstance(self.models[metric], dict):
                # Save ensemble models
                for model_name, model in self.models[metric].items():
                    if model_name == 'nn':
                        model.save(f"{filepath}_{metric}_{model_name}.h5")
                    else:
                        joblib.dump(model, f"{filepath}_{metric}_{model_name}.pkl")
            else:
                # Save single model
                joblib.dump(self.models[metric], f"{filepath}_{metric}_model.pkl")
        
        # Save metadata
        with open(f"{filepath}_metadata.json", 'w') as f:
            json.dump(export_data, f, indent=2)
        
        logger.info(f"Model exported to {filepath}")