from app.chunker import chunk_code
from app.vector_store import VectorStore


def run_test():
    sample_code = """
def submit_contact_form(payload):
    response = requests.post("/api/contact", json=payload)
    return response


def validate_email(email):
    if "@" not in email:
        return False
    return True


def calculate_salary(employee):
    return employee.base_salary + employee.bonus


def generate_invoice(order):
    total = order.price * order.quantity
    return total


def send_notification(message):
    print(message)
"""

    print("STEP 1 → Chunking code...\n")

    # Smaller chunk size so functions are separated better
    chunks = chunk_code(
        file_path="contact_service.py",
        content=sample_code,
        chunk_size=5
    )

    for chunk in chunks:
        print(chunk)
        print("-" * 60)

    print("\nSTEP 2 → Saving chunks to ChromaDB...\n")

    store = VectorStore()

    # IMPORTANT:
    # If you get duplicate ID errors,
    # delete the local chroma_db/ folder and rerun.
    store.add_chunks(chunks)

    print("Chunks stored successfully.\n")

    print("STEP 3 → Semantic search...\n")

    queries = [
        "HTTP request without error handling",
        "email format validation",
        "salary calculation logic"
    ]

    for query in queries:
        print(f"\nQUERY: {query}\n")

        results = store.search_similar_code(
            query=query,
            top_k=2
        )

        print("Search Results:\n")
        print(results)
        print("=" * 80)


if __name__ == "__main__":
    run_test()
