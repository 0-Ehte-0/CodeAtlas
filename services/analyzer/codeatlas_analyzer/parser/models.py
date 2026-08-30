# services/analyzer/codeatlas_analyzer/parser/models.py
from dataclasses import dataclass, field
from typing import Any, Optional
from tree_sitter import Node, Tree
from codeatlas_contracts.enums import SupportedLanguage


@dataclass(frozen=True)
class SourceSpan:
    """Represents a 1-indexed line and 0-indexed column source boundary."""
    start_line: int
    start_column: int
    end_line: int
    end_column: int

    @classmethod
    def from_tree_sitter_node(cls, node: Node) -> "SourceSpan":
        # Tree-sitter rows are 0-indexed; convert to 1-indexed for editor/citation standard
        return cls(
            start_line=node.start_point[0] + 1,
            start_column=node.start_point[1],
            end_line=node.end_point[0] + 1,
            end_column=node.end_point[1],
        )


@dataclass
class ParsedSourceTree:
    """Encapsulates a parsed AST along with its raw source and error metadata."""
    relative_path: str
    language: SupportedLanguage
    source_bytes: bytes
    tree: Optional[Tree]
    is_parsed: bool
    has_syntax_errors: bool = False
    error_message: Optional[str] = None
    diagnostics: list[str] = field(default_factory=list)

    def get_node_text(self, node: Node) -> str:
        """Safely extracts text for a given Tree-sitter node using raw byte offsets."""
        return self.source_bytes[node.start_byte:node.end_byte].decode("utf-8", errors="replace")