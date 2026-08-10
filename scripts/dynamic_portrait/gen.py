
from hoi4dev import *

import base64
import os
from http import HTTPStatus
from dashscope import VideoSynthesis
import mimetypes
import dashscope

# --- Configuration (Assumes DASHSCOPE_API_KEY is set in environment) ---
# Set the base API URL (Using Beijing region as in the original tutorial)
dashscope.base_http_api_url = 'https://dashscope.aliyuncs.com/api/v1'
api_key = os.getenv("DASHSCOPE_API_KEY")

# --- Helper Function: For Base64 Encoding ---
# The format is data:{MIME_type};base64,{base64_data}
def encode_file(file_path):
    """Encodes a local image file to the DashScope Base64 string format."""
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Image file not found at: {file_path}")
        
    mime_type, _ = mimetypes.guess_type(file_path)
    if not mime_type or not mime_type.startswith("image/"):
        raise ValueError("Unsupported or unrecognizable image format")

    with open(file_path, "rb") as image_file:
        encoded_string = base64.b64encode(image_file.read()).decode('utf-8')
    return f"data:{mime_type};base64,{encoded_string}"

# --- Main Function ---
def generate_video_kf2v(prompt: str, image_path: str) -> str:
    """
    Generates a 5-second, 480P video using a prompt and a single image 
    for both the first and last frames.

    Args:
        prompt: The text prompt describing the video content and motion.
        image_path: The local path to the image to use as the start and end frame.

    Returns:
        The URL of the generated video, or an error message string.
    """
    if not api_key:
        return "Error: DASHSCOPE_API_KEY environment variable is not set."

    # Encode the local image file to Base64 format for use in the API call
    try:
        image_url = encode_file(image_path)
    except Exception as e:
        return f"Error encoding image: {e}"

    print('Submitting video generation task... please wait.')

    # API call to generate the video
    rsp = VideoSynthesis.call(
        api_key=api_key,
        # Model for Key Frame to Video (kf2v) synthesis
        model="wan2.2-kf2v-flash", 
        prompt=prompt,
        # Use the same image for first and last frame
        first_frame_url=image_url, 
        last_frame_url=image_url,   
        # Set resolution to 480P as requested
        resolution="480P", 
        # The wan2.2-kf2v-flash model's duration is fixed at 5s,
        # so we don't need to specify a 'duration' parameter.
        prompt_extend=False # Use prompt extension for potentially better results
    )

    if rsp.status_code == HTTPStatus.OK:
        video_url = rsp.output.video_url
        print(f'Successfully generated video! URL: {video_url}')
        return video_url
    else:
        error_message = (
            f'Failed to generate video. Status Code: {rsp.status_code}, '
            f'Error Code: {rsp.code}, Message: {rsp.message}'
        )
        print(error_message)
        return error_message

# --- Example Usage (Requires an image file named 'my_input_image.png' in the same directory) ---
# Note: This block will only run if you execute this script directly.
if __name__ == '__main__':
    # 1. Create a dummy image file for testing the path (Remove this and use your actual file)
    # Be sure to replace this with your actual image path!
    DUMMY_IMAGE_PATH = "./my_input_image.png"
    try:
        # Create a simple 1x1 black image file to satisfy the file check for demonstration
        from PIL import Image
        img = Image.new('RGB', (1, 1), color = 'black')
        img.save(DUMMY_IMAGE_PATH)
        print(f"Created a dummy image: {DUMMY_IMAGE_PATH}")
    except ImportError:
        print("Pillow (PIL) is not installed. Please install it (`pip install Pillow`) or ensure a real image file exists at the path below.")
    except Exception as e:
        print(f"Could not create dummy image. Please ensure a real image exists at: {DUMMY_IMAGE_PATH}. Error: {e}")
        
    # 2. Define your desired prompt and image path
    my_prompt = "A majestic eagle soaring over a snow-capped mountain range, with the camera slowly panning out to reveal a wider vista."
    my_image_path = DUMMY_IMAGE_PATH # Replace with the path to your actual first/last frame image!

    # 3. Call the function
    # result_url = generate_video_kf2v(my_prompt, my_image_path)
    # print("\nFinal Result (Video URL or Error):")
    # print(result_url)
    
    # 4. Clean up the dummy file (optional)
    # try:
    #     os.remove(DUMMY_IMAGE_PATH)
    #     print(f"Removed dummy image: {DUMMY_IMAGE_PATH}")
    # except Exception:
    #     pass

character_name = "AUTUMN_BLAZE"

character_folder = pjoin(f"./resources/characters/{character_name}/")

portrait_file = pjoin(character_folder, "portraits/default.png")

