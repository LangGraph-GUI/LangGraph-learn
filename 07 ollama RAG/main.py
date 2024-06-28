from langchain_community.embeddings import OllamaEmbeddings
from langchain_community.chat_models import ChatOllama
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain.text_splitter import RecursiveCharacterTextSplitter
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

# Initialize the text splitter
text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=100)

# Split the document into chunks
chunks = text_splitter.split_text(file_content)

# Initialize ChromaDB client and create a collection
client = chromadb.Client()
collection = client.create_collection(name="docs")

# Embed each chunk and store it in the collection
for i, chunk in enumerate(chunks):
    chunk_embedding = embed_model.embed_documents([chunk])
    collection.add(
        ids=[str(i)],
        embeddings=chunk_embedding,
        documents=[chunk]
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
    
    # Retrieve the most relevant document chunks
    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=3  # Retrieve top 3 relevant chunks
    )

    relevant_docs = [result[0] for result in results['documents']]
    combined_docs = " ".join(relevant_docs)
    print(f"Most relevant documents combined: {combined_docs}")

    # Format the prompt with the input variable
    formatted_prompt = prompt.format(question=f"Using this data: {combined_docs}. Respond to this prompt: {question}")

    # Generate a response using the langchain pipeline
    generation = llm_chain.invoke(formatted_prompt)
    return generation

# Example usage
question = "What does the product look liked?"
answer = answer_question(question)
print(f"Answer: {answer}")
