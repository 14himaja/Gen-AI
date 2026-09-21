from app.database import db

queries = [
    "What is the coverage limit for Ayushman Bharat PM-JAY?",
    "Do you offer discounts for senior citizens on medicines?",
    "What are the rules for visiting hours in ICU?",
    "How much refund do I get if I cancel an appointment 3 hours before?",
    "What documents are needed for CGHS cashless admission?",
    "Is there any financial aid or concession for low income EWS patients?"
]

print("=== TESTING RAG KNOWLEDGE BASE SEARCH ===")
for q in queries:
    results = db.search_knowledge_base(q)
    print(f"\nQUERY: '{q}'")
    print(f"Retrieved Chunks: {len(results)}")
    if results:
        top = results[0]
        print(f"Top Match Source: {top.get('source')}")
        print(f"Top Match Topic: {top.get('topic')}")
        snippet = top.get('content')[:180].replace('₹', 'INR ')
        print(f"Content Snippet: {snippet}...")
