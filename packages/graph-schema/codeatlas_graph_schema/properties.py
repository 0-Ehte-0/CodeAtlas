class NodeProperty:
    """
    Standardized Neo4j node property key names across all entity types.
    """
    # Core Entity Identifiers
    ID = "id"                          # Unique node identifier (UUID or deterministic hash)
    NAME = "name"                      # Display name (e.g., function name, class name)
    QUALIFIED_NAME = "qualified_name"  # Fully qualified path (e.g., 'codeatlas.analyzer.parse_ast')

    # Source File Metadata & AST Positions
    FILE_PATH = "file_path"            # Path relative to repository root
    LANGUAGE = "language"              # Programming language (e.g., python, typescript)
    START_LINE = "start_line"          # 1-based start line in source file
    END_LINE = "end_line"              # 1-based end line in source file

    # Scope & Repository Tracking
    REPO_ID = "repo_id"                # Parent repository ID
    COMMIT_HASH = "commit_hash"        # Commit SHA for Snapshot nodes

    # API Endpoint Properties
    HTTP_METHOD = "http_method"        # GET, POST, PUT, DELETE, etc.
    ROUTE_PATH = "route_path"          # e.g., '/api/v1/repositories/{id}'

    # Database Schema Properties
    DATA_TYPE = "data_type"            # e.g., 'VARCHAR', 'INTEGER', 'BOOLEAN'
    IS_PRIMARY_KEY = "is_primary_key"  # Boolean flag for primary keys

    # External Package Properties
    VERSION = "version"                # Package version string (e.g., '2.31.0')
    ECOSYSTEM = "ecosystem"            # Package ecosystem (e.g., 'pypi', 'npm', 'crates')