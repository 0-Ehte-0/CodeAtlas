# services/analyzer/codeatlas_analyzer/parser/registry.py
from pathlib import Path
from typing import Dict, Optional
import tree_sitter
from tree_sitter import Language, Parser

import tree_sitter_javascript as ts_js
import tree_sitter_python as ts_py
import tree_sitter_typescript as ts_ts
import tree_sitter_html as ts_html
import tree_sitter_css as ts_css

from codeatlas_contracts.enums import SupportedLanguage
from codeatlas_observability.logger import get_logger
from codeatlas_analyzer.discovery.models import DiscoveredFile
from codeatlas_analyzer.parser.models import ParsedSourceTree

logger = get_logger("analyzer.parser")


class ParserRegistry:
    """Manages Tree-sitter language grammars, parser instances, and source code parsing."""

    def __init__(self) -> None:
        self._languages: Dict[SupportedLanguage, Language] = {}
        self._parsers: Dict[SupportedLanguage, Parser] = {}
        self._initialize_grammars()

    def _initialize_grammars(self) -> None:
        """Loads and caches Tree-sitter language grammars for all supported languages."""
        try:
            self._languages[SupportedLanguage.PYTHON] = Language(ts_py.language())
            self._languages[SupportedLanguage.TYPESCRIPT] = Language(ts_ts.language_typescript())
            self._languages[SupportedLanguage.JAVASCRIPT] = Language(ts_js.language())
            self._languages[SupportedLanguage.HTML] = Language(ts_html.language())
            self._languages[SupportedLanguage.CSS] = Language(ts_css.language())

            for lang, grammar in self._languages.items():
                parser = Parser(grammar)
                self._parsers[lang] = parser

            logger.info("Initialized Tree-sitter grammars successfully (Python, TypeScript, JavaScript).")
        except Exception as exc:
            logger.error(f"Failed to initialize Tree-sitter language bindings: {exc}", exc_info=True)
            raise

    def get_parser(self, language: SupportedLanguage) -> Optional[Parser]:
        """Returns the cached parser instance for a given language."""
        return self._parsers.get(language)

    def parse_file(self, discovered_file: DiscoveredFile) -> ParsedSourceTree:
        """Parses a discovered file safely without crashing on file errors or malformed syntax."""
        language = SupportedLanguage.from_extension(discovered_file.extension)
        if language == SupportedLanguage.UNKNOWN or language not in self._parsers:
            return ParsedSourceTree(
                relative_path=discovered_file.relative_path,
                language=language,
                source_bytes=b"",
                tree=None,
                is_parsed=False,
                error_message=f"Unsupported language extension: {discovered_file.extension}",
            )

        file_path = Path(discovered_file.absolute_path)
        try:
            source_bytes = file_path.read_bytes()
        except Exception as read_err:
            logger.warning(f"Could not read source file {discovered_file.absolute_path}: {read_err}")
            return ParsedSourceTree(
                relative_path=discovered_file.relative_path,
                language=language,
                source_bytes=b"",
                tree=None,
                is_parsed=False,
                error_message=f"I/O read failure: {str(read_err)}",
            )

        parser = self._parsers[language]
        try:
            tree = parser.parse(source_bytes)
            has_errors = tree.root_node.has_error
            diagnostics = []

            if has_errors:
                diagnostics.append("Syntax tree contains ERROR or MISSING recovery nodes.")
                logger.debug(f"Partial AST recovered with syntax errors in {discovered_file.relative_path}")

            return ParsedSourceTree(
                relative_path=discovered_file.relative_path,
                language=language,
                source_bytes=source_bytes,
                tree=tree,
                is_parsed=True,
                has_syntax_errors=has_errors,
                diagnostics=diagnostics,
            )
        except Exception as parse_err:
            logger.error(f"Parser crash while parsing {discovered_file.relative_path}: {parse_err}")
            return ParsedSourceTree(
                relative_path=discovered_file.relative_path,
                language=language,
                source_bytes=source_bytes,
                tree=None,
                is_parsed=False,
                error_message=f"Parser crash: {str(parse_err)}",
            )