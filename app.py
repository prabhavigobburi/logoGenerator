from flask import Flask, request, jsonify
from flask_cors import CORS
import io
import base64
import os
import requests
from PIL import Image, ImageDraw, ImageFont
import random
import logging

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

app = Flask(__name__)
# Enable CORS with more specific settings
CORS(app, resources={r"/*": {"origins": "*"}})

# Logo color palettes for mock generation
COLOR_PALETTES = {
    "blue": [(25, 119, 181), (79, 159, 210), (139, 189, 232)],
    "green": [(39, 174, 96), (82, 190, 128), (155, 219, 172)],
    "red": [(192, 57, 43), (231, 76, 60), (243, 156, 145)],
    "purple": [(142, 68, 173), (155, 89, 182), (187, 143, 206)],
    "orange": [(230, 126, 34), (241, 196, 15), (248, 196, 113)],
    "monochrome": [(52, 73, 94), (127, 140, 141), (189, 195, 199)],
}

def create_mock_logo(company_name, style="minimalist", color_scheme="blue"):
    """
    Creates a simple mock logo using PIL.
    """
    logger.info(f"Creating mock logo for {company_name} with style {style} and colors {color_scheme}")
    width, height = 500, 500
    image = Image.new('RGB', (width, height), (255, 255, 255))
    
    try:
        draw = ImageDraw.Draw(image)
        
        # Select a color palette
        if color_scheme.lower() in COLOR_PALETTES:
            colors = COLOR_PALETTES[color_scheme.lower()]
        else:
            # Default to a random palette
            colors = random.choice(list(COLOR_PALETTES.values()))
        
        # Draw background elements based on style
        if style == "minimalist":
            # Simple circle background
            draw.ellipse((150, 150, 350, 350), fill=colors[0])
        elif style == "geometric":
            # Triangular elements
            draw.polygon([(250, 100), (100, 350), (400, 350)], fill=colors[0])
        elif style == "modern":
            # Rectangles
            draw.rectangle((100, 100, 400, 200), fill=colors[0])
            draw.rectangle((150, 200, 350, 400), fill=colors[1])
        else:
            # Default abstract shape
            draw.rectangle((100, 100, 400, 400), fill=colors[0])
            draw.ellipse((150, 150, 350, 350), fill=colors[1])
        
        # Add company initial in the center
        initial = company_name[0].upper() if company_name else "L"
        
        # Handle text drawing without truetype fonts (which may not be available)
        try:
            # Try to use default font for text
            default_font = ImageFont.load_default()
            
            # Calculate center position (approx)
            text_position = (width//2 - 10, height//2 - 10)
            
            # Draw the initial
            draw.text(text_position, initial, (255, 255, 255), font=default_font)
            
            # Draw company name at the bottom
            name_position = (width//2 - len(company_name)*3, 400)
            draw.text(name_position, company_name, colors[0], font=default_font)
            
        except Exception as text_error:
            logger.error(f"Failed to add text to logo: {text_error}")
            # If text drawing fails, still return the image without text
        
        return image
        
    except Exception as e:
        logger.error(f"Error creating mock logo: {e}")
        # If any error occurs, create a super simple fallback image
        fallback = Image.new('RGB', (500, 500), (79, 159, 210))
        return fallback

@app.route('/generate_logos', methods=['POST'])
def generate_logos():
    logger.info("Logo generation request received")
    
    try:
        data = request.json
        logger.debug(f"Request data: {data}")
        
        company_name = data.get('company_name', '')
        company_focus = data.get('company_focus', '')
        style = data.get('style', 'minimalist')
        colors = data.get('colors', '')
        use_diffusers = data.get('use_diffusers', False)  # Ignored since we're not using torch
        
        # Validate required fields
        if not company_name or not company_focus:
            logger.warning("Missing required fields")
            return jsonify({"error": "Company name and focus are required"}), 400
        
        logger.info(f"Generating logo for {company_name}, {company_focus}, style: {style}, colors: {colors}")
        
        # Generate mock logos as our main strategy
        try:
            # Parse color preferences to determine color scheme
            color_scheme = "blue"  # default
            if colors:
                if "blue" in colors.lower():
                    color_scheme = "blue"
                elif "green" in colors.lower():
                    color_scheme = "green"
                elif "red" in colors.lower():
                    color_scheme = "red"
                elif "purple" in colors.lower():
                    color_scheme = "purple"
                elif "orange" in colors.lower() or "yellow" in colors.lower():
                    color_scheme = "orange"
                elif "black" in colors.lower() or "white" in colors.lower() or "gray" in colors.lower():
                    color_scheme = "monochrome"
            
            # Create image and convert to base64
            logger.info("Creating logo image")
            image = create_mock_logo(company_name, style, color_scheme)
            
            buffered = io.BytesIO()
            image.save(buffered, format="PNG")
            img_str = base64.b64encode(buffered.getvalue()).decode()
            image_data = f"data:image/png;base64,{img_str}"
            
            logger.info("Logo generated successfully")
            # Return a single image for simplicity
            return jsonify({"image_base64": image_data})
            
        except Exception as img_error:
            logger.error(f"Error generating image: {img_error}")
            # Fall back to placeholder if image generation fails
            return jsonify({
                "logo_urls": ["https://via.placeholder.com/500x500?text=Logo"]
            })
            
    except Exception as e:
        logger.error(f"Unexpected error in generate_logos: {e}")
        return jsonify({"error": f"Server error: {str(e)}"}), 500

# Add a simple test endpoint
@app.route('/test', methods=['GET'])
def test():
    return jsonify({"status": "Backend server is running"}), 200

if __name__ == '__main__':
    logger.info("Backend server starting on http://127.0.0.1:5000")
    app.run(host='127.0.0.1', port=5000, debug=True)
