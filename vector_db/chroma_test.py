import chromadb
client = chromadb.PersistentClient(path="test_db")
collection = client.create_collection("demo")
collection.add(documents=["This is a test vector"], ids=["1"])
result = collection.query(query_texts=["test"], n_results=1)
print(result)
