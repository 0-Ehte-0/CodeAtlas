# services/analyzer/codeatlas_analyzer/extraction/html.py
from typing import Dict, List, Optional, Tuple
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


class HTMLExtractor(BaseExtractor):
    """Extracts File, DOM Landmark, and Script/Style Import entities from HTML ASTs."""

    @property
    def supported_language(self) -> SupportedLanguage:
        return SupportedLanguage.HTML

    def extract(self, parsed_tree: ParsedSourceTree, snapshot_id: str) -> ExtractionResult:
        file_entity = self.create_file_entity(parsed_tree, snapshot_id)
        result = ExtractionResult(file_entity=file_entity)
        result.entities.append(file_entity)

        if not parsed_tree.tree or not parsed_tree.tree.root_node:
            return result

        self._traverse_html_node(
            node=parsed_tree.tree.root_node,
            parsed_tree=parsed_tree,
            snapshot_id=snapshot_id,
            parent_id=file_entity.id,
            result=result,
        )
        return result

    def _get_tag_and_attributes(self, element_node: Node, parsed_tree: ParsedSourceTree) -> Tuple[str, Dict[str, str]]:
        """Extracts the tag name and a key-value dictionary of attributes from an HTML element."""
        tag_name = ""
        attributes: Dict[str, str] = {}

        # Locate the start/self-closing/script/style tag node
        start_tag_node = None
        if element_node.type in ("start_tag", "self_closing_tag", "script_start_tag", "style_start_tag"):
            start_tag_node = element_node
        else:
            for child in element_node.children:
                if child.type in ("start_tag", "self_closing_tag", "script_start_tag", "style_start_tag"):
                    start_tag_node = child
                    break

        if not start_tag_node:
            if element_node.type == "script_element":
                tag_name = "script"
            elif element_node.type == "style_element":
                tag_name = "style"
            return tag_name, attributes

        for child in start_tag_node.children:
            if child.type == "tag_name":
                tag_name = parsed_tree.get_node_text(child).strip().lower()
            elif child.type == "attribute":
                attr_name = ""
                attr_val = ""
                for attr_child in child.children:
                    if attr_child.type == "attribute_name":
                        attr_name = parsed_tree.get_node_text(attr_child).strip()
                    elif attr_child.type in ("quoted_attribute_value", "attribute_value"):
                        raw_val = parsed_tree.get_node_text(attr_child).strip()
                        attr_val = raw_val.strip("\"'")
                if attr_name:
                    attributes[attr_name] = attr_val

        if not tag_name:
            if element_node.type == "script_element" or start_tag_node.type == "script_start_tag":
                tag_name = "script"
            elif element_node.type == "style_element" or start_tag_node.type == "style_start_tag":
                tag_name = "style"

        return tag_name, attributes

    def _traverse_html_node(
        self,
        node: Node,
        parsed_tree: ParsedSourceTree,
        snapshot_id: str,
        parent_id: str,
        result: ExtractionResult,
    ) -> None:
        """Recursively inspects HTML elements for assets, script inclusions, and landmarks."""
        for child in node.children:
            if child.type in ("element", "script_element", "style_element"):
                span = SourceSpan.from_tree_sitter_node(child)
                tag_name, attrs = self._get_tag_and_attributes(child, parsed_tree)

                # 1. External Script Imports (<script src="...">)
                if tag_name == "script" and "src" in attrs:
                    src_target = attrs["src"]
                    script_id = generate_symbol_id(snapshot_id, parsed_tree.relative_path, f"script:{src_target}")
                    script_entity = ExtractedEntity(
                        id=script_id,
                        label=NodeLabel.EXTERNAL_PACKAGE if src_target.startswith(("http://", "https://", "//")) else NodeLabel.FILE,
                        name=src_target.split("/")[-1],
                        qualified_name=src_target,
                        relative_path=parsed_tree.relative_path,
                        language=SupportedLanguage.JAVASCRIPT,
                        start_line=span.start_line,
                        end_line=span.end_line,
                        extra_properties={"src": src_target},
                    )
                    result.entities.append(script_entity)
                    result.relationships.append(
                        ExtractedRelationship(
                            source_id=parent_id,
                            target_id=script_id,
                            rel_type=RelationshipType.IMPORTS,
                        )
                    )

                # 2. Stylesheet Imports (<link rel="stylesheet" href="...">)
                elif tag_name == "link" and "stylesheet" in attrs.get("rel", "").lower() and "href" in attrs:
                    href_target = attrs["href"]
                    css_id = generate_symbol_id(snapshot_id, parsed_tree.relative_path, f"stylesheet:{href_target}")
                    css_entity = ExtractedEntity(
                        id=css_id,
                        label=NodeLabel.FILE,
                        name=href_target.split("/")[-1],
                        qualified_name=href_target,
                        relative_path=parsed_tree.relative_path,
                        language=SupportedLanguage.CSS,
                        start_line=span.start_line,
                        end_line=span.end_line,
                        extra_properties={"href": href_target},
                    )
                    result.entities.append(css_entity)
                    result.relationships.append(
                        ExtractedRelationship(
                            source_id=parent_id,
                            target_id=css_id,
                            rel_type=RelationshipType.IMPORTS,
                        )
                    )

                # 3. Form Handlers & API Actions (<form action="/api/v1/login" method="POST">)
                elif tag_name == "form" and "action" in attrs:
                    action = attrs["action"]
                    method = attrs.get("method", "GET").upper()
                    form_id = generate_symbol_id(snapshot_id, parsed_tree.relative_path, f"form:{action}")
                    form_entity = ExtractedEntity(
                        id=form_id,
                        label=NodeLabel.API_ENDPOINT,
                        name=f"FORM {method} {action}",
                        qualified_name=action,
                        relative_path=parsed_tree.relative_path,
                        language=SupportedLanguage.HTML,
                        start_line=span.start_line,
                        end_line=span.end_line,
                        extra_properties={"http_method": method, "route_path": action},
                    )
                    result.entities.append(form_entity)
                    result.relationships.append(
                        ExtractedRelationship(
                            source_id=parent_id,
                            target_id=form_id,
                            rel_type=RelationshipType.REFERENCES,
                        )
                    )

                # 4. Major Elements with explicit IDs
                elif "id" in attrs:
                    element_dom_id = attrs["id"]
                    entity_id = generate_symbol_id(snapshot_id, parsed_tree.relative_path, f"#{element_dom_id}")
                    element_entity = ExtractedEntity(
                        id=entity_id,
                        label=NodeLabel.VARIABLE,
                        name=f"#{element_dom_id}",
                        qualified_name=f"{parsed_tree.relative_path}#{element_dom_id}",
                        relative_path=parsed_tree.relative_path,
                        language=SupportedLanguage.HTML,
                        start_line=span.start_line,
                        end_line=span.end_line,
                        extra_properties={"tag": tag_name, "dom_id": element_dom_id, "classes": attrs.get("class", "")},
                    )
                    result.entities.append(element_entity)
                    result.relationships.append(
                        ExtractedRelationship(
                            source_id=parent_id,
                            target_id=entity_id,
                            rel_type=RelationshipType.DECLARES,
                        )
                    )

                # Recurse into children
                self._traverse_html_node(child, parsed_tree, snapshot_id, parent_id, result)