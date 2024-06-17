from langchain_community.chat_models import ChatOllama
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser

# Specify the local language model
local_llm = "phi3"

# Initialize the ChatOllama model with desired parameters
llm = ChatOllama(model=local_llm, format="json", temperature=0)

# Define the prompt template
template = "Question: {question}\nAnswer: Let's think step by step."
prompt = PromptTemplate.from_template(template)

# Format the prompt with the input variable
formatted_prompt = prompt.format(question="Tell me about you")


llm_chain = prompt | llm | StrOutputParser()
generation = llm_chain.invoke(formatted_prompt)

print(generation)
