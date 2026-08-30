# tests/test_python_extractor.py
import pytest
from codeatlas_contracts.enums import SupportedLanguage
from codeatlas_graph_schema.labels import NodeLabel
from codeatlas_graph_schema.relationships import RelationshipType
from codeatlas_analyzer.parser.registry import ParserRegistry
from codeatlas_analyzer.parser.models import ParsedSourceTree
from codeatlas_analyzer.extraction.python import PythonExtractor

SAMPLE_PYTHON_CODE = b'''
import os

def top_level_func(a: int, b: int) -> int:
    return a + b

@decorator
class AuthService:
    def __init__(self, token: str):
        self.token = token

    def authenticate(self) -> bool:
        return True
'''

@pytest.fixture
def parser_registry():
    return ParserRegistry()

def test_python_extraction_entities_and_relationships(parser_registry):
    parser = parser_registry.get_parser(SupportedLanguage.PYTHON)
    tree = parser.parse(SAMPLE_PYTHON_CODE)
    
    parsed_tree = ParsedSourceTree(
        relative_path="src/auth/service.py",
        language=SupportedLanguage.PYTHON,
        source_bytes=SAMPLE_PYTHON_CODE,
        tree=tree,
        is_parsed=True,
    )
    
    extractor = PythonExtractor()
    snapshot_id = "snap-test-001"
    result = extractor.extract(parsed_tree, snapshot_id)
    
    # 1 File + 1 Function + 1 Class + 2 Methods = 5 entities
    assert len(result.entities) == 5
    
    # Check File entity
    file_entity = next(e for e in result.entities if e.label == NodeLabel.FILE)
    assert file_entity.id == "snap-test-001:src/auth/service.py"
    assert file_entity.name == "service.py"
    
    # Check Function entity
    func_entity = next(e for e in result.entities if e.name == "top_level_func")
    assert func_entity.label == NodeLabel.FUNCTION
    assert func_entity.id == "snap-test-001:src/auth/service.py#top_level_func"
    assert func_entity.start_line == 4
    
    # Check Class entity
    class_entity = next(e for e in result.entities if e.name == "AuthService")
    assert class_entity.label == NodeLabel.CLASS
    assert class_entity.id == "snap-test-001:src/auth/service.py#AuthService"
    assert class_entity.start_line == 7  # Includes decorator
    
    # Check Method entities
    methods = [e for e in result.entities if e.label == NodeLabel.METHOD]
    assert len(methods) == 2
    method_names = {m.name for m in methods}
    assert method_names == {"__init__", "authenticate"}
    
    auth_method = next(m for m in methods if m.name == "authenticate")
    assert auth_method.qualified_name == "AuthService.authenticate"
    assert auth_method.id == "snap-test-001:src/auth/service.py#AuthService.authenticate"
    
    # Check Relationships (File -> top_level_func, File -> AuthService, AuthService -> __init__, AuthService -> authenticate)
    assert len(result.relationships) == 4
    for rel in result.relationships:
        assert rel.rel_type == RelationshipType.DECLARES