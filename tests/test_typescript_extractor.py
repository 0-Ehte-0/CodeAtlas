# tests/test_typescript_extractor.py
import pytest
from codeatlas_contracts.enums import SupportedLanguage
from codeatlas_graph_schema.labels import NodeLabel
from codeatlas_graph_schema.relationships import RelationshipType
from codeatlas_analyzer.parser.registry import ParserRegistry
from codeatlas_analyzer.parser.models import ParsedSourceTree
from codeatlas_analyzer.extraction.typescript import TypeScriptExtractor

SAMPLE_TS_CODE = b'''
export interface UserDTO {
    id: string;
    username: string;
}

export class UserService {
    private db: any;

    constructor(db: any) {
        self.db = db;
    }

    async findUser(id: string): Promise<UserDTO> {
        return { id, username: "admin" };
    }
}

export const validateToken = (token: string): boolean => {
    return token.length > 0;
};
'''

@pytest.fixture
def parser_registry():
    return ParserRegistry()

def test_typescript_extraction_entities_and_relationships(parser_registry):
    parser = parser_registry.get_parser(SupportedLanguage.TYPESCRIPT)
    tree = parser.parse(SAMPLE_TS_CODE)
    
    parsed_tree = ParsedSourceTree(
        relative_path="src/services/user.ts",
        language=SupportedLanguage.TYPESCRIPT,
        source_bytes=SAMPLE_TS_CODE,
        tree=tree,
        is_parsed=True,
    )
    
    extractor = TypeScriptExtractor(SupportedLanguage.TYPESCRIPT)
    snapshot_id = "snap-test-002"
    result = extractor.extract(parsed_tree, snapshot_id)
    
    # 1 File + 1 Interface + 1 Class + 2 Methods + 1 Arrow Function = 6 entities
    assert len(result.entities) == 6
    
    # Check Interface
    iface_entity = next(e for e in result.entities if e.name == "UserDTO")
    assert iface_entity.label == NodeLabel.INTERFACE
    assert iface_entity.id == "snap-test-002:src/services/user.ts#UserDTO"
    
    # Check Class
    class_entity = next(e for e in result.entities if e.name == "UserService")
    assert class_entity.label == NodeLabel.CLASS
    assert class_entity.id == "snap-test-002:src/services/user.ts#UserService"
    
    # Check Methods
    methods = [e for e in result.entities if e.label == NodeLabel.METHOD]
    assert len(methods) == 2
    assert {m.name for m in methods} == {"constructor", "findUser"}
    
    # Check Arrow Function
    arrow_func = next(e for e in result.entities if e.name == "validateToken")
    assert arrow_func.label == NodeLabel.FUNCTION
    assert arrow_func.id == "snap-test-002:src/services/user.ts#validateToken"
    
    # Check Relationships
    assert len(result.relationships) == 5
    for rel in result.relationships:
        assert rel.rel_type == RelationshipType.DECLARES