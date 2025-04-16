from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from typing import List, Dict, Optional
import base64
from huggingface_hub import InferenceClient
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Waste Classification API",
    description="API for waste classification and sustainability recommendations",
    version="1.0.0"
)

# Initialize the InferenceClient
try:
    client = InferenceClient(
        provider="together",
        api_key="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",  # Move this to environment variables in production
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
    if not image.content_type.startswith('image/'):
        raise HTTPException(status_code=400, detail="File must be an image")

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
        return {"result": result}

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
    """
    try:
        items_str = ", ".join(request.items)
        
        messages = [{
            "role": "user",
            "content": [
                {
                    "type": "text",
                    "text": f"""
You are an creative expert in sustainability. For the waste items "{items_str}", return only a valid JSON object:
{{
    "recycling_tips": ["", "", ""],         # 3 creative DIY ideas (≤12 words)
    "environmental_facts": ["", "", ""], # 3 shocking environmental facts (≤20 words)
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
        
        # Parse the string into a Python dictionary
        import json
        parsed_result = json.loads(cleaned_result)
        
        # Return the clean dictionary directly
        return parsed_result

    except HTTPException:
        raise
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
        
        # Parse the string into a Python dictionary
        import json
        parsed_result = json.loads(cleaned_result)
        
        # Return the clean dictionary directly
        return parsed_result

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error in classify endpoint: {str(e)}")
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