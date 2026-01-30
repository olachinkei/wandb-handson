"""
Weave Handson Test Suite

テスト実行方法:
    uv run pytest tests/test.py -v

APIキーなしで実行（モックテストのみ）:
    uv run pytest tests/test.py -v -m "not requires_api"
"""

import os
import sys
import json
import ast
import asyncio
from pathlib import Path
from unittest.mock import patch, MagicMock, AsyncMock
import pytest

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / "jp"))

# Project root
PROJECT_ROOT = Path(__file__).parent.parent


# =============================================================================
# Fixtures
# =============================================================================

@pytest.fixture
def sample_dataset():
    """Sample dataset for testing."""
    return [
        {"question": "What is 2+2?", "expected": "4"},
        {"question": "What is the capital of Japan?", "expected": "Tokyo"},
    ]


@pytest.fixture
def sample_qa_pairs():
    """Q&A pairs for evaluation testing."""
    return [
        {"question": "What is Python?", "expected": "programming language", "answer": "Python is a programming language."},
        {"question": "What is 1+1?", "expected": "2", "answer": "The answer is 2."},
        {"question": "Who is Einstein?", "expected": "physicist", "answer": "Albert Einstein was a famous physicist."},
    ]


@pytest.fixture
def assets_file(tmp_path):
    """Create a temporary assets file."""
    assets = {
        "prompts": {"test": "weave:///test/project/object/test:abc123"},
        "datasets": {"test": "weave:///test/project/object/test:abc123"},
        "models": {"test": "weave:///test/project/object/test:abc123"},
        "scorers": {"test": "weave:///test/project/object/test:abc123"},
    }
    assets_path = tmp_path / "assets.json"
    json.dump(assets, open(assets_path, 'w'))
    return assets_path


@pytest.fixture
def mock_chat_response():
    """Mock chat response."""
    mock_response = MagicMock()
    mock_response.choices = [MagicMock()]
    mock_response.choices[0].message.content = "Test response"
    return mock_response


# =============================================================================
# Test Project Structure
# =============================================================================

class TestProjectStructure:
    """Test project structure and files."""
    
    def test_directories_exist(self):
        """Test required directories exist."""
        assert (PROJECT_ROOT / "jp").exists()
        assert (PROJECT_ROOT / "en").exists()
        assert (PROJECT_ROOT / "tests").exists()

    def test_config_files_exist(self):
        """Test config files exist."""
        assert (PROJECT_ROOT / "pyproject.toml").exists()
        assert (PROJECT_ROOT / "README.md").exists()
        assert (PROJECT_ROOT / "config.yaml").exists()
        assert (PROJECT_ROOT / "assets.json").exists()

    def test_jp_scripts_exist(self):
        """Test all Japanese scripts exist."""
        jp_dir = PROJECT_ROOT / "jp"
        
        scripts = [
            "config_loader.py",
            "1_1_0_basic_trace.py",
            "1_2_1_agent_sdk.py",
            "1_2_2_multimodal.py",
            "1_3_advanced_trace.py",
            "1_4_playground.py",
            "2_1_prompt.py",
            "2_2_dataset.py",
            "2_3_model.py",
            "2_4_score.py",
            "2_5_call.py",
            "3_1_offline_evaluation.py",
            "3_2_evaluation_logger.py",
            "3_3_online_feedback.py",
            "3_4_guardrail_monitoring.py",
        ]
        
        for script in scripts:
            assert (jp_dir / script).exists(), f"{script} should exist"

    def test_jp_scripts_valid_syntax(self):
        """Test all JP scripts have valid Python syntax."""
        jp_dir = PROJECT_ROOT / "jp"
        
        for py_file in jp_dir.glob("*.py"):
            with open(py_file) as f:
                source = f.read()
            try:
                ast.parse(source)
            except SyntaxError as e:
                pytest.fail(f"{py_file.name} has syntax error: {e}")


# =============================================================================
# Test Config
# =============================================================================

class TestConfig:
    """Test configuration files and loaders."""
    
    def test_config_yaml_structure(self):
        """Test config.yaml structure."""
        import yaml
        
        with open(PROJECT_ROOT / "config.yaml") as f:
            config = yaml.safe_load(f)
        
        assert "provider" in config
        assert config["provider"] in ["openai", "gemini"]
        assert "openai" in config
        assert "gemini" in config
        assert "model" in config["openai"]
        assert "model" in config["gemini"]

    def test_config_yaml_defaults(self):
        """Test config.yaml has reasonable defaults."""
        import yaml
        
        with open(PROJECT_ROOT / "config.yaml") as f:
            config = yaml.safe_load(f)
        
        assert "default_temperature" in config
        assert 0 <= config["default_temperature"] <= 1
        assert "default_max_tokens" in config
        assert config["default_max_tokens"] > 0

    def test_config_loader_functions(self):
        """Test config_loader functions."""
        from config_loader import load_config, get_model_name, get_temperature, get_max_tokens
        
        config = load_config()
        assert isinstance(config, dict)
        
        model = get_model_name()
        assert isinstance(model, str)
        assert len(model) > 0
        
        temp = get_temperature()
        assert isinstance(temp, float)
        assert 0 <= temp <= 2
        
        tokens = get_max_tokens()
        assert isinstance(tokens, int)
        assert tokens > 0


# =============================================================================
# Test Scorer Logic
# =============================================================================

class TestScorerLogic:
    """Test scorer implementations."""
    
    def test_exact_match_scorer(self):
        """Test exact match scoring."""
        def exact_match(expected: str, output: dict) -> dict:
            generated = output.get('answer', '')
            return {'exact_match': expected.lower().strip() in generated.lower().strip()}
        
        # Positive cases
        assert exact_match("Paris", {"answer": "Paris"})['exact_match'] == True
        assert exact_match("Paris", {"answer": "paris"})['exact_match'] == True
        assert exact_match("Paris", {"answer": "The answer is Paris."})['exact_match'] == True
        
        # Negative cases
        assert exact_match("Paris", {"answer": "London"})['exact_match'] == False
        assert exact_match("Paris", {"answer": ""})['exact_match'] == False

    def test_contains_answer_scorer(self):
        """Test contains answer scoring."""
        def contains_answer(expected: str, output: dict) -> dict:
            generated = output.get('answer', '')
            return {'contains_answer': expected.lower() in generated.lower()}
        
        assert contains_answer("Paris", {"answer": "The capital is Paris."})['contains_answer'] == True
        assert contains_answer("paris", {"answer": "PARIS is beautiful"})['contains_answer'] == True
        assert contains_answer("Paris", {"answer": "London"})['contains_answer'] == False

    def test_length_scorer(self):
        """Test length scoring."""
        def length_score(output: str, min_len: int = 10, max_len: int = 500) -> dict:
            text = output if isinstance(output, str) else str(output)
            length = len(text)
            return {
                'length': length,
                'is_appropriate': min_len <= length <= max_len
            }
        
        result = length_score("This is a test response.", min_len=5, max_len=50)
        assert result['is_appropriate'] == True
        assert result['length'] == 24
        
        result = length_score("Hi", min_len=10, max_len=100)
        assert result['is_appropriate'] == False
        assert result['length'] == 2

    def test_toxicity_check(self):
        """Test toxicity keyword detection."""
        keywords = ["hate", "violence", "harmful"]
        
        def check_toxicity(text: str) -> dict:
            flagged = [kw for kw in keywords if kw in text.lower()]
            return {'is_safe': len(flagged) == 0, 'flagged': flagged}
        
        result = check_toxicity("This is helpful content")
        assert result['is_safe'] == True
        assert result['flagged'] == []
        
        result = check_toxicity("I hate this thing")
        assert result['is_safe'] == False
        assert "hate" in result['flagged']

    def test_json_validator(self):
        """Test JSON validation scoring."""
        def validate_json(output: str) -> dict:
            try:
                json.loads(output)
                return {'is_valid_json': True}
            except:
                return {'is_valid_json': False}
        
        assert validate_json('{"key": "value"}')['is_valid_json'] == True
        assert validate_json('{"nested": {"a": 1}}')['is_valid_json'] == True
        assert validate_json('Not JSON')['is_valid_json'] == False
        assert validate_json('{invalid}')['is_valid_json'] == False

    def test_quality_scorer(self, sample_qa_pairs):
        """Test quality scoring with sample data."""
        def quality_score(answer: str, expected: str) -> dict:
            contains = expected.lower() in answer.lower()
            length_ok = 10 <= len(answer) <= 500
            return {
                'contains_expected': contains,
                'length_ok': length_ok,
                'overall_quality': contains and length_ok
            }
        
        for pair in sample_qa_pairs:
            result = quality_score(pair['answer'], pair['expected'])
            assert result['contains_expected'] == True
            assert result['length_ok'] == True
            assert result['overall_quality'] == True


# =============================================================================
# Test Data Structures
# =============================================================================

class TestDataStructures:
    """Test data structure handling."""
    
    def test_dataset_structure(self, sample_dataset):
        """Test dataset structure."""
        for row in sample_dataset:
            assert "question" in row
            assert "expected" in row
            assert isinstance(row["question"], str)
            assert isinstance(row["expected"], str)

    def test_assets_file_structure(self, assets_file):
        """Test assets file structure."""
        assets = json.load(open(assets_file))
        
        required_keys = ["prompts", "datasets", "models", "scorers"]
        for key in required_keys:
            assert key in assets
            assert isinstance(assets[key], dict)

    def test_assets_file_exists(self):
        """Test assets.json exists in project."""
        assets_path = PROJECT_ROOT / "assets.json"
        assert assets_path.exists()
        
        assets = json.load(open(assets_path))
        assert isinstance(assets, dict)

    def test_weave_ref_format(self, assets_file):
        """Test Weave reference format."""
        assets = json.load(open(assets_file))
        
        for asset_type, items in assets.items():
            for name, ref in items.items():
                assert ref.startswith("weave:///")
                assert ":" in ref  # Should have version


# =============================================================================
# Test Utilities
# =============================================================================

class TestUtilities:
    """Test utility functions."""
    
    def test_json_parsing(self):
        """Test JSON parsing."""
        valid = '{"answer": "Paris", "score": 0.95}'
        result = json.loads(valid)
        assert result["answer"] == "Paris"
        assert result["score"] == 0.95
        
        with pytest.raises(json.JSONDecodeError):
            json.loads('Not JSON')

    def test_bleu_like_score(self):
        """Test BLEU-like scoring."""
        def bleu_like(expected: str, generated: str) -> float:
            exp_tokens = set(expected.lower().split())
            gen_tokens = set(generated.lower().split())
            if not exp_tokens or not gen_tokens:
                return 0.0
            common = exp_tokens & gen_tokens
            precision = len(common) / len(gen_tokens)
            recall = len(common) / len(exp_tokens)
            if precision + recall == 0:
                return 0.0
            return 2 * precision * recall / (precision + recall)
        
        assert bleu_like("hello world", "hello world") == 1.0
        assert 0 < bleu_like("hello world", "hello there") < 1
        assert bleu_like("hello world", "goodbye moon") == 0.0
        assert bleu_like("", "test") == 0.0

    def test_save_and_load_assets(self, tmp_path):
        """Test saving and loading assets."""
        assets_path = tmp_path / "test_assets.json"
        
        # Save
        assets = {"prompts": {"test": "weave:///a/b/c:123"}}
        json.dump(assets, open(assets_path, 'w'))
        
        # Load
        loaded = json.load(open(assets_path))
        assert loaded["prompts"]["test"] == "weave:///a/b/c:123"


# =============================================================================
# Test Mock Integrations
# =============================================================================

class TestMockIntegrations:
    """Test with mocked external services."""
    
    def test_mock_openai_chat(self, mock_chat_response):
        """Test mocked OpenAI chat completion."""
        with patch('openai.OpenAI') as mock_client:
            mock_instance = MagicMock()
            mock_client.return_value = mock_instance
            mock_instance.chat.completions.create.return_value = mock_chat_response
            
            client = mock_client()
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": "test"}],
            )
            
            assert response.choices[0].message.content == "Test response"

    def test_mock_weave_init(self):
        """Test mocked weave init."""
        with patch('weave.init') as mock_init:
            mock_init.return_value = MagicMock()
            import weave
            result = weave.init()
            mock_init.assert_called_once()

    def test_mock_weave_publish(self):
        """Test mocked weave publish."""
        with patch('weave.publish') as mock_publish:
            mock_ref = MagicMock()
            mock_ref.uri.return_value = "weave:///test/project/object/test:abc123"
            mock_publish.return_value = mock_ref
            
            import weave
            ref = weave.publish({"test": "data"}, name="test")
            assert ref.uri() == "weave:///test/project/object/test:abc123"

    def test_mock_weave_op(self):
        """Test mocked weave.op decorator."""
        with patch('weave.op') as mock_op:
            mock_op.return_value = lambda f: f
            
            @mock_op()
            def test_function(x):
                return x * 2
            
            assert test_function(5) == 10

    def test_mock_chat_completion_helper(self):
        """Test mocked chat_completion helper."""
        with patch('config_loader.chat_completion') as mock_chat:
            mock_chat.return_value = "Mocked response"
            
            from config_loader import chat_completion
            result = chat_completion([{"role": "user", "content": "test"}])
            assert result == "Mocked response"


# =============================================================================
# Test Async Functions
# =============================================================================

class TestAsyncFunctions:
    """Test async functionality."""
    
    @pytest.mark.asyncio
    async def test_async_scoring(self):
        """Test async scoring function."""
        async def async_score(output: str) -> dict:
            await asyncio.sleep(0.01)  # Simulate async work
            return {"score": len(output) / 100}
        
        result = await async_score("Test output")
        assert "score" in result
        assert result["score"] == 0.11

    @pytest.mark.asyncio
    async def test_async_batch_processing(self, sample_dataset):
        """Test async batch processing."""
        async def process_item(item: dict) -> dict:
            await asyncio.sleep(0.01)
            return {"question": item["question"], "processed": True}
        
        tasks = [process_item(item) for item in sample_dataset]
        results = await asyncio.gather(*tasks)
        
        assert len(results) == len(sample_dataset)
        for result in results:
            assert result["processed"] == True


# =============================================================================
# Test Edge Cases
# =============================================================================

class TestEdgeCases:
    """Test edge cases and error handling."""
    
    def test_empty_input(self):
        """Test handling of empty inputs."""
        def safe_score(output: str) -> dict:
            if not output:
                return {"score": 0, "error": "Empty input"}
            return {"score": len(output)}
        
        result = safe_score("")
        assert result["score"] == 0
        assert "error" in result

    def test_none_input(self):
        """Test handling of None inputs."""
        def safe_process(text):
            if text is None:
                return ""
            return str(text)
        
        assert safe_process(None) == ""
        assert safe_process("test") == "test"

    def test_unicode_handling(self):
        """Test unicode text handling."""
        def process_text(text: str) -> dict:
            return {"length": len(text), "text": text}
        
        result = process_text("日本語テスト")
        assert result["length"] == 6
        
        result = process_text("🎉 Emoji test 🎊")
        assert "🎉" in result["text"]

    def test_large_input(self):
        """Test handling of large inputs."""
        def truncate(text: str, max_len: int = 1000) -> str:
            if len(text) > max_len:
                return text[:max_len] + "..."
            return text
        
        large_text = "x" * 5000
        result = truncate(large_text)
        assert len(result) == 1003  # 1000 + "..."

    def test_special_characters(self):
        """Test handling of special characters."""
        def sanitize(text: str) -> str:
            return text.replace("\n", " ").replace("\t", " ").strip()
        
        result = sanitize("Hello\n\tWorld")
        assert result == "Hello  World"


# =============================================================================
# Integration Tests (Requires API)
# =============================================================================

@pytest.mark.requires_api
class TestIntegration:
    """Integration tests requiring API keys."""
    
    def test_weave_init(self):
        """Test weave initialization."""
        import weave
        from dotenv import load_dotenv
        load_dotenv()
        project_name = f"{os.getenv('WANDB_ENTITY')}/{os.getenv('WANDB_PROJECT', 'weave-handson')}"
        try:
            weave.init(project_name)
            assert True
        except Exception as e:
            pytest.fail(f"Weave init failed: {e}")

    def test_openai_connection(self):
        """Test OpenAI connection."""
        import openai
        client = openai.OpenAI()
        
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": "Say 'test'"}],
            max_tokens=10,
        )
        assert len(response.choices) > 0

    def test_config_loader_chat_completion(self):
        """Test chat completion via config_loader."""
        from config_loader import chat_completion
        
        result = chat_completion([
            {"role": "user", "content": "Say 'hello'"}
        ], max_tokens=10)
        
        assert isinstance(result, str)
        assert len(result) > 0


# =============================================================================
# Main
# =============================================================================

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
