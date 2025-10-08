"""
Configuration loader and validator for agent performance evaluation
"""

import yaml
from typing import Dict, Any, List, Optional
from pathlib import Path
from pydantic import BaseModel, Field, ValidationError
import logging


class ScaleConfig(BaseModel):
    """Model for scale configuration"""
    type: str
    range: List[float]
    description: str


class TargetConfig(BaseModel):
    """Model for target configuration"""
    value: float
    description: str
    operator: str


class CalculationConfig(BaseModel):
    """Model for calculation configuration"""
    formula: str
    final_range: Optional[List[float]] = None


class SubFactorConfig(BaseModel):
    """Model for sub-factor configuration"""
    name: str
    description: str
    scale: ScaleConfig
    weight: float


class KPIConfig(BaseModel):
    """Model for KPI configuration"""
    name: str
    description: str
    evaluates: str
    factors: Optional[List[str]] = None
    scale: Optional[ScaleConfig] = None
    target: TargetConfig
    sub_factors: Optional[Dict[str, SubFactorConfig]] = None
    calculation: Optional[CalculationConfig] = None
    interpretation: Optional[Dict[str, List[float]]] = None


class CategoryConfig(BaseModel):
    """Model for category configuration"""
    name: str
    description: str
    kpis: Dict[str, KPIConfig]


class EvaluationConfig(BaseModel):
    """Model for evaluation configuration"""
    feedback: Dict[str, List[str]]
    training_needs: Dict[str, List[str]]
    recognition: Dict[str, List[str]]


class SettingsConfig(BaseModel):
    """Model for settings configuration"""
    evaluation_frequency: str
    aggregation_levels: List[str]
    thresholds: Dict[str, float]
    reporting: Dict[str, Any]


class EvaluationFramework(BaseModel):
    """Model for the complete evaluation framework"""
    name: str
    version: str
    categories: Dict[str, CategoryConfig]


class ConfigLoader:
    """Loads and validates the agent performance configuration"""
    
    def __init__(self, config_path: str = None):
        self.logger = logging.getLogger(__name__)
        if config_path is None:
            # Default path relative to the src directory
            self.config_path = Path(__file__).parent.parent / "config" / "agent_performance_config.yaml"
        else:
            self.config_path = Path(config_path)
    
    def load_config(self) -> Dict[str, Any]:
        """Load the YAML configuration file"""
        try:
            with open(self.config_path, 'r', encoding='utf-8') as file:
                config_data = yaml.safe_load(file)
            
            self.logger.info(f"Successfully loaded configuration from {self.config_path}")
            return config_data
            
        except FileNotFoundError:
            self.logger.error(f"Configuration file not found: {self.config_path}")
            raise
        except yaml.YAMLError as e:
            self.logger.error(f"Error parsing YAML configuration: {e}")
            raise
        except Exception as e:
            self.logger.error(f"Unexpected error loading configuration: {e}")
            raise
    
    def validate_config(self, config_data: Dict[str, Any]) -> bool:
        """Validate the configuration structure"""
        try:
            # Validate the evaluation framework
            evaluation_framework = EvaluationFramework(**config_data['evaluation_framework'])
            
            # Validate evaluation section
            if 'evaluation' in config_data:
                evaluation = EvaluationConfig(**config_data['evaluation'])
            
            # Validate settings section
            if 'settings' in config_data:
                settings = SettingsConfig(**config_data['settings'])
            
            self.logger.info("Configuration validation successful")
            return True
            
        except ValidationError as e:
            self.logger.error(f"Configuration validation failed: {e}")
            return False
        except Exception as e:
            self.logger.error(f"Unexpected error during validation: {e}")
            return False
    
    def get_kpi_config(self, category: str, kpi: str) -> Optional[KPIConfig]:
        """Get configuration for a specific KPI"""
        config_data = self.load_config()
        
        try:
            categories = config_data['evaluation_framework']['categories']
            if category in categories and kpi in categories[category]['kpis']:
                kpi_data = categories[category]['kpis'][kpi]
                return KPIConfig(**kpi_data)
            else:
                self.logger.warning(f"KPI '{kpi}' not found in category '{category}'")
                return None
                
        except KeyError as e:
            self.logger.error(f"Missing key in configuration: {e}")
            return None
    
    def get_category_kpis(self, category: str) -> Dict[str, KPIConfig]:
        """Get all KPIs for a specific category"""
        config_data = self.load_config()
        
        try:
            categories = config_data['evaluation_framework']['categories']
            if category in categories:
                kpis = {}
                for kpi_name, kpi_data in categories[category]['kpis'].items():
                    kpis[kpi_name] = KPIConfig(**kpi_data)
                return kpis
            else:
                self.logger.warning(f"Category '{category}' not found in configuration")
                return {}
                
        except KeyError as e:
            self.logger.error(f"Missing key in configuration: {e}")
            return {}
    
    def get_all_categories(self) -> List[str]:
        """Get list of all category names"""
        config_data = self.load_config()
        
        try:
            return list(config_data['evaluation_framework']['categories'].keys())
        except KeyError:
            self.logger.error("Categories not found in configuration")
            return []
    
    def get_evaluation_settings(self) -> Optional[SettingsConfig]:
        """Get evaluation settings"""
        config_data = self.load_config()
        
        try:
            if 'settings' in config_data:
                return SettingsConfig(**config_data['settings'])
            else:
                self.logger.warning("Settings not found in configuration")
                return None
                
        except Exception as e:
            self.logger.error(f"Error loading settings: {e}")
            return None
    
    def calculate_kpi_score(self, kpi_config: KPIConfig, sub_scores: Dict[str, float]) -> float:
        """Calculate KPI score based on sub-factors and weights"""
        if not kpi_config.sub_factors or not kpi_config.calculation:
            # For simple KPIs without sub-factors, return the provided score
            return list(sub_scores.values())[0] if sub_scores else 0.0
        
        total_score = 0.0
        total_weight = 0.0
        
        for factor_name, factor_config in kpi_config.sub_factors.items():
            if factor_name in sub_scores:
                total_score += sub_scores[factor_name] * factor_config.weight
                total_weight += factor_config.weight
        
        # Normalize by total weight to handle missing factors
        if total_weight > 0:
            return total_score / total_weight * (sum(kpi_config.sub_factors[f].weight for f in kpi_config.sub_factors))
        else:
            return 0.0
    
    def evaluate_target_compliance(self, score: float, target_config: TargetConfig) -> bool:
        """Evaluate if a score meets the target criteria"""
        operator = target_config.operator
        target_value = target_config.value
        
        if operator == ">=":
            return score >= target_value
        elif operator == ">":
            return score > target_value
        elif operator == "<=":
            return score <= target_value
        elif operator == "<":
            return score < target_value
        elif operator == "=":
            return abs(score - target_value) < 0.001  # Allow for floating point precision
        else:
            self.logger.warning(f"Unknown operator: {operator}")
            return False
    
    def get_interpretation(self, score: float, kpi_config: KPIConfig) -> str:
        """Get interpretation of a score based on KPI configuration"""
        if not kpi_config.interpretation:
            return "No interpretation available"
        
        for level, range_values in kpi_config.interpretation.items():
            if len(range_values) == 2:
                min_val, max_val = range_values
                if min_val <= score <= max_val:
                    return level.replace('_', ' ').title()
        
        return "Unknown"


# Global configuration loader instance
config_loader = ConfigLoader()


def load_agent_performance_config() -> Dict[str, Any]:
    """Convenience function to load the configuration"""
    return config_loader.load_config()


def validate_agent_performance_config() -> bool:
    """Convenience function to validate the configuration"""
    try:
        config_data = config_loader.load_config()
        return config_loader.validate_config(config_data)
    except Exception:
        return False
