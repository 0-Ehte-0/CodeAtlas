# services/analyzer/codeatlas_analyzer/extraction/models.py
from dataclasses import dataclass, field
from typing import Any, Dict, Optional
from codeatlas_graph_schema import NodeLabel
from codeatlas_graph_schema import NodeProperty
from codeatlas_graph_schema import RelationshipType
from codeatlas_contracts import SupportedLanguage

# symbol = any file, class, function, method, or other structural entity that can be extracted from code
def generate_symbol_id(snapshot_id: str, relative_path: str, qualified_name: Optional[str] = None) -> str:
    """Generates a stable, reproducible symbol ID adhering to snapshot isolation."""
    if not qualified_name:
        return f"{snapshot_id}:{relative_path}"
    return f"{snapshot_id}:{relative_path}#{qualified_name}"


@dataclass
class ExtractedEntity:
    """Canonical extracted structural entity for Neo4j ingestion."""
    id: str
    label: NodeLabel
    name: str
    qualified_name: str
    relative_path: str
    language: SupportedLanguage
    start_line: int
    end_line: int
    docstring: Optional[str] = None
    extra_properties: Dict[str, Any] = field(default_factory=dict)

    def to_node_properties(self, snapshot_id: str, commit_hash: str) -> Dict[str, Any]:
        """Maps the extracted entity into properties defined in NodeProperty."""
        props = {
            NodeProperty.ID: self.id,
            NodeProperty.NAME: self.name,
            NodeProperty.QUALIFIED_NAME: self.qualified_name,
            NodeProperty.FILE_PATH: self.relative_path,
            NodeProperty.LANGUAGE: self.language.value,
            NodeProperty.START_LINE: self.start_line,
            NodeProperty.END_LINE: self.end_line,
            NodeProperty.COMMIT_HASH: commit_hash,
        }
        props.update(self.extra_properties)
        return props


@dataclass
class ExtractedRelationship:
    """Represents a directional relationship between two extracted entities."""
    source_id: str
    target_id: str
    rel_type: RelationshipType
    properties: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ExtractionResult:
    """Aggregated container of all extracted entities and relationships for a file."""
    file_entity: ExtractedEntity
    entities: list[ExtractedEntity] = field(default_factory=list)
    relationships: list[ExtractedRelationship] = field(default_factory=list)