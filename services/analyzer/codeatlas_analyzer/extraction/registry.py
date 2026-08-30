# services/analyzer/codeatlas_analyzer/extraction/registry.py
from typing import Dict, Optional
from codeatlas_contracts import SupportedLanguage
from codeatlas_analyzer.parser.models import ParsedSourceTree

from codeatlas_analyzer.extraction.base import BaseExtractor
from codeatlas_analyzer.extraction.python import PythonExtractor
from codeatlas_analyzer.extraction.typescript import TypeScriptExtractor
from codeatlas_analyzer.extraction.html import HTMLExtractor
from codeatlas_analyzer.extraction.css import CSSExtractor

from codeatlas_analyzer.extraction.models import ExtractionResult

class ExtractorRegistry:
    """Registry coordinating language-specific extractors."""

    def __init__(self) -> None:
        self._extractors: Dict[SupportedLanguage, BaseExtractor] = {
            SupportedLanguage.PYTHON: PythonExtractor(),
            SupportedLanguage.TYPESCRIPT: TypeScriptExtractor(SupportedLanguage.TYPESCRIPT),
            SupportedLanguage.JAVASCRIPT: TypeScriptExtractor(SupportedLanguage.JAVASCRIPT),
            SupportedLanguage.HTML: HTMLExtractor(),
            SupportedLanguage.CSS: CSSExtractor(),
        }

    def get_extractor(self, language: SupportedLanguage) -> Optional[BaseExtractor]:
        return self._extractors.get(language)

    def extract_tree(self, parsed_tree: ParsedSourceTree, snapshot_id: str) -> Optional[ExtractionResult]:
        extractor = self.get_extractor(parsed_tree.language)
        if not extractor:
            return None
        return extractor.extract(parsed_tree, snapshot_id)