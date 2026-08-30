# tests/test_markup_extractors.py
import pytest
import tree_sitter
from tree_sitter import Language, Parser
import tree_sitter_html as ts_html
import tree_sitter_css as ts_css

from codeatlas_contracts.enums import SupportedLanguage
from codeatlas_graph_schema.labels import NodeLabel
from codeatlas_graph_schema.relationships import RelationshipType
from codeatlas_analyzer.parser.models import ParsedSourceTree
from codeatlas_analyzer.extraction.html import HTMLExtractor
from codeatlas_analyzer.extraction.css import CSSExtractor

HTML_SAMPLE = b'''
<!DOCTYPE html>
<html>
<head>
    <link rel="stylesheet" href="styles/main.css">
    <script src="scripts/bundle.js"></script>
</head>
<body>
    <div id="app-container" class="layout">
        <form action="/api/auth/login" method="POST">
            <button type="submit">Log In</button>
        </form>
    </div>
</body>
</html>
'''

CSS_SAMPLE = b'''
@import url("theme/variables.css");

@keyframes pulse {
    0% { opacity: 1; }
    50% { opacity: 0.5; }
}

.layout {
    display: flex;
}

#app-container {
    padding: 20px;
}
'''

def test_html_extractor_entities_and_relations():
    parser = Parser(Language(ts_html.language()))
    tree = parser.parse(HTML_SAMPLE)

    parsed_tree = ParsedSourceTree(
        relative_path="public/index.html",
        language=SupportedLanguage.HTML,
        source_bytes=HTML_SAMPLE,
        tree=tree,
        is_parsed=True,
    )

    extractor = HTMLExtractor()
    result = extractor.extract(parsed_tree, "snap-001")

    # Verify stylesheet and script imports
    import_rels = [r for r in result.relationships if r.rel_type == RelationshipType.IMPORTS]
    assert len(import_rels) == 2

    # Verify form endpoint reference
    form_entity = next(e for e in result.entities if e.label == NodeLabel.API_ENDPOINT)
    assert form_entity.extra_properties["route_path"] == "/api/auth/login"
    assert form_entity.extra_properties["http_method"] == "POST"

    # Verify DOM element identification
    dom_entity = next(e for e in result.entities if e.name == "#app-container")
    assert dom_entity.label == NodeLabel.VARIABLE


def test_css_extractor_entities_and_relations():
    parser = Parser(Language(ts_css.language()))
    tree = parser.parse(CSS_SAMPLE)

    parsed_tree = ParsedSourceTree(
        relative_path="public/styles/main.css",
        language=SupportedLanguage.CSS,
        source_bytes=CSS_SAMPLE,
        tree=tree,
        is_parsed=True,
    )

    extractor = CSSExtractor()
    result = extractor.extract(parsed_tree, "snap-001")

    # 1 File + 1 Import + 1 Keyframe + 2 RuleSets = 5 entities
    assert len(result.entities) == 5

    # Verify @import
    import_rel = next(r for r in result.relationships if r.rel_type == RelationshipType.IMPORTS)
    assert "variables.css" in import_rel.target_id

    # Verify @keyframes animation extraction
    anim_entity = next(e for e in result.entities if "@keyframes" in e.name)
    assert anim_entity.extra_properties["animation_name"] == "pulse"

    # Verify Selector rulesets
    selectors = {e.name for e in result.entities if e.label == NodeLabel.VARIABLE and "@keyframes" not in e.name}
    assert selectors == {".layout", "#app-container"}