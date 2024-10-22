from langchain_openai import ChatOpenAI
import os
from dotenv import load_dotenv

load_dotenv()

modal_name = "gpt-4"
apiKey = os.getenv("OPENAI_API_KEY")
end_point = os.getenv("LANGCHAIN_ENDPOINT")
project = os.getenv("LANGCHAIN_PROJECT")
temperature = 0.5
_BASE_URL = os.getenv("URL_LLAMA")
from litellm import completion

# Ensure API key is set
if not apiKey:
    print("OPENAI_API_KEY is", apiKey)
    raise ValueError("OPENAI_API_KEY is not set", )

# Initialize the OpenAI chat model (Check if endpoint/project is needed for your use case)
llm = ChatOpenAI(
    model=modal_name, 
    api_key=apiKey,
    temperature=temperature,
    verbose=True,
    # Uncomment these if you are indeed using them
    # endpoint=end_point,
    # project=project
)



def get_llm():
    return llm

def get_llm_modal_with_tools(tools):
    if tools is None:
        ValueError("you must be pass tool")
    
    return llm.bind_tools(tools)


def get_ollama_modal_with_tools(tools=None):
    if tools is None:
        raise ValueError("You must pass at least one tool.")
    
    # Define a custom wrapper for tool binding with Ollama completion
    def ollama_with_tools(prompt, **kwargs):
        response = ollama_completion()(prompt, **kwargs)  # Call the ollama model
        
        # After receiving response, run through the provided tools (simulating "binding tools")
        for tool in tools:
            if hasattr(tool, 'process'):  # Assuming tools have a process method
                response = tool.process(response)
        
        return response
    
    return ollama_with_tools