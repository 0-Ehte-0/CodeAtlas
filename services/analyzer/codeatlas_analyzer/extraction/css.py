# services/analyzer/codeatlas_analyzer/extraction/css.py
from typing import List, Optional
from tree_sitter import Node

from codeatlas_contracts import SupportedLanguage
from codeatlas_graph_schema.labels import NodeLabel
from codeatlas_graph_schema.relationships import RelationshipType
from codeatlas_analyzer.extraction.base import BaseExtractor
from codeatlas_analyzer.extraction.models import (
    ExtractedEntity,
    ExtractedRelationship,
    ExtractionResult,
    generate_symbol_id,
)
from codeatlas_analyzer.parser.models import ParsedSourceTree, SourceSpan


class CSSExtractor(BaseExtractor):
    """Extracts File, RuleSet Selectors, Keyframes, and @import statements from CSS ASTs."""

    @property
    def supported_language(self) -> SupportedLanguage:
        return SupportedLanguage.CSS

    def extract(self, parsed_tree: ParsedSourceTree, snapshot_id: str) -> ExtractionResult:
        file_entity = self.create_file_entity(parsed_tree, snapshot_id)
        result = ExtractionResult(file_entity=file_entity)
        result.entities.append(file_entity)

        if not parsed_tree.tree or not parsed_tree.tree.root_node:
            return result

        self._extract_css_statements(
            node=parsed_tree.tree.root_node,
            parsed_tree=parsed_tree,
            snapshot_id=snapshot_id,
            parent_id=file_entity.id,
            scope_prefix="",
            result=result,
        )
        return result

    def _extract_css_statements(
        self,
        node: Node,
        parsed_tree: ParsedSourceTree,
        snapshot_id: str,
        parent_id: str,
        scope_prefix: str,
        result: ExtractionResult,
    ) -> None:
        """Traverses stylesheet nodes, media queries, and rulesets."""
        for child in node.children:
            span = SourceSpan.from_tree_sitter_node(child)

            # 1. @import statements (@import "layout.css"; or @import url("theme.css");)
            if child.type == "import_statement":
                import_text = parsed_tree.get_node_text(child).strip()
                target_path = self._sanitize_import_target(import_text)
                import_id = generate_symbol_id(snapshot_id, parsed_tree.relative_path, f"import:{target_path}")

                import_entity = ExtractedEntity(
                    id=import_id,
                    label=NodeLabel.FILE,
                    name=target_path.split("/")[-1],
                    qualified_name=target_path,
                    relative_path=parsed_tree.relative_path,
                    language=SupportedLanguage.CSS,
                    start_line=span.start_line,
                    end_line=span.end_line,
                    extra_properties={"import_path": target_path},
                )
                result.entities.append(import_entity)
                result.relationships.append(
                    ExtractedRelationship(
                        source_id=parent_id,
                        target_id=import_id,
                        rel_type=RelationshipType.IMPORTS,
                    )
                )

            # 2. Keyframes (@keyframes slideIn { ... })
            elif child.type == "keyframes_statement":
                name_node = next(
                    (c for c in child.children if c.type in ("keyframes_name", "identifier", "custom_property_name")),
                    None,
                )
                if name_node:
                    anim_name = parsed_tree.get_node_text(name_node).strip()
                    anim_id = generate_symbol_id(snapshot_id, parsed_tree.relative_path, f"keyframes:{anim_name}")

                    anim_entity = ExtractedEntity(
                        id=anim_id,
                        label=NodeLabel.VARIABLE,
                        name=f"@keyframes {anim_name}",
                        qualified_name=f"{parsed_tree.relative_path}#@keyframes {anim_name}",
                        relative_path=parsed_tree.relative_path,
                        language=SupportedLanguage.CSS,
                        start_line=span.start_line,
                        end_line=span.end_line,
                        extra_properties={"animation_name": anim_name},
                    )
                    result.entities.append(anim_entity)
                    result.relationships.append(
                        ExtractedRelationship(
                            source_id=parent_id,
                            target_id=anim_id,
                            rel_type=RelationshipType.DECLARES,
                        )
                    )

            # 3. Standard CSS Rule Sets (.layout, #main, button:hover)
            elif child.type == "rule_set":
                selectors_node = next(
                    (c for c in child.children if c.type in ("selectors", "selector")),
                    None,
                )
                if selectors_node:
                    selector_raw = parsed_tree.get_node_text(selectors_node).strip()
                    qualified_selector = f"{scope_prefix} {selector_raw}".strip() if scope_prefix else selector_raw
                    symbol_id = generate_symbol_id(snapshot_id, parsed_tree.relative_path, f"rule:{qualified_selector}")

                    rule_entity = ExtractedEntity(
                        id=symbol_id,
                        label=NodeLabel.VARIABLE,
                        name=qualified_selector,
                        qualified_name=f"{parsed_tree.relative_path}#{qualified_selector}",
                        relative_path=parsed_tree.relative_path,
                        language=SupportedLanguage.CSS,
                        start_line=span.start_line,
                        end_line=span.end_line,
                        extra_properties={"selector": qualified_selector},
                    )
                    result.entities.append(rule_entity)
                    result.relationships.append(
                        ExtractedRelationship(
                            source_id=parent_id,
                            target_id=symbol_id,
                            rel_type=RelationshipType.DECLARES,
                        )
                    )

            # 4. Nested @media and @supports blocks
            elif child.type in ("media_statement", "supports_statement"):
                block_node = next((c for c in child.children if c.type == "block"), None)
                if block_node:
                    self._extract_css_statements(
                        node=block_node,
                        parsed_tree=parsed_tree,
                        snapshot_id=snapshot_id,
                        parent_id=parent_id,
                        scope_prefix=scope_prefix,
                        result=result,
                    )

    def _sanitize_import_target(self, import_text: str) -> str:
        """Sanitizes raw `@import url('...')` or `@import '...'` statements down to file paths."""
        cleaned = import_text.replace("@import", "").replace(";", "").strip()
        if cleaned.startswith("url(") and cleaned.endswith(")"):
            cleaned = cleaned[4:-1].strip()
        return cleaned.strip("\"'")