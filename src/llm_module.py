import google.generativeai as genai
import requests
import os
from . import config

# Configure the Gemini API key
genai.configure(api_key=config.GEMINI_API_KEY)

# Initialize the GenerativeModel
# Note: For multimodal input (text and image), you'd typically use a model like 'gemini-pro-vision'.
# However, the user specified 'gemini-2.0-flash', which might be primarily text-based or have specific ways to handle multimodal input.
# We will start with text-based interaction and can extend to vision later if the model supports it directly
# or by passing image descriptions as text.

# For gemini-2.0-flash, it's likely a newer model. We'll assume it can handle text and potentially image data if passed correctly.
# The Gemini API typically uses `GenerativeModel(model_name)`
# For models like gemini-1.5-flash or gemini-1.5-pro, you can send images directly.
# Let's assume gemini-2.0-flash also supports this. If not, we'll need to adjust.

model = genai.GenerativeModel(config.GEMINI_MODEL_NAME)

def get_llm_response(prompt_text: str, image_path: str = None) -> str:
    """
    Gets a response from the Gemini LLM.
    Can optionally include an image for multimodal input if the model supports it.

    Args:
        prompt_text: The text prompt for the LLM.
        image_path: (Optional) Path to an image file for multimodal input.

    Returns:
        The LLM's text response.
    """
    try:
        if image_path and os.path.exists(image_path):
            # For multimodal input with Gemini, you typically pass a list of content parts
            # including text and image data (e.g., PIL.Image object or image bytes).
            # Let's try to load the image and pass it.
            # The exact way to pass images might vary slightly based on the specific Gemini model version
            # and SDK updates. We'll use a common approach.
            import PIL.Image
            img = PIL.Image.open(image_path)
            
            # Check if the model is a vision model, typically names contain 'vision'
            # Since 'gemini-2.0-flash' name doesn't explicitly state 'vision', we proceed with caution.
            # The `generate_content` method can accept a list of parts (text, image).
            response = model.generate_content([prompt_text, img])
        else:
            response = model.generate_content(prompt_text)
        
        # Handle potential streaming or multi-candidate responses if applicable
        # For simplicity, we'll assume a direct text response part.
        # You might need to inspect `response.parts` or `response.text` based on the API version.
        if hasattr(response, 'text') and response.text:
            return response.text
        elif response.parts:
            # If the response has parts, iterate and concatenate text parts
            full_response = "".join(part.text for part in response.parts if hasattr(part, 'text'))
            if full_response:
                return full_response
        return "Error: Could not extract text from LLM response."

    except Exception as e:
        print(f"Error interacting with LLM: {e}")
        # More specific error handling can be added here based on Gemini API exceptions
        if "API key not valid" in str(e):
            return "LLM Error: API key is not valid. Please check your configuration."
        elif "content has no parts" in str(e).lower() or "response.text" in str(e).lower():
             # This can happen if the model expects a different input format or if the response structure is unexpected
            try:
                # Fallback to trying to get text from the first candidate if available
                if response.candidates and response.candidates[0].content and response.candidates[0].content.parts:
                    return "".join(part.text for part in response.candidates[0].content.parts if hasattr(part, 'text'))
                return "LLM Error: Received an empty or unparseable response from the model."
            except Exception as inner_e:
                print(f"Error trying to parse LLM response candidates: {inner_e}")
                return f"LLM Error: {e}"
        return f"LLM Error: {e}"

if __name__ == '__main__':
    # Test the LLM module (requires a valid API key to be set in config.py or environment)
    print("Testing LLM module...")
    # Create a dummy image for testing multimodal input if needed
    # For now, let's test with text only first.
    # Ensure config.py has the GEMINI_API_KEY set or it's in the environment.
    
    # Text-only test
    text_prompt = "Hello, what can you do?"
    print(f"Sending text prompt: {text_prompt}")
    response_text = get_llm_response(text_prompt)
    print(f"LLM Response (text-only): {response_text}")

    # Multimodal test (requires an image file)
    # Create a dummy image file for testing if you don't have one
    # For example, you could use Pillow to create a simple image:
    # from PIL import Image, ImageDraw
    # img_test = Image.new('RGB', (60, 30), color = 'red')
    # img_test.save('/home/ubuntu/multimodal_assistant/test_image.png')
    # test_image_path = '/home/ubuntu/multimodal_assistant/test_image.png'
    
    # print(f"\nSending multimodal prompt with image: {test_image_path}")
    # multimodal_prompt = "What do you see in this image?"
    # response_multimodal = get_llm_response(multimodal_prompt, image_path=test_image_path)
    # print(f"LLM Response (multimodal): {response_multimodal}")

