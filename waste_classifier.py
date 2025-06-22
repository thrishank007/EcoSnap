from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Dict, Optional
import base64
from huggingface_hub import InferenceClient
import logging
from datetime import datetime
import os
import json
import re

# import for HuggingFaceEmbeddings
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import TextLoader, DirectoryLoader


# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Waste Classification API",
    description="API for waste classification and sustainability recommendations",
    version="1.0.0"
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Function to generate mock data (simplified version - use your full generator)
def generate_mock_data():
    """Generate mock sustainability data for RAG"""
    data_dir = "./sustainability_data"
    os.makedirs(data_dir, exist_ok=True)
    
    # Create a simple example file
    example_content = """
    # Plastic Waste Sustainability Information
    
    ## Recycling Guidelines
    To recycle plastic bottles, first rinse thoroughly, then place in appropriate bin. This helps reduce landfill waste.
    
    ## Creative Reuse
    Turn old plastic bottles into garden planters by cutting and reshaping. Perfect for home decoration.
    
    ## Environmental Impact
    Plastic bottles take 450 years to decompose in landfills, releasing microplastics.
    
    ## Disposal Methods
    1. Remove labels before disposal.
    2. Take to collection center.
    3. Remember to check local regulations.
    """
    
    with open(os.path.join(data_dir, "plastic_general_info.txt"), "w") as f:
        f.write(example_content)
    
    logger.info("Generated mock sustainability data")

# Initialize RAG system with HuggingFace embeddings
def initialize_sustainability_rag():
    """Initialize the RAG system with sustainability data using HuggingFace embeddings"""
    try:
        # Check if data exists
        data_dir = "./sustainability_data"
        if not os.path.exists(data_dir) or len(os.listdir(data_dir)) == 0:
            logger.warning("Sustainability data not found. Generating mock data...")
            generate_mock_data()
            logger.info("Mock data generated successfully")
        
        # Use HuggingFace embeddings instead of OpenAI
        # This uses the all-MiniLM-L6-v2 model which is small and fast
        embeddings = HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-MiniLM-L6-v2"
        )
        
        # Check if vector store already exists
        if os.path.exists("./faiss_index"):
            # Add allow_dangerous_deserialization=True to fix the pickle loading issue
            vector_store = FAISS.load_local(
                "./faiss_index", 
                embeddings,
                allow_dangerous_deserialization=True
            )
            logger.info("Loaded existing vector store")
        else:
            # Load and process documents
            loader = DirectoryLoader(data_dir, glob="**/*.txt")
            documents = loader.load()
            vector_store = FAISS.from_documents(documents, embeddings)
            vector_store.save_local("./faiss_index")
        return vector_store
    except Exception as e:
        logger.error(f"Error initializing sustainability RAG: {str(e)}")
        raise
# Initialize the global vector store
VECTOR_STORE = initialize_sustainability_rag()

# Initialize the InferenceClient
try:
    client = InferenceClient(
        provider="together",
        api_key=os.getenv("TOGETHER_API_KEY", "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"),
    )
except Exception as e:
    logger.error(f"Failed to initialize InferenceClient: {str(e)}")
    raise

# Pydantic models for request/response validation
class ItemsRequest(BaseModel):
    items: List[str] = Field(..., min_items=1, max_items=10, description="List of waste items to analyze")
    idea: Optional[str] = Field(None, description="Specific DIY idea to generate")

class SustainabilityResponse(BaseModel):
    recycling_tips: List[str] = Field(..., min_items=3, max_items=3)
    environmental_facts: List[str] = Field(..., min_items=3, max_items=3)
    disposal_methods: List[str] = Field(..., min_items=3, max_items=3)

class ClassificationResponse(BaseModel):
    result: List[str]

# Utility functions
async def encode_image_to_base64(image: UploadFile) -> str:
    """Convert uploaded image to base64 string."""
    try:
        image_bytes = await image.read()
        return base64.b64encode(image_bytes).decode("utf-8")
    except Exception as e:
        logger.error(f"Error encoding image: {str(e)}")
        raise HTTPException(status_code=400, detail="Invalid image file")

async def get_llm_completion(messages: List[Dict], max_tokens: int = 512) -> str:
    """Get completion from LLM model."""
    try:
        completion = client.chat.completions.create(
            model="meta-llama/Llama-4-Scout-17B-16E-Instruct",
            messages=messages,
            max_tokens=max_tokens,
        )
        return completion.choices[0].message["content"]
    except Exception as e:
        logger.error(f"Error getting LLM completion: {str(e)}")
        raise HTTPException(status_code=500, detail="Error processing request")

# API endpoints
@app.post("/classify/", response_model=ClassificationResponse)
async def classify(image: UploadFile = File(...)):
    """
    Classify waste items in an uploaded image.
    Returns a list of identified waste items.
    """
 # Check if image is provided and has content_type
    if not image or not image.content_type or not image.content_type.startswith('image/'):
        raise HTTPException(status_code=400, detail="File must be an image")

    # Additional validation for file size (optional)
    if image.size and image.size > 10 * 1024 * 1024:  # 10MB limit
        raise HTTPException(status_code=400, detail="File too large. Maximum size is 10MB")

    try:
        base64_image = await encode_image_to_base64(image)
        
        messages = [{
            "role": "user",
            "content": [
                {
                    "type": "text",
                    "text": """Analyze the image and list **ONLY the names of waste items** visible. Follow these rules:  
1. Return a JSON array of strings (e.g., ["plastic bottle", "cardboard box", "banana peel"]).  
2. Include **only recyclable/compostable/landfill items** (ignore non-waste objects like furniture or electronics unless they're broken e-waste).  
3. Use simple, common names (e.g., 'glass jar', not 'transparent cylindrical container').  
4. If unsure about an item, omit it.  
5. Prioritize **material type** over brand names (e.g., 'aluminum can', not 'Coca-Cola can')."""
                },
                {
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:image/jpeg;base64,{base64_image}"
                    }
                }
            ]
        }]
        
        result = await get_llm_completion(messages)
        
        # Attempt to parse the response as JSON
        try:
            # Try to extract JSON array using regex if needed
            json_match = re.search(r'(\[.*\])', result, re.DOTALL)
            if json_match:
                items_list = json.loads(json_match.group(1))
            else:
                items_list = json.loads(result)
            return {"result": items_list}
        except json.JSONDecodeError:
            # If JSON parsing fails, log and return the raw result
            logger.warning(f"Failed to parse JSON from LLM response: {result}")
            return {"result": [result]}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error in classify endpoint: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.post("/generate/")
async def generate(request: ItemsRequest):
    """
    Generate sustainability recommendations for a list of waste items.
    Returns recycling tips, environmental facts, and disposal methods.
    Uses RAG to enhance responses with relevant sustainability information.
    """
    try:
        items_str = ", ".join(request.items)
        
        # Implement RAG - retrieve relevant context based on items
        context = ""
        if VECTOR_STORE is not None:
            # Query vector store for each item
            all_contexts = []
            for item in request.items:
                query = f"sustainability information about {item}"
                try:
                    docs = VECTOR_STORE.similarity_search(query, k=2)
                    if docs:
                        item_contexts = [doc.page_content for doc in docs]
                        all_contexts.extend(item_contexts)
                except Exception as e:
                    logger.warning(f"Error retrieving context for {item}: {str(e)}")
            
            # Create context from retrieved documents
            if all_contexts:
                context = "Here's relevant information about these items:\n\n" + "\n\n".join(all_contexts)
                logger.info(f"Retrieved context for items: {len(all_contexts)} documents")
            else:
                logger.warning("No relevant context found in the vector store")
        else:
            logger.warning("Vector store not initialized, proceeding without RAG")
        
        # Add the retrieved context to the prompt
        messages = [{
            "role": "user",
            "content": [
                {
                    "type": "text",
                    "text": f"""{context}

You are a creative expert in sustainability. For the waste items "{items_str}", return only a valid JSON object:
{{
    "recycling_tips": ["", "", ""],         # 3 creative DIY ideas (≤12 words)
    "environmental_facts": ["", "", ""],    # 3 shocking environmental facts (≤20 words)
    "disposal_methods": ["", "", ""]        # 3 location-aware disposal steps (≤15 words)
}}
Rules:
- Use plain language.
- No explanations or intro text.
- Do not repeat the item name.
- If unsure, leave arrays empty.
- Return ONLY the JSON object, no markdown formatting.
"""
                }
            ]
        }]
        
        # Get the completion from the LLM
        result = await get_llm_completion(messages)
        
        # Clean up the response by removing markdown formatting if present
        cleaned_result = result.strip('`').replace('```json\n', '').replace('\n```', '')
        
        # More robust JSON extraction
        try:
            # Try direct parsing first
            parsed_result = json.loads(cleaned_result)
        except json.JSONDecodeError:
            # If that fails, try to extract JSON with regex
            json_match = re.search(r'(\{.*\})', cleaned_result, re.DOTALL)
            if json_match:
                json_str = json_match.group(1)
                parsed_result = json.loads(json_str)
            else:
                raise ValueError("Could not extract valid JSON from LLM response")
        
        # Return the clean dictionary directly
        return parsed_result

    except HTTPException:
        raise
    except json.JSONDecodeError as e:
        logger.error(f"JSON parsing error: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to parse LLM response as JSON")
    except Exception as e:
        logger.error(f"Unexpected error in generate endpoint: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.post('/diy/')
async def diy(request: ItemsRequest):
    """
    Generate Complete Tutorial for DIY ideas using waste items.
    """
    try:
        items_str = ", ".join(request.items)
        idea = request.idea
        
        messages = [{
            "role": "user",
            "content": [
                {
                    "type": "text",
                    "text": f"""
You are an expert in creative sustainability and DIY projects. DIY using "{idea}" using the waste item(s) "{items_str}", return **only a valid JSON object** with the following structure:
{{
  "title": "string",                     // Catchy project name (e.g., "Plastic Bottle Bird Feeder")
  "materials": ["item1", "item2", ...],  // 5-7 recycled/household items (include quantities if needed)
  "steps": ["step1", "step2", ...],      // 5-8 concise, imperative-form instructions (e.g., "Cut the bottle in half")
  "difficulty": "Easy/Medium/Advanced",  // Choose one
  "safety_tip": "string"                 // Specific caution (e.g., "Wear gloves when cutting plastic")
}}

**Rules**:
1. Use only plain text—NO MARKDOWN.  
2. Prioritize recycled/repurposed materials.  
3. Steps must be actionable (start with verbs).  
4. Validate JSON syntax (commas, quotes, brackets).  
5. If unsure about a field, leave its value as an empty array/string.  
6. Difficulty must be one of: Easy, Medium, Advanced.  
7. Never repeat the item name in steps or materials.  
"""
                }
            ]
        }]
        # Get the completion from the LLM
        result = await get_llm_completion(messages)
        
        # Clean up the response by removing markdown formatting if present
        cleaned_result = result.strip('`').replace('```json\n', '').replace('\n```', '')
        
        # More robust JSON extraction
        try:
            # Try direct parsing first
            parsed_result = json.loads(cleaned_result)
        except json.JSONDecodeError:
            # If that fails, try to extract JSON with regex
            json_match = re.search(r'(\{.*\})', cleaned_result, re.DOTALL)
            if json_match:
                json_str = json_match.group(1)
                parsed_result = json.loads(json_str)
            else:
                raise ValueError("Could not extract valid JSON from LLM response")
        
        # Return the clean dictionary directly
        return parsed_result

    except HTTPException:
        raise
    except json.JSONDecodeError as e:
        logger.error(f"JSON parsing error: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to parse LLM response as JSON")
    except Exception as e:
        logger.error(f"Unexpected error in diy endpoint: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

# Health check endpoint
@app.get("/health")
async def health_check():
    """Check API health status."""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "version": app.version
    }

if __name__ == "__main__":
    import uvicorn
    
    # Start the FastAPI server
    logger.info("Starting FastAPI server on http://localhost:8000")
    uvicorn.run(app, host="0.0.0.0", port=8000)