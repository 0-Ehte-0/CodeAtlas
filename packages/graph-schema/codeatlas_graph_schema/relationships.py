from enum import Enum

class RelationshipType(str, Enum):
    """
    Standardized Neo4j Relationship Types for CodeAtlas.
    Defines structural containment, code invocation, data access, and API/queue bindings.
    """
    # Structural Ownership
    CONTAINS = "CONTAINS"            # Parent-child structure (e.g., Repository -> File, File -> Class)
    DECLARES = "DECLARES"            # Scope bindings (e.g., Class -> Method, Module -> Variable)
    
    # Code Execution & Structural Dependencies
    IMPORTS = "IMPORTS"              # Code imports (e.g., File -> Module, File -> ExternalPackage)
    CALLS = "CALLS"                  # Direct code execution (e.g., Function -> Function, Method -> Method)
    INHERITS = "INHERITS"            # Class inheritance (e.g., Class -> Class)
    IMPLEMENTS = "IMPLEMENTS"        # Interface implementation (e.g., Class -> Interface)
    REFERENCES = "REFERENCES"        # Identifier usage (e.g., Method -> Variable, Function -> Class)
    
    # Database / I/O Operations
    READS_FROM = "READS_FROM"        # Data fetch operations (e.g., Method -> DatabaseTable)
    WRITES_TO = "WRITES_TO"          # Data mutation operations (e.g., Method -> DatabaseTable)
    
    # API Routes & Messaging Infrastructure
    EXPOSES_ENDPOINT = "EXPOSES_ENDPOINT" # Web route handler mapping (e.g., Function -> APIEndpoint)
    PUBLISHES_TO = "PUBLISHES_TO"     # Producer event publishing (e.g., Method -> QueueTopic)
    SUBSCRIBES_TO = "SUBSCRIBES_TO"   # Consumer event handler (e.g., Function -> QueueTopic)
    DEPENDS_ON = "DEPENDS_ON"         # General system-level or inter-service dependency linkage