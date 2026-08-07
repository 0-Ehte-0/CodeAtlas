from enum import Enum

class NodeLabel(str, Enum):
    """
    Standardized Neo4j Node Labels for CodeAtlas graph schema.
    Represents structural containers, code elements, and infrastructure components.
    """
    # High-level Structural Containers
    REPOSITORY = "Repository"        # Root code repository container
    SNAPSHOT = "Snapshot"            # Point-in-time commit state representation
    MODULE = "Module"                # Code package, module, or directory scope
    FILE = "File"                    # Source code file on disk
    NAMESPACE = "Namespace"          # Logical scope (e.g., C# namespace, C++ namespace, TS module)

    # Object-Oriented & Procedural Code Entities
    CLASS = "Class"                  # Class definition
    INTERFACE = "Interface"          # Abstract interface / contract definition
    FUNCTION = "Function"            # Standalone function
    METHOD = "Method"                # Method bound to a class or interface
    VARIABLE = "Variable"            # Constant, global variable, or class property/field

    # Infrastructure, Storage, & External Dependencies
    DATABASE_TABLE = "DatabaseTable"  # Relational or document database table/collection
    DATABASE_COLUMN = "DatabaseColumn" # Individual column/field within a database table
    API_ENDPOINT = "APIEndpoint"     # Exposed REST, gRPC, or HTTP route endpoint
    QUEUE_TOPIC = "QueueTopic"       # Event queue topic or message channel (e.g., Kafka, Redis Pub/Sub)
    EXTERNAL_PACKAGE = "ExternalPackage" # Third-party library dependency (e.g., PyPI, npm)