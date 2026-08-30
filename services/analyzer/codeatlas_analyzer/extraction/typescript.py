# services/analyzer/codeatlas_analyzer/extraction/typescript.py
from typing import Optional
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


class TypeScriptExtractor(BaseExtractor):
    """Extracts File, Class, Interface, Function, and Method entities from TypeScript and JavaScript ASTs."""

    def __init__(self, language: SupportedLanguage = SupportedLanguage.TYPESCRIPT):
        self._language = language

    @property
    def supported_language(self) -> SupportedLanguage:
        return self._language

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

    def _unwrap_export(self, node: Node) -> Node:
        """Unwraps export_statement to reach the underlying declaration."""
        if node.type == "export_statement":
            for child in node.children:
                if child.type in (
                    "class_declaration",
                    "abstract_class_declaration",
                    "function_declaration",
                    "lexical_declaration",
                    "variable_declaration",
                    "interface_declaration",
                ):
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
        """Traverses TypeScript AST nodes and records declared structural entities."""
        for child in node.children:
            unwrapped = self._unwrap_export(child)
            span = SourceSpan.from_tree_sitter_node(child)

            # Class declarations
            if unwrapped.type in ("class_declaration", "abstract_class_declaration"):
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
                    language=self.supported_language,
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
                    self._extract_class_members(
                        class_body=body_node,
                        parsed_tree=parsed_tree,
                        snapshot_id=snapshot_id,
                        class_id=symbol_id,
                        class_scope=qualified_name,
                        result=result,
                    )

            # Interface declarations (TypeScript)
            elif unwrapped.type == "interface_declaration":
                name_node = unwrapped.child_by_field_name("name")
                if not name_node:
                    continue
                iface_name = parsed_tree.get_node_text(name_node)
                qualified_name = f"{parent_scope}.{iface_name}" if parent_scope else iface_name
                symbol_id = generate_symbol_id(snapshot_id, parsed_tree.relative_path, qualified_name)

                iface_entity = ExtractedEntity(
                    id=symbol_id,
                    label=NodeLabel.INTERFACE,
                    name=iface_name,
                    qualified_name=qualified_name,
                    relative_path=parsed_tree.relative_path,
                    language=self.supported_language,
                    start_line=span.start_line,
                    end_line=span.end_line,
                )
                result.entities.append(iface_entity)
                result.relationships.append(
                    ExtractedRelationship(
                        source_id=parent_id,
                        target_id=symbol_id,
                        rel_type=RelationshipType.DECLARES,
                    )
                )

            # Standard function declarations
            elif unwrapped.type == "function_declaration":
                name_node = unwrapped.child_by_field_name("name")
                if not name_node:
                    continue
                func_name = parsed_tree.get_node_text(name_node)
                qualified_name = f"{parent_scope}.{func_name}" if parent_scope else func_name
                symbol_id = generate_symbol_id(snapshot_id, parsed_tree.relative_path, qualified_name)

                func_entity = ExtractedEntity(
                    id=symbol_id,
                    label=NodeLabel.FUNCTION,
                    name=func_name,
                    qualified_name=qualified_name,
                    relative_path=parsed_tree.relative_path,
                    language=self.supported_language,
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

            # Arrow functions and function expressions in variable declarations: const foo = () => {}
            elif unwrapped.type in ("lexical_declaration", "variable_declaration"):
                for declarator in unwrapped.children:
                    if declarator.type == "variable_declarator":
                        value_node = declarator.child_by_field_name("value")
                        if value_node and value_node.type in ("arrow_function", "function_expression"):
                            name_node = declarator.child_by_field_name("name")
                            if not name_node:
                                continue
                            func_name = parsed_tree.get_node_text(name_node)
                            qualified_name = f"{parent_scope}.{func_name}" if parent_scope else func_name
                            symbol_id = generate_symbol_id(snapshot_id, parsed_tree.relative_path, qualified_name)

                            func_entity = ExtractedEntity(
                                id=symbol_id,
                                label=NodeLabel.FUNCTION,
                                name=func_name,
                                qualified_name=qualified_name,
                                relative_path=parsed_tree.relative_path,
                                language=self.supported_language,
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

    def _extract_class_members(
        self,
        class_body: Node,
        parsed_tree: ParsedSourceTree,
        snapshot_id: str,
        class_id: str,
        class_scope: str,
        result: ExtractionResult,
    ) -> None:
        """Extracts methods from a TypeScript/JavaScript class body."""
        for member in class_body.children:
            if member.type == "method_definition":
                name_node = member.child_by_field_name("name")
                if not name_node:
                    continue
                method_name = parsed_tree.get_node_text(name_node)
                qualified_name = f"{class_scope}.{method_name}"
                symbol_id = generate_symbol_id(snapshot_id, parsed_tree.relative_path, qualified_name)
                span = SourceSpan.from_tree_sitter_node(member)

                method_entity = ExtractedEntity(
                    id=symbol_id,
                    label=NodeLabel.METHOD,
                    name=method_name,
                    qualified_name=qualified_name,
                    relative_path=parsed_tree.relative_path,
                    language=self.supported_language,
                    start_line=span.start_line,
                    end_line=span.end_line,
                )
                result.entities.append(method_entity)
                result.relationships.append(
                    ExtractedRelationship(
                        source_id=class_id,
                        target_id=symbol_id,
                        rel_type=RelationshipType.DECLARES,
                    )
                )