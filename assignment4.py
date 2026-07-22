import streamlit as st
import requests
import urllib.parse
import random

# App title
st.title("🎨 AI Image Studio")

# Sidebar settings
st.sidebar.header("Settings")

# Select art style
art_style = st.sidebar.selectbox(
    "Select Art Style",
    [
        "Photorealistic",
        "Anime",
        "Sketch",
        "Cyberpunk",
        "3D Render",
        "Watercolor"
    ]
)

# Image size
image_width = st.sidebar.slider(
    "Image Width",
    256,
    1024,
    768
)

image_height = st.sidebar.slider(
    "Image Height",
    256,
    1024,
    768
)

# Magic Enhance option
magic_enhance = st.sidebar.checkbox("✨ Enable Magic Enhance")

# User prompt
user_prompt = st.text_input("Describe your image")

# Buttons
generate = st.button("Generate Image")
surprise = st.button("🎲 Surprise Me!")

# Random prompts
surprise_prompts = [
    "An astronaut riding a horse on Mars",
    "A cyberpunk street food vendor in Tokyo",
    "A dragon sleeping on floating islands",
    "A giant turtle carrying a futuristic city",
    "A robot painting a sunset"
]


# Function to generate image
def generate_image(prompt):

    # Add art style
    full_prompt = f"{prompt}, {art_style}"

    # Add enhancement words
    if magic_enhance:
        full_prompt += (
            ", masterpiece, 8k resolution, highly detailed,"
            " trending on artstation,"
            " unreal engine 5 render"
        )

    # Encode prompt
    encoded_prompt = urllib.parse.quote(full_prompt)

    # Create URL with width and height
    url = (
        f"https://image.pollinations.ai/prompt/{encoded_prompt}"
        f"?width={image_width}&height={image_height}"
    )

    # Show loading message
    with st.spinner("Generating image..."):

        response = requests.get(url)

    # Display image
    if response.status_code == 200:

        st.image(
            response.content,
            caption="Generated Image",
            use_container_width=True
        )

        st.download_button(
            label="Download Image",
            data=response.content,
            file_name=f"{art_style}_image.png",
            mime="image/png"
        )

    else:
        st.error("Image generation failed.")


# Generate from user prompt
if generate:

    if user_prompt.strip() == "":
        st.warning("Please enter an image prompt.")

    else:
        generate_image(user_prompt)


# Surprise Me feature
if surprise:

    random_prompt = random.choice(surprise_prompts)

    st.info(f"Random Prompt: {random_prompt}")

    generate_image(random_prompt)