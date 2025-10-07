"""
Tests for SAP AI Core integration
"""

import pytest
import json
import tempfile
import os
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path

from src.aicore_service import (
    AICoreAuthenticator, 
    AICoreClient, 
    AICoreCredentialsLoader,
    get_aicore_client
)
from src.aicore_langchain import AICoreChat, create_aicore_chat_model
from langchain.schema import HumanMessage, AIMessage


@pytest.fixture
def mock_credentials():
    """Mock credentials for testing"""
    return {
        'oauth': {
            'clientid': 'test-client-id',
            'clientsecret': 'test-client-secret',
            'url': 'https://test-auth.example.com'
        },
        'services': {
            'ai_api_url': 'https://test-ai-api.example.com'
        },
        'model': {
            'default_model': 'gpt-4',
            'temperature': 0.1,
            'max_tokens': 4000
        },
        'security': {
            'verify_ssl': True,
            'token_refresh': {
                'refresh_buffer': 300,
                'max_retries': 3
            }
        },
        'logging': {
            'enable_request_logging': False
        }
    }


@pytest.fixture
def mock_credentials_file(mock_credentials):
    """Create a temporary credentials file for testing"""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
        import yaml
        yaml.dump({'aicore': mock_credentials}, f)
        yield f.name
    os.unlink(f.name)


class TestAICoreAuthenticator:
    """Test AI Core authentication"""
    
    def test_init(self, mock_credentials):
        """Test authenticator initialization"""
        auth = AICoreAuthenticator(mock_credentials)
        
        assert auth.client_id == 'test-client-id'
        assert auth.client_secret == 'test-client-secret'
        assert auth.auth_url == 'https://test-auth.example.com'
        assert auth.access_token is None
        assert auth.token_expires_at is None
    
    @patch('requests.post')
    def test_refresh_token_success(self, mock_post, mock_credentials):
        """Test successful token refresh"""
        # Mock successful response
        mock_response = Mock()
        mock_response.raise_for_status.return_value = None
        mock_response.json.return_value = {
            'access_token': 'test-token',
            'expires_in': 3600
        }
        mock_post.return_value = mock_response
        
        auth = AICoreAuthenticator(mock_credentials)
        token = auth._refresh_token()
        
        assert token == 'test-token'
        assert auth.access_token == 'test-token'
        assert auth.token_expires_at is not None
        
        # Verify request was made correctly
        mock_post.assert_called_once()
        call_args = mock_post.call_args
        assert 'oauth/token' in call_args[0][0]
        assert call_args[1]['data']['grant_type'] == 'client_credentials'
    
    @patch('requests.post')
    def test_refresh_token_failure(self, mock_post, mock_credentials):
        """Test token refresh failure"""
        mock_post.side_effect = Exception("Network error")
        
        auth = AICoreAuthenticator(mock_credentials)
        
        with pytest.raises(Exception, match="Failed to authenticate with AI Core"):
            auth._refresh_token()
    
    def test_is_token_valid(self, mock_credentials):
        """Test token validity check"""
        from datetime import datetime, timedelta
        
        auth = AICoreAuthenticator(mock_credentials)
        
        # No token
        assert not auth._is_token_valid()
        
        # Valid token
        auth.access_token = 'test-token'
        auth.token_expires_at = datetime.now() + timedelta(hours=1)
        assert auth._is_token_valid()
        
        # Expired token
        auth.token_expires_at = datetime.now() - timedelta(hours=1)
        assert not auth._is_token_valid()


class TestAICoreClient:
    """Test AI Core client"""
    
    @patch('src.aicore_service.AICoreAuthenticator')
    def test_init(self, mock_auth, mock_credentials):
        """Test client initialization"""
        client = AICoreClient(mock_credentials)
        
        assert client.ai_api_url == 'https://test-ai-api.example.com'
        assert client.default_model == 'gpt-4'
        assert client.temperature == 0.1
        assert client.max_tokens == 4000
        mock_auth.assert_called_once_with(mock_credentials)
    
    @patch('requests.post')
    def test_chat_completion_success(self, mock_post, mock_credentials):
        """Test successful chat completion"""
        # Mock authenticator
        mock_auth = Mock()
        mock_auth.get_access_token.return_value = 'test-token'
        
        # Mock successful API response
        mock_response = Mock()
        mock_response.raise_for_status.return_value = None
        mock_response.json.return_value = {
            'choices': [{'message': {'content': 'Test response'}}]
        }
        mock_post.return_value = mock_response
        
        with patch('src.aicore_service.AICoreAuthenticator', return_value=mock_auth):
            client = AICoreClient(mock_credentials)
            
            messages = [{'role': 'user', 'content': 'Test message'}]
            result = client.chat_completion(messages)
            
            assert result['choices'][0]['message']['content'] == 'Test response'
            
            # Verify request
            mock_post.assert_called_once()
            call_args = mock_post.call_args
            assert 'chat/completions' in call_args[0][0]
            assert call_args[1]['headers']['Authorization'] == 'Bearer test-token'
    
    @patch('requests.post')
    def test_chat_completion_failure(self, mock_post, mock_credentials):
        """Test chat completion failure"""
        # Mock authenticator
        mock_auth = Mock()
        mock_auth.get_access_token.return_value = 'test-token'
        
        # Mock failed API response
        mock_post.side_effect = Exception("API error")
        
        with patch('src.aicore_service.AICoreAuthenticator', return_value=mock_auth):
            client = AICoreClient(mock_credentials)
            
            messages = [{'role': 'user', 'content': 'Test message'}]
            
            with pytest.raises(Exception, match="AI Core API request failed"):
                client.chat_completion(messages)
    
    @patch('requests.get')
    def test_get_available_models(self, mock_get, mock_credentials):
        """Test getting available models"""
        # Mock authenticator
        mock_auth = Mock()
        mock_auth.get_access_token.return_value = 'test-token'
        
        # Mock successful response
        mock_response = Mock()
        mock_response.raise_for_status.return_value = None
        mock_response.json.return_value = {
            'data': [{'id': 'gpt-4'}, {'id': 'gpt-3.5-turbo'}]
        }
        mock_get.return_value = mock_response
        
        with patch('src.aicore_service.AICoreAuthenticator', return_value=mock_auth):
            client = AICoreClient(mock_credentials)
            models = client.get_available_models()
            
            assert len(models) == 2
            assert models[0]['id'] == 'gpt-4'
    
    def test_health_check_healthy(self, mock_credentials):
        """Test health check when healthy"""
        with patch.object(AICoreClient, 'get_available_models', return_value=[{'id': 'gpt-4'}]):
            client = AICoreClient(mock_credentials)
            health = client.health_check()
            
            assert health['status'] == 'healthy'
            assert health['available_models_count'] == 1
    
    def test_health_check_unhealthy(self, mock_credentials):
        """Test health check when unhealthy"""
        with patch.object(AICoreClient, 'get_available_models', side_effect=Exception("Connection failed")):
            client = AICoreClient(mock_credentials)
            health = client.health_check()
            
            assert health['status'] == 'unhealthy'
            assert 'Connection failed' in health['error']


class TestAICoreCredentialsLoader:
    """Test credentials loader"""
    
    def test_load_credentials_success(self, mock_credentials_file):
        """Test successful credentials loading"""
        loader = AICoreCredentialsLoader(mock_credentials_file)
        credentials = loader.load_credentials()
        
        assert credentials['oauth']['clientid'] == 'test-client-id'
        assert credentials['services']['ai_api_url'] == 'https://test-ai-api.example.com'
    
    def test_load_credentials_file_not_found(self):
        """Test loading non-existent credentials file"""
        loader = AICoreCredentialsLoader('/nonexistent/path.yaml')
        
        with pytest.raises(FileNotFoundError):
            loader.load_credentials()
    
    def test_validate_credentials_missing_field(self):
        """Test credentials validation with missing fields"""
        invalid_credentials = {
            'aicore': {
                'oauth': {
                    'clientid': 'test-id'
                    # Missing clientsecret, url
                }
                # Missing services
            }
        }
        
        loader = AICoreCredentialsLoader()
        
        with pytest.raises(ValueError, match="Missing required credential field"):
            loader._validate_credentials(invalid_credentials)


class TestAICoreLangChain:
    """Test LangChain integration"""
    
    @patch('src.aicore_langchain.get_aicore_client')
    def test_aicore_chat_init(self, mock_get_client):
        """Test AICoreChat initialization"""
        mock_client = Mock()
        mock_get_client.return_value = mock_client
        
        chat = AICoreChat(model_name="gpt-4", temperature=0.2)
        
        assert chat.model_name == "gpt-4"
        assert chat.temperature == 0.2
        assert chat._llm_type == "aicore-chat"
        mock_get_client.assert_called_once()
    
    @patch('src.aicore_langchain.get_aicore_client')
    def test_convert_messages_to_aicore_format(self, mock_get_client):
        """Test message conversion"""
        mock_client = Mock()
        mock_get_client.return_value = mock_client
        
        chat = AICoreChat()
        
        messages = [
            HumanMessage(content="Hello"),
            AIMessage(content="Hi there")
        ]
        
        converted = chat._convert_messages_to_aicore_format(messages)
        
        assert len(converted) == 2
        assert converted[0] == {"role": "user", "content": "Hello"}
        assert converted[1] == {"role": "assistant", "content": "Hi there"}
    
    @patch('src.aicore_langchain.get_aicore_client')
    def test_generate_success(self, mock_get_client):
        """Test successful generation"""
        mock_client = Mock()
        mock_client.chat_completion.return_value = {
            'choices': [{'message': {'content': 'Generated response'}}]
        }
        mock_get_client.return_value = mock_client
        
        chat = AICoreChat()
        messages = [HumanMessage(content="Test")]
        
        result = chat._generate(messages)
        
        assert len(result.generations) == 1
        assert result.generations[0].message.content == 'Generated response'
        mock_client.chat_completion.assert_called_once()
    
    @patch('src.aicore_langchain.get_aicore_client')
    def test_generate_error(self, mock_get_client):
        """Test generation with error"""
        mock_client = Mock()
        mock_client.chat_completion.side_effect = Exception("API error")
        mock_get_client.return_value = mock_client
        
        chat = AICoreChat()
        messages = [HumanMessage(content="Test")]
        
        result = chat._generate(messages)
        
        assert len(result.generations) == 1
        assert "Error: Unable to generate response" in result.generations[0].message.content
    
    def test_create_aicore_chat_model(self):
        """Test factory function"""
        with patch('src.aicore_langchain.AICoreChat') as mock_chat:
            create_aicore_chat_model(
                model_name="gpt-3.5-turbo",
                temperature=0.5,
                max_tokens=2000
            )
            
            mock_chat.assert_called_once_with(
                model_name="gpt-3.5-turbo",
                temperature=0.5,
                max_tokens=2000,
                credentials_path=None
            )


class TestIntegration:
    """Integration tests"""
    
    @patch('src.aicore_service.requests.post')
    @patch('src.aicore_service.requests.get')
    def test_end_to_end_flow(self, mock_get, mock_post, mock_credentials_file):
        """Test end-to-end flow"""
        # Mock token refresh
        mock_token_response = Mock()
        mock_token_response.raise_for_status.return_value = None
        mock_token_response.json.return_value = {
            'access_token': 'test-token',
            'expires_in': 3600
        }
        
        # Mock chat completion
        mock_chat_response = Mock()
        mock_chat_response.raise_for_status.return_value = None
        mock_chat_response.json.return_value = {
            'choices': [{'message': {'content': 'Analysis complete'}}]
        }
        
        # Mock models endpoint
        mock_models_response = Mock()
        mock_models_response.raise_for_status.return_value = None
        mock_models_response.json.return_value = {
            'data': [{'id': 'gpt-4'}]
        }
        
        def mock_requests(*args, **kwargs):
            if 'oauth/token' in args[0]:
                return mock_token_response
            elif 'chat/completions' in args[0]:
                return mock_chat_response
            else:
                return mock_models_response
        
        mock_post.side_effect = mock_requests
        mock_get.return_value = mock_models_response
        
        # Test the flow
        from src.aicore_service import AICoreCredentialsLoader, AICoreClient
        
        loader = AICoreCredentialsLoader(mock_credentials_file)
        credentials = loader.load_credentials()
        client = AICoreClient(credentials)
        
        # Test health check
        health = client.health_check()
        assert health['status'] == 'healthy'
        
        # Test chat completion
        messages = [{'role': 'user', 'content': 'Analyze this conversation'}]
        result = client.chat_completion(messages)
