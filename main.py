import streamlit as st
import requests
from flask import Flask, request, jsonify
from diffusers import StableDiffusionPipeline
import torch
from PIL import Image
import io
import base64

# --- Flask Backend (Embedded) ---

app = Flask(__name__)

try:
    pipe = StableDiffusionPipeline.from_pretrained("runwayml/stable-diffusion-v1-5", torch_dtype=torch.float16)
    pipe = pipe.to("cuda")
except Exception as e:
    print(f"Error loading Diffusers model: {e}")
    pipe = None

def generate_logos_from_api(company_name, style, colors, focus):
    return [
        f"https://placehold.co/150x100?text={company_name}+{style}+{focus}+1",
        f"https://placehold.co/150x100?text={company_name}+{style}+{focus}+2",
        f"https://placehold.co/150x100?text={company_name}+{style}+{focus}+3",
    ]

def generate_logo_with_diffusers(prompt):
    if pipe is None:
        return None
    try:
        image = pipe(prompt).images[0]
        buffered = io.BytesIO()
        image.save(buffered, format="PNG")
        img_str = base64.b64encode(buffered.getvalue()).decode()
        return f'data:image/png;base64,{img_str}'
    except Exception as e:
        print(f"Diffusers error: {e}")
        return None

@app.route("/generate_logos", methods=["POST"])
def generate_logos():
    data = request.get_json()
    company_name = data["company_name"]
    company_focus = data["company_focus"]
    style = data["style"]
    colors = data["colors"]
    use_diffusers = data["use_diffusers"]

    if use_diffusers:
        if pipe is None:
            return jsonify({"error": "Diffusers model not loaded"}), 500
        prompt = f"A {style} logo for {company_name}, {colors}, {company_focus}"
        base64_img = generate_logo_with_diffusers(prompt)
        if base64_img:
            return jsonify({"image_base64": base64_img})
        else:
            return jsonify({"error": "Diffusers logo generation failed."}), 500
    else:
        logo_urls = generate_logos_from_api(company_name, style, colors, company_focus)
        return jsonify({"logo_urls": logo_urls})

# --- Streamlit Frontend (Embedded) ---

st.title("LogoCraft Chatbot")

company_name = st.text_input("Company Name:")
company_focus = st.text_input("Company Focus:")
style = st.selectbox("Logo Style:", ["Modern", "Minimalist", "Abstract", "Playful"])
colors = st.text_input("Color Preferences:")
use_diffusers = st.checkbox("Use Diffusers (slower, better quality)")

if st.button("Generate Logos"):
    if not company_name or not company_focus or not style or not colors:
        st.error("Please fill in all fields.")
    else:
        try:
            response = requests.post("http://127.0.0.1:5000/generate_logos", json={
                "company_name": company_name,
                "company_focus": company_focus,
                "style": style,
                "colors": colors,
                "use_diffusers": use_diffusers,
            })
            response.raise_for_status()
            data = response.json()

            if use_diffusers:
                if data["image_base64"]:
                    st.image(data["image_base64"], caption="Generated Logo", use_column_width=True)
                else:
                    st.error(data.get("error", "Diffusers logo generation failed."))
            else:
                for i, url in enumerate(data["logo_urls"]):
                    st.image(url, caption=f"Logo Option {i+1}", use_column_width=True)

        except requests.exceptions.RequestException as e:
            st.error(f"Error connecting to backend: {e}")
        except ValueError:
            st.error("Invalid response from backend.")
        except Exception as e:
            st.error(f"An unexpected error occurred: {e}")

# --- Run Both (Streamlit and Flask) ---

if __name__ == "_main_":
    import threading
    threading.Thread(target=app.run, kwargs={'use_reloader': False}).start()
    st.write("Flask backend started. Streamlit app running...")
