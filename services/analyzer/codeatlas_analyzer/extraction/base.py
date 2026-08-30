# services/analyzer/codeatlas_analyzer/extraction/base.py
from abc import ABC, abstractmethod
from codeatlas_graph_schema import NodeLabel
from codeatlas_contracts import SupportedLanguage
from codeatlas_analyzer.parser.models import ParsedSourceTree
from codeatlas_analyzer.extraction.models import (
    ExtractedEntity,
    ExtractionResult,
    generate_symbol_id,
)


class BaseExtractor(ABC):
    """Abstract base class for all language-specific AST entity extractors."""

    @property
    @abstractmethod
    def supported_language(self) -> SupportedLanguage:
        pass

    def create_file_entity(self, parsed_tree: ParsedSourceTree, snapshot_id: str) -> ExtractedEntity:
        """Creates the root File entity for the source file."""
        line_count = 1
        if parsed_tree.source_bytes:
            line_count = parsed_tree.source_bytes.count(b"\n") + 1

        return ExtractedEntity(
            id=generate_symbol_id(snapshot_id, parsed_tree.relative_path),
            label=NodeLabel.FILE,
            name=parsed_tree.relative_path.split("/")[-1],
            qualified_name=parsed_tree.relative_path,
            relative_path=parsed_tree.relative_path,
            language=self.supported_language,
            start_line=1,
            end_line=line_count,
        )

    @abstractmethod
    def extract(self, parsed_tree: ParsedSourceTree, snapshot_id: str) -> ExtractionResult:
        """Extracts files, classes, functions, methods, and relationships from the parsed AST."""
        pass