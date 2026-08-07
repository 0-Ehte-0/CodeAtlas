from neo4j import GraphDatabase

from config import get_neo4j_auth, get_neo4j_uri

URI = get_neo4j_uri()
USERNAME, PASSWORD = get_neo4j_auth()

driver = GraphDatabase.driver(
    URI,
    auth=(USERNAME, PASSWORD)
)


def test_neo4j_connection():
    with driver.session() as session:
        result = session.run("RETURN 1 AS result")
        record = result.single()

        print(record["result"])


if __name__ == "__main__":
    test_neo4j_connection()