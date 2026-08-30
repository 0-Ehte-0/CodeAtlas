# services/analyzer/codeatlas_analyzer/extraction/python.py
from typing import List, Optional
from tree_sitter import Node

from codeatlas_contracts import SupportedLanguage
from codeatlas_graph_schema import NodeLabel
from codeatlas_graph_schema import RelationshipType
from codeatlas_analyzer.extraction.base import BaseExtractor
from codeatlas_analyzer.extraction.models import (
    ExtractedEntity,
    ExtractedRelationship,
    ExtractionResult,
    generate_symbol_id,
)
from codeatlas_analyzer.parser.models import ParsedSourceTree, SourceSpan


class PythonExtractor(BaseExtractor):
    """Extracts File, Class, Function, and Method entities from Python ASTs."""

    @property
    def supported_language(self) -> SupportedLanguage:
        return SupportedLanguage.PYTHON

    def extract(self, parsed_tree: ParsedSourceTree, snapshot_id: str) -> ExtractionResult:
        file_entity = self.create_file_entity(parsed_tree, snapshot_id)
        result = ExtractionResult(file_entity=file_entity)
        result.entities.append(file_entity)

        if not parsed_tree.tree or not parsed_tree.tree.root_node:
            return result

        self._extract_scope(
            node=parsed_tree.tree.root_node,
            parsed_tree=parsed_tree,
            snapshot_id=snapshot_id,
            parent_id=file_entity.id,
            parent_scope="",
            result=result,
        )
        return result

    def _unwrap_node(self, node: Node) -> Node:
        """Unwraps decorated definitions to reach the inner class or function definition."""
        if node.type == "decorated_definition":
            for child in node.children:
                if child.type in ("function_definition", "class_definition"):
                    return child
        return node

    def _extract_scope(
        self,
        node: Node,
        parsed_tree: ParsedSourceTree,
        snapshot_id: str,
        parent_id: str,
        parent_scope: str,
        result: ExtractionResult,
    ) -> None:
        """Recursively traverses AST nodes in a given lexical scope."""
        for child in node.children:
            unwrapped = self._unwrap_node(child)
            span = SourceSpan.from_tree_sitter_node(child)  # Capture outer span including decorators

            if unwrapped.type == "class_definition":
                name_node = unwrapped.child_by_field_name("name")
                if not name_node:
                    continue
                class_name = parsed_tree.get_node_text(name_node)
                qualified_name = f"{parent_scope}.{class_name}" if parent_scope else class_name
                symbol_id = generate_symbol_id(snapshot_id, parsed_tree.relative_path, qualified_name)

                class_entity = ExtractedEntity(
                    id=symbol_id,
                    label=NodeLabel.CLASS,
                    name=class_name,
                    qualified_name=qualified_name,
                    relative_path=parsed_tree.relative_path,
                    language=SupportedLanguage.PYTHON,
                    start_line=span.start_line,
                    end_line=span.end_line,
                )
                result.entities.append(class_entity)
                result.relationships.append(
                    ExtractedRelationship(
                        source_id=parent_id,
                        target_id=symbol_id,
                        rel_type=RelationshipType.DECLARES,
                    )
                )

                body_node = unwrapped.child_by_field_name("body")
                if body_node:
                    self._extract_scope(
                        node=body_node,
                        parsed_tree=parsed_tree,
                        snapshot_id=snapshot_id,
                        parent_id=symbol_id,
                        parent_scope=qualified_name,
                        result=result,
                    )

            elif unwrapped.type == "function_definition":
                name_node = unwrapped.child_by_field_name("name")
                if not name_node:
                    continue
                func_name = parsed_tree.get_node_text(name_node)
                qualified_name = f"{parent_scope}.{func_name}" if parent_scope else func_name
                symbol_id = generate_symbol_id(snapshot_id, parsed_tree.relative_path, qualified_name)

                # Classify as METHOD if enclosed within a class scope, otherwise FUNCTION
                label = NodeLabel.METHOD if parent_scope else NodeLabel.FUNCTION

                func_entity = ExtractedEntity(
                    id=symbol_id,
                    label=label,
                    name=func_name,
                    qualified_name=qualified_name,
                    relative_path=parsed_tree.relative_path,
                    language=SupportedLanguage.PYTHON,
                    start_line=span.start_line,
                    end_line=span.end_line,
                )
                result.entities.append(func_entity)
                result.relationships.append(
                    ExtractedRelationship(
                        source_id=parent_id,
                        target_id=symbol_id,
                        rel_type=RelationshipType.DECLARES,
                    )
                )