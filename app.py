# streamlit_app.py (Frontend)
import streamlit as st
import requests

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
            response.raise_for_status()  # Raise HTTPError for bad responses (4xx or 5xx)
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
