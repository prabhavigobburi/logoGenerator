# app.py
from flask import Flask, render_template, request, jsonify, send_file
import torch
from diffusers import StableDiffusionPipeline
import io
from PIL import Image, ImageDraw, ImageFont
import os
import uuid

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'static/generated'
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Global variable for the model
pipe = None

def load_model():
    global pipe
    if pipe is None:
        try:
            # Try loading the full model
            model_id = "runwayml/stable-diffusion-v1-5"
            pipe = StableDiffusionPipeline.from_pretrained(
                model_id,
                torch_dtype=torch.float32  # Use float32 for CPU
            )
            # Check if CUDA is available and use it
            if torch.cuda.is_available():
                pipe = pipe.to("cuda")
            else:
                pipe = pipe.to("cpu")
                # Enable attention slicing for lower memory usage
                pipe.enable_attention_slicing()
            return pipe
        except Exception as e:
            print(f"Error loading model: {str(e)}")
            return None
    return pipe

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/generate', methods=['POST'])
def generate_logo():
    # Get form data
    description = request.form.get('description', '')
    style = request.form.get('style', 'Minimalist')
    colors = request.form.get('colors', 'Blue and Grey')
    width = int(request.form.get('width', 512))
    height = int(request.form.get('height', 512))
    steps = int(request.form.get('steps', 50))
    guidance = float(request.form.get('guidance', 7.5))
    
    try:
        # Try to load the model
        pipe = load_model()
        
        if pipe:
            # Use the model to generate the image
            enhanced_prompt = f"A professional {style.lower()} logo with {colors.lower()} colors. {description} High quality, vector style, suitable for business use."
            
            image = pipe(
                enhanced_prompt,
                width=width,
                height=height,
                num_inference_steps=steps,
                guidance_scale=guidance
            ).images[0]
        else:
            # Fallback to a simple generated image if model fails to load
            image = Image.new('RGB', (width, height), color='white')
            d = ImageDraw.Draw(image)
            
            # Parse the color
            color = colors.split(' ')[0].lower()
            if color == 'blue':
                bg_color = (30, 144, 255)
            elif color == 'red':
                bg_color = (220, 20, 60)
            elif color == 'green':
                bg_color = (46, 139, 87)
            elif color == 'purple':
                bg_color = (128, 0, 128)
            elif color == 'orange':
                bg_color = (255, 140, 0)
            elif color == 'black':
                bg_color = (0, 0, 0)
            else:
                bg_color = (100, 100, 100)
            
            # Create a simple colored placeholder with text
            d.rectangle([(0, 0), (width, height)], fill=bg_color)
            
            # Try to add text (if PIL supports it without additional fonts)
            try:
                d.text((width//4, height//3), f"{style} Logo", fill="white", font_size=40)
                d.text((width//4, height//2), description[:30], fill="white", font_size=20)
            except:
                # If text with font_size parameter fails, try the basic version
                d.text((width//4, height//3), f"{style} Logo", fill="white")
                d.text((width//4, height//2), description[:30], fill="white")
        
        # Save the image
        filename = f"logo_{uuid.uuid4().hex}.png"
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        image.save(filepath)
        
        return jsonify({
            'success': True,
            'image_url': f"/static/generated/{filename}",
            'prompt': enhanced_prompt if pipe else f"Simple {style} logo with {colors} colors"
        })
        
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        print(f"ERROR: {error_details}")  # Print to server console
        return jsonify({
            'success': False,
            'error': str(e),
            'details': error_details
        })

@app.route('/download/<filename>')
def download_file(filename):
    return send_file(os.path.join(app.config['UPLOAD_FOLDER'], filename), as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)
