from langchain_community.embeddings import OllamaEmbeddings
import chromadb
import requests
import json

# Initialize the embedding model
embed_model = OllamaEmbeddings(model="mistral")

# Documents to be embedded
documents = [
    "Llamas are members of the camelid family meaning they're pretty closely related to vicuñas and camels",
    "Llamas were first domesticated and used as pack animals 4,000 to 5,000 years ago in the Peruvian highlands",
    "Llamas can grow as much as 6 feet tall though the average llama between 5 feet 6 inches and 5 feet 9 inches tall",
    "Llamas weigh between 280 and 450 pounds and can carry 25 to 30 percent of their body weight",
    "Llamas are vegetarians and have very efficient digestive systems",
    "Llamas live to be about 20 years old, though some only live for 15 years and others live to be 30 years old",
]

# Generate embeddings for the documents
embeddings = embed_model.embed_documents(documents)

# Initialize ChromaDB client and create a collection
client = chromadb.Client()
collection = client.create_collection(name="docs")

# Store each document and its embedding in the collection
for i, embedding in enumerate(embeddings):
    collection.add(
        ids=[str(i)],
        embeddings=[embedding],
        documents=[documents[i]]
    )

# Query the database with a prompt
query = "What animals are llamas related to?"
query_embedding = embed_model.embed_query(query)

# Retrieve the most relevant document
results = collection.query(
    query_embeddings=[query_embedding],
    n_results=1
)

most_relevant_doc = results['documents'][0][0]
print(f"Most relevant document: {most_relevant_doc}")

# Generate a response using the prompt and the retrieved document
url = "http://localhost:11434/api/generate"
headers = {"Content-Type": "application/json"}
data = {
    "model": "mistral",
    "prompt": f"Using this data: {most_relevant_doc}. Respond to this prompt: {query}",
    "stream": False
}

response = requests.post(url, headers=headers, data=json.dumps(data))
if response.status_code == 200:
    response_json = response.json()
    print(f"Response: {response_json['response']}")
else:
    print(f"Error: {response.status_code} - {response.text}")
