"""
Tests for the LLM Agent Service
"""

import pytest
import json
from unittest.mock import Mock, patch, MagicMock
from typing import Dict, Any

from src.llm_agent_service import (
    ConversationAnalysisTool,
    ConfigurationTool,
    ConversationFormatterTool,
    LLMAgentPerformanceAnalysisService,
    get_llm_agent_service
)
from src.models import ConversationData, Tweet, Classification


class TestConversationAnalysisTool:
    """Test the ConversationAnalysisTool"""
    
    def test_tool_initialization(self):
        """Test tool initialization"""
        tool = ConversationAnalysisTool()
        assert tool.name == "conversation_analysis_tool"
        assert "analyze a conversation against a specific KPI" in tool.description.lower()
    
    @patch('src.llm_agent_service.ChatOpenAI')
    def test_run_analysis_success(self, mock_llm_class):
        """Test successful conversation analysis"""
        # Mock LLM response
        mock_llm = Mock()
        mock_response = Mock()
        mock_response.content = json.dumps({
            "score": 8.5,
            "normalized_score": 0.85,
            "meets_target": True,
            "confidence": 0.9,
            "reasoning": "Strong empathetic response",
            "evidence": ["I understand your frustration"],
            "recommendations": ["Continue empathetic approach"],
            "interpretation": "Excellent"
        })
        mock_llm.invoke.return_value = mock_response
        mock_llm_class.return_value = mock_llm
        
        tool = ConversationAnalysisTool()
        
        conversation_text = "Customer: I'm frustrated\nAgent: I understand your frustration"
        kpi_config = json.dumps({
            "name": "Empathy Score",
            "description": "Measure empathy",
            "scale": {"type": "numeric", "range": [0, 10]},
            "target": {"value": 7.0, "operator": ">="}
        })
        
        result = tool._run(conversation_text, kpi_config)
        result_data = json.loads(result)
        
        assert result_data["score"] == 8.5
        assert result_data["meets_target"] == True
        assert "empathetic response" in result_data["reasoning"]
    
    def test_run_analysis_error_handling(self):
        """Test error handling in analysis"""
        tool = ConversationAnalysisTool()
        
        # Test with invalid JSON
        result = tool._run("conversation", "invalid json")
        result_data = json.loads(result)
        
        assert "error" in result_data
        assert result_data["score"] == 0.0
        assert result_data["confidence"] == 0.0
    
    def test_create_analysis_prompt(self):
        """Test analysis prompt creation"""
        tool = ConversationAnalysisTool()
        
        conversation_text = "Test conversation"
        kpi_data = {
            "name": "Test KPI",
            "description": "Test description",
            "evaluates": "Test evaluation",
            "scale": {"type": "numeric", "range": [0, 10], "description": "0-10 scale"},
            "target": {"value": 8.0, "operator": ">=", "description": ">= 8"},
            "sub_factors": {
                "factor1": {
                    "name": "Factor 1",
                    "description": "First factor",
                    "weight": 0.6
                }
            },
            "interpretation": {
                "excellent": [8, 10],
                "good": [6, 7.99]
            }
        }
        
        prompt = tool._create_analysis_prompt(conversation_text, kpi_data, "Test context")
        
        # Verify key elements are in the prompt
        assert "Test conversation" in prompt
        assert "Test KPI" in prompt
        assert "Test description" in prompt
        assert "SUB-FACTORS TO CONSIDER" in prompt
        assert "Factor 1" in prompt
        assert "INTERPRETATION LEVELS" in prompt
        assert "Excellent" in prompt
        assert "JSON" in prompt


class TestConfigurationTool:
    """Test the ConfigurationTool"""
    
    def test_tool_initialization(self):
        """Test tool initialization"""
        tool = ConfigurationTool()
        assert tool.name == "configuration_tool"
        assert "retrieve KPI configuration" in tool.description.lower()
    
    @patch('src.llm_agent_service.config_loader')
    def test_run_get_specific_kpi(self, mock_config_loader):
        """Test getting specific KPI configuration"""
        # Mock KPI config
        mock_kpi = Mock()
        mock_kpi.dict.return_value = {
            "name": "Test KPI",
            "description": "Test description",
            "scale": {"type": "numeric", "range": [0, 10]}
        }
        mock_config_loader.get_kpi_config.return_value = mock_kpi
        
        tool = ConfigurationTool()
        result = tool._run("test_category", "test_kpi")
        result_data = json.loads(result)
        
        assert result_data["name"] == "Test KPI"
        assert result_data["description"] == "Test description"
        mock_config_loader.get_kpi_config.assert_called_once_with("test_category", "test_kpi")
    
    @patch('src.llm_agent_service.config_loader')
    def test_run_get_category_kpis(self, mock_config_loader):
        """Test getting all KPIs in a category"""
        # Mock category KPIs
        mock_kpi1 = Mock()
        mock_kpi1.dict.return_value = {"name": "KPI 1"}
        mock_kpi2 = Mock()
        mock_kpi2.dict.return_value = {"name": "KPI 2"}
        
        mock_config_loader.get_category_kpis.return_value = {
            "kpi1": mock_kpi1,
            "kpi2": mock_kpi2
        }
        
        tool = ConfigurationTool()
        result = tool._run("test_category")
        result_data = json.loads(result)
        
        assert "kpi1" in result_data
        assert "kpi2" in result_data
        assert result_data["kpi1"]["name"] == "KPI 1"
        assert result_data["kpi2"]["name"] == "KPI 2"
    
    @patch('src.llm_agent_service.config_loader')
    def test_run_kpi_not_found(self, mock_config_loader):
        """Test handling when KPI is not found"""
        mock_config_loader.get_kpi_config.return_value = None
        
        tool = ConfigurationTool()
        result = tool._run("test_category", "nonexistent_kpi")
        result_data = json.loads(result)
        
        assert "error" in result_data
        assert "not found" in result_data["error"]


class TestConversationFormatterTool:
    """Test the ConversationFormatterTool"""
    
    def test_tool_initialization(self):
        """Test tool initialization"""
        tool = ConversationFormatterTool()
        assert tool.name == "conversation_formatter_tool"
        assert "format conversation data" in tool.description.lower()
    
    def test_run_format_conversation(self):
        """Test conversation formatting"""
        tool = ConversationFormatterTool()
        
        conversation_json = json.dumps({
            "tweets": [
                {
                    "role": "Customer",
                    "text": "I have an issue",
                    "created_at": "2023-01-01T10:00:00"
                },
                {
                    "role": "Service Provider",
                    "text": "I'll help you",
                    "created_at": "2023-01-01T10:05:00"
                }
            ],
            "classification": {
                "categorization": "Support Request",
                "intent": "Help",
                "topic": "General",
                "sentiment": "Neutral"
            }
        })
        
        result = tool._run(conversation_json)
        
        # Verify formatting
        assert "CONVERSATION ANALYSIS" in result
        assert "CONVERSATION CONTEXT" in result
        assert "Support Request" in result
        assert "CONVERSATION FLOW" in result
        assert "Customer" in result
        assert "Service Provider" in result
        assert "I have an issue" in result
        assert "I'll help you" in result
    
    def test_run_format_error_handling(self):
        """Test error handling in formatting"""
        tool = ConversationFormatterTool()
        
        # Test with invalid JSON
        result = tool._run("invalid json")
        
        assert "Error formatting conversation" in result


class TestLLMAgentPerformanceAnalysisService:
    """Test the LLMAgentPerformanceAnalysisService"""
    
    @pytest.fixture
    def sample_conversation_data(self):
        """Create sample conversation data for testing"""
        tweets = [
            Tweet(tweet_id=1, author_id="customer1", role="Customer", inbound=True,
                  created_at="2023-01-01T10:00:00", text="I need help with billing"),
            Tweet(tweet_id=2, author_id="agent1", role="Service Provider", inbound=False,
                  created_at="2023-01-01T10:05:00", text="I understand your concern about billing. Let me help you resolve this.")
        ]
        
        classification = Classification(
            categorization="Billing Issue",
            intent="Support Request",
            topic="Billing",
            sentiment="Neutral"
        )
        
        return ConversationData(tweets=tweets, classification=classification)
    
    @patch('src.llm_agent_service.config_loader')
    @patch('src.llm_agent_service.ChatOpenAI')
    @patch('src.llm_agent_service.create_openai_functions_agent')
    @patch('src.llm_agent_service.AgentExecutor')
    def test_service_initialization(self, mock_executor, mock_create_agent, mock_llm, mock_config_loader):
        """Test service initialization"""
        mock_config_loader.load_config.return_value = {"test": "config"}
        
        service = LLMAgentPerformanceAnalysisService()
        
        assert service.model_name == "gpt-4"
        assert service.temperature == 0.1
        assert len(service.tools) == 3
        mock_config_loader.load_config.assert_called_once()
    
    @patch('src.llm_agent_service.config_loader')
    @patch('src.llm_agent_service.ChatOpenAI')
    @patch('src.llm_agent_service.create_openai_functions_agent')
    @patch('src.llm_agent_service.AgentExecutor')
    def test_analyze_conversation_comprehensive(self, mock_executor_class, mock_create_agent, 
                                              mock_llm, mock_config_loader, sample_conversation_data):
        """Test comprehensive conversation analysis"""
        # Setup mocks
        mock_config_loader.load_config.return_value = {"test": "config"}
        mock_executor = Mock()
        mock_executor.invoke.return_value = {
            "output": "Comprehensive analysis completed with scores and recommendations"
        }
        mock_executor_class.return_value = mock_executor
        
        service = LLMAgentPerformanceAnalysisService()
        result = service.analyze_conversation_comprehensive(sample_conversation_data)
        
        # Verify result structure
        assert "conversation_id" in result
        assert "analysis_timestamp" in result
        assert "analysis_method" in result
        assert "agent_output" in result
        assert result["analysis_method"] == "LLM-based Agent Analysis"
        assert result["model_used"] == "gpt-4"
        
        # Verify agent was called
        mock_executor.invoke.assert_called_once()
        call_args = mock_executor.invoke.call_args[0][0]
        assert "input" in call_args
        assert "comprehensive analysis" in call_args["input"].lower()
    
    @patch('src.llm_agent_service.config_loader')
    @patch('src.llm_agent_service.ChatOpenAI')
    @patch('src.llm_agent_service.create_openai_functions_agent')
    @patch('src.llm_agent_service.AgentExecutor')
    def test_analyze_conversation_kpi(self, mock_executor_class, mock_create_agent,
                                    mock_llm, mock_config_loader, sample_conversation_data):
        """Test KPI-specific conversation analysis"""
        # Setup mocks
        mock_config_loader.load_config.return_value = {"test": "config"}
        mock_executor = Mock()
        mock_executor.invoke.return_value = {
            "output": "KPI analysis completed with score and reasoning"
        }
        mock_executor_class.return_value = mock_executor
        
        service = LLMAgentPerformanceAnalysisService()
        result = service.analyze_conversation_kpi(sample_conversation_data, "empathy_communication", "empathy_score")
        
        # Verify result structure
        assert result["category"] == "empathy_communication"
        assert result["kpi"] == "empathy_score"
        assert "analysis_result" in result
        
        # Verify agent was called with correct parameters
        mock_executor.invoke.assert_called_once()
        call_args = mock_executor.invoke.call_args[0][0]
        assert "empathy_communication/empathy_score" in call_args["input"]
    
    @patch('src.llm_agent_service.config_loader')
    @patch('src.llm_agent_service.ChatOpenAI')
    @patch('src.llm_agent_service.create_openai_functions_agent')
    @patch('src.llm_agent_service.AgentExecutor')
    def test_get_available_kpis(self, mock_executor_class, mock_create_agent,
                              mock_llm, mock_config_loader):
        """Test getting available KPIs"""
        # Setup mocks
        mock_config_loader.load_config.return_value = {"test": "config"}
        mock_config_loader.get_all_categories.return_value = ["category1", "category2"]
        mock_config_loader.get_category_kpis.side_effect = [
            {"kpi1": Mock(), "kpi2": Mock()},
            {"kpi3": Mock()}
        ]
        
        service = LLMAgentPerformanceAnalysisService()
        kpis = service.get_available_kpis()
        
        assert "category1" in kpis
        assert "category2" in kpis
        assert kpis["category1"] == ["kpi1", "kpi2"]
        assert kpis["category2"] == ["kpi3"]
    
    @patch('src.llm_agent_service.config_loader')
    @patch('src.llm_agent_service.ChatOpenAI')
    @patch('src.llm_agent_service.create_openai_functions_agent')
    @patch('src.llm_agent_service.AgentExecutor')
    def test_validate_configuration(self, mock_executor_class, mock_create_agent,
                                  mock_llm, mock_config_loader):
        """Test configuration validation"""
        # Setup mocks
        mock_config_loader.load_config.return_value = {"test": "config"}
        mock_executor = Mock()
        mock_executor.invoke.return_value = {
            "output": "Configuration validation completed successfully"
        }
        mock_executor_class.return_value = mock_executor
        
        service = LLMAgentPerformanceAnalysisService()
        result = service.validate_configuration()
        
        assert "validation_timestamp" in result
        assert "validation_method" in result
        assert result["validation_method"] == "LLM-based Agent Validation"
        assert "result" in result
        
        # Verify agent was called for validation
        mock_executor.invoke.assert_called_once()
        call_args = mock_executor.invoke.call_args[0][0]
        assert "validate the current KPI configuration" in call_args["input"]
    
    @patch('src.llm_agent_service.config_loader')
    def test_initialization_config_error(self, mock_config_loader):
        """Test initialization with configuration error"""
        mock_config_loader.load_config.side_effect = Exception("Config error")
        
        with pytest.raises(Exception):
            LLMAgentPerformanceAnalysisService()
    
    @patch('src.llm_agent_service.config_loader')
    @patch('src.llm_agent_service.ChatOpenAI')
    @patch('src.llm_agent_service.create_openai_functions_agent')
    @patch('src.llm_agent_service.AgentExecutor')
    def test_error_handling_in_comprehensive_analysis(self, mock_executor_class, mock_create_agent,
                                                    mock_llm, mock_config_loader, sample_conversation_data):
        """Test error handling in comprehensive analysis"""
        # Setup mocks
        mock_config_loader.load_config.return_value = {"test": "config"}
        mock_executor = Mock()
        mock_executor.invoke.side_effect = Exception("Agent error")
        mock_executor_class.return_value = mock_executor
        
        service = LLMAgentPerformanceAnalysisService()
        result = service.analyze_conversation_comprehensive(sample_conversation_data)
        
        # Should return error information instead of raising
        assert "error" in result
        assert "Agent error" in result["error"]
        assert "conversation_id" in result
        assert "analysis_timestamp" in result


class TestFactoryFunction:
    """Test the factory function"""
    
    @patch('src.llm_agent_service.LLMAgentPerformanceAnalysisService')
    def test_get_llm_agent_service_default(self, mock_service_class):
        """Test factory function with default parameters"""
        mock_service = Mock()
        mock_service_class.return_value = mock_service
        
        result = get_llm_agent_service()
        
        mock_service_class.assert_called_once_with(model_name="gpt-4", temperature=0.1)
        assert result == mock_service
    
    @patch('src.llm_agent_service.LLMAgentPerformanceAnalysisService')
    def test_get_llm_agent_service_custom(self, mock_service_class):
        """Test factory function with custom parameters"""
        mock_service = Mock()
        mock_service_class.return_value = mock_service
        
        result = get_llm_agent_service(model_name="gpt-3.5-turbo", temperature=0.5)
        
        mock_service_class.assert_called_once_with(model_name="gpt-3.5-turbo", temperature=0.5)
        assert result == mock_service


class TestIntegration:
    """Integration tests for the LLM agent system"""
    
    @pytest.fixture
    def conversation_with_empathy(self):
        """Create conversation data showing good empathy"""
        tweets = [
            Tweet(tweet_id=1, author_id="customer1", role="Customer", inbound=True,
                  created_at="2023-01-01T10:00:00", 
                  text="I'm really frustrated with this billing error. It's been going on for weeks!"),
            Tweet(tweet_id=2, author_id="agent1", role="Service Provider", inbound=False,
                  created_at="2023-01-01T10:03:00",
                  text="I completely understand your frustration, and I sincerely apologize for the ongoing billing issue. That must be really stressful for you. Let me personally ensure we resolve this right now."),
            Tweet(tweet_id=3, author_id="customer1", role="Customer", inbound=True,
                  created_at="2023-01-01T10:15:00",
                  text="Thank you so much! You've been incredibly helpful and understanding.")
        ]
        
        classification = Classification(
            categorization="Billing Issue",
            intent="Support Request", 
            topic="Billing",
            sentiment="Positive"
        )
        
        return ConversationData(tweets=tweets, classification=classification)
    
    def test_tool_integration(self):
        """Test that tools work together properly"""
        # Test conversation formatter with configuration tool
        formatter = ConversationFormatterTool()
        config_tool = ConfigurationTool()
        
        # Create test data
        conversation_json = json.dumps({
            "tweets": [{"role": "Customer", "text": "Test", "created_at": "2023-01-01"}],
            "classification": {"categorization": "Test", "intent": "Test", "topic": "Test", "sentiment": "Neutral"}
        })
        
        # Format conversation
        formatted = formatter._run(conversation_json)
        assert "CONVERSATION ANALYSIS" in formatted
        assert "Test" in formatted
        
        # The configuration tool would typically be mocked in real integration tests
        # since it depends on actual configuration files
    
    @patch('src.llm_agent_service.config_loader')
    @patch('src.llm_agent_service.ChatOpenAI')  
    @patch('src.llm_agent_service.create_openai_functions_agent')
    @patch('src.llm_agent_service.AgentExecutor')
    def test_end_to_end_mock_analysis(self, mock_executor_class, mock_create_agent,
                                    mock_llm, mock_config_loader, conversation_with_empathy):
        """Test end-to-end analysis flow with mocked components"""
        # Setup comprehensive mocks
        mock_config_loader.load_config.return_value = {
            "evaluation_framework": {
                "categories": {
                    "empathy_communication": {
                        "kpis": {
                            "empathy_score": {
                                "name": "Empathy Score",
                                "description": "Measure empathy in responses"
                            }
                        }
                    }
                }
            }
        }
        mock_config_loader.get_all_categories.return_value = ["empathy_communication"]
        mock_config_loader.get_category_kpis.return_value = {"empathy_score": Mock()}
        
        # Mock agent execution with realistic response
        mock_executor = Mock()
        mock_executor.invoke.return_value = {
            "output": json.dumps({
                "empathy_communication": {
                    "empathy_score": {
                        "score": 9.2,
                        "meets_target": True,
                        "reasoning": "Excellent empathetic response with acknowledgment of feelings",
                        "evidence": ["I completely understand your frustration", "sincerely apologize"],
                        "recommendations": ["Continue this excellent empathetic approach"]
                    }
                },
                "overall_assessment": "Excellent performance in empathy and communication"
            })
        }
        mock_executor_class.return_value = mock_executor
        
        # Create service and run analysis
        service = LLMAgentPerformanceAnalysisService()
        result = service.analyze_conversation_comprehensive(conversation_with_empathy)
        
        # Verify results
        assert "conversation_id" in result
        assert "analysis_method" in result
        assert result["analysis_method"] == "LLM-based Agent Analysis"
        assert "agent_output" in result
        
        # Verify agent was called appropriately
        mock_executor.invoke.assert_called_once()
        call_args = mock_executor.invoke.call_args[0][0]
        assert "comprehensive analysis" in call_args["input"].lower()
        assert "conversation data" in call_args["input"].lower()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
