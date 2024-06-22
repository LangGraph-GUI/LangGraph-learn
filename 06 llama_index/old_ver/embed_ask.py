from langchain_community.embeddings import OllamaEmbeddings
from langchain_community.chat_models import ChatOllama
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
import chromadb

# Initialize the embedding model
embed_model = OllamaEmbeddings(model="mistral")

# Path to the markdown file
file_path = "./data/product.md"

# Function to read the content of the file
def load_file_content(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        return file.read()

# Read the content from the file
file_content = load_file_content(file_path)

# Embed the content of the file
document_embeddings = embed_model.embed_documents([file_content])

# Initialize ChromaDB client and create a collection
client = chromadb.Client()
collection = client.create_collection(name="docs")

# Store the document and its embedding in the collection
collection.add(
    ids=["0"],
    embeddings=document_embeddings,
    documents=[file_content]
)

# Specify the local language model
local_llm = "phi3"

# Initialize the ChatOllama model with desired parameters
llm = ChatOllama(model=local_llm, format="json", temperature=0)

# Define the prompt template
template = "Question: {question}\nAnswer: Let's think step by step."
prompt = PromptTemplate.from_template(template)

# Define the langchain pipeline
llm_chain = prompt | llm | StrOutputParser()

# Function to answer questions using RAG
def answer_question(question):
    # Generate an embedding for the question
    query_embedding = embed_model.embed_query(question)
    
    # Retrieve the most relevant document
    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=1
    )

    most_relevant_doc = results['documents'][0][0]
    print(f"Most relevant document: {most_relevant_doc}")

    # Format the prompt with the input variable
    formatted_prompt = prompt.format(question=f"Using this data: {most_relevant_doc}. Respond to this prompt: {question}")

    # Generate a response using the langchain pipeline
    generation = llm_chain.invoke(formatted_prompt)
    return generation

# Example usage
question = "What features does the product have?"
answer = answer_question(question)
print(f"Answer: {answer}")
