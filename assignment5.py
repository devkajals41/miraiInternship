import streamlit as st
import google.generativeai as genai
import json
import re
import io
import os
import traceback
import requests
from gtts import gTTS
from dotenv import load_dotenv

# grabs GEMINI_API_KEY out of the .env file so I don't have to hardcode it anywhere
load_dotenv()

st.set_page_config(page_title="AI Visual Novel", page_icon="🎮", layout="wide")


# caching this so streamlit doesn't reconnect to the Gemini API on every single rerun
@st.cache_resource
def get_gemini_client(api_key: str):
    genai.configure(api_key=api_key)
    return genai.GenerativeModel("gemini-3.5-flash")


# sidebar with the story settings the user picks before we start generating anything
with st.sidebar:
    st.title("📖 Story Settings")

    genre = st.selectbox(
        "Story Genre",
        ["Fantasy", "Sci-Fi", "Horror", "Mystery Noir", "Post-Apocalyptic", "Comedy"],
    )
    art_style = st.selectbox(
        "Art Style",
        ["Anime", "Watercolor", "Pixel Art", "Photorealistic", "Comic Book", "Studio Ghibli style"],
    )

    st.divider()
    if st.button("🔄 Restart Story"):
        # wipe everything and let it rebuild from scratch on rerun
        for key in ["chat", "history", "story_text", "image_bytes", "audio_bytes", "options"]:
            st.session_state.pop(key, None)
        st.rerun()

st.title("🎮 AI-Powered Visual Novel")

# no key typed into the UI on purpose — pulling it from .env (or secrets.toml as a fallback)
api_key = os.environ.get("GEMINI_API_KEY")
if not api_key:
    try:
        api_key = st.secrets.get("GEMINI_API_KEY")
    except Exception:
        api_key = None

if not api_key:
    st.error(
        "No Gemini API key found. Add GEMINI_API_KEY=your-key-here to a .env file "
        "next to app.py."
    )
    st.stop()

# first time the app loads, set up the chat object and the system prompt once
if "chat" not in st.session_state:
    model = get_gemini_client(api_key)

    system_prompt = f"""
You are the narrative engine for an interactive visual novel.
Genre: {genre}. Art style for illustrations: {art_style}.

STRICT OUTPUT RULE:
You must respond ONLY with a valid JSON object (no markdown fences, no extra commentary)
with exactly these three keys:

1. "story_text": A vivid narrative paragraph (4-8 sentences) continuing the story.
2. "image_prompt": A heavily detailed, descriptive prompt (art style, lighting, mood,
   composition) suitable for an AI image generator, matching the current scene.
3. "options": A JSON array of 2 to 3 short, distinct strings representing the choices
   the reader can take next.

Never include anything outside the JSON object.
"""
    st.session_state.chat = model.start_chat(history=[])
    st.session_state.system_prompt = system_prompt
    st.session_state.history = []
    st.session_state.story_text = None
    st.session_state.image_bytes = None
    st.session_state.audio_bytes = None
    st.session_state.options = []
    st.session_state.last_error = None


def extract_json(raw_text: str) -> dict:
    # gemini ignores the "no markdown fences" instruction sometimes, so just strip them out
    cleaned = raw_text.strip()
    cleaned = re.sub(r"^```json\s*|^```\s*|```$", "", cleaned, flags=re.MULTILINE).strip()
    return json.loads(cleaned)


def send_turn(user_message: str):
    # this is the main function — sends the player's choice to Gemini, gets back
    # the JSON, and updates everything on screen (text, image, audio, buttons)
    try:
        prompt = user_message
        if not st.session_state.history:
            # only need to send the big system prompt on the very first message
            prompt = st.session_state.system_prompt + "\n\nBegin the story now. Opening action: " + user_message

        response = st.session_state.chat.send_message(prompt)
        data = extract_json(response.text)

        st.session_state.story_text = data.get("story_text", "")
        st.session_state.options = data.get("options", [])
        st.session_state.history.append(user_message)

        # go grab the image and narration for this new scene
        fetch_image(data.get("image_prompt", ""))
        generate_narration(st.session_state.story_text)

    except json.JSONDecodeError as e:
        # happens occasionally if the model adds extra text before/after the JSON
        print("JSON parse failed. Raw response was:\n", response.text)
        st.session_state.last_error = f"The story engine returned a malformed response: {e}"
    except Exception as e:
        # print the full traceback to the terminal so it's easy to debug,
        # and keep a short version on screen since toasts disappear too fast to read
        traceback.print_exc()
        st.session_state.last_error = f"Story engine error: {e}"


def fetch_image(image_prompt: str):
    # pollinations is free but sometimes slow/down, so this can't be allowed to crash the app
    if not image_prompt:
        st.session_state.image_bytes = None
        return
    try:
        encoded_prompt = requests.utils.quote(f"{image_prompt}, {art_style}")
        url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?width=768&height=512&nologo=true"
        resp = requests.get(url, timeout=25)
        resp.raise_for_status()
        st.session_state.image_bytes = resp.content
    except Exception:
        st.session_state.image_bytes = None
        st.toast("🖼️ Image server is busy, skipping visual...")


def generate_narration(story_text: str):
    # same idea as fetch_image — turn the text into speech, but don't crash if it fails
    if not story_text:
        st.session_state.audio_bytes = None
        return
    try:
        tts = gTTS(text=story_text, lang="en")
        buf = io.BytesIO()
        tts.write_to_fp(buf)
        buf.seek(0)
        st.session_state.audio_bytes = buf.read()
    except Exception:
        st.session_state.audio_bytes = None
        st.toast("🔊 Narration engine is busy, skipping audio...")


# on the very first load there's no story yet, so kick things off automatically
if st.session_state.story_text is None:
    with st.spinner("Weaving the opening scene..."):
        send_turn(f"Start a brand new {genre.lower()} story and set the opening scene.")

# show the last error on screen (not just a toast) so it doesn't vanish before you can read it
if st.session_state.get("last_error"):
    st.error(st.session_state.last_error)
    st.caption("Full traceback was printed to your terminal.")

# main scene layout — image on the left, text + narration on the right
col1, col2 = st.columns([1, 1])

with col1:
    if st.session_state.image_bytes:
        st.image(st.session_state.image_bytes, use_container_width=True)
    else:
        st.info("No image available for this scene.")

with col2:
    st.markdown(f"### {st.session_state.story_text or ''}")
    if st.session_state.audio_bytes:
        st.audio(st.session_state.audio_bytes, format="audio/mp3")

st.divider()

# buttons here aren't hardcoded — they come straight from whatever "options" the
# AI decided to give back for this scene, so the choices change every turn
st.subheader("What do you do next?")
button_cols = st.columns(len(st.session_state.options) or 1)

for i, option_text in enumerate(st.session_state.options):
    with button_cols[i]:
        if st.button(option_text, use_container_width=True, key=f"option_{len(st.session_state.history)}_{i}"):
            with st.spinner("The story continues..."):
                send_turn(option_text)
            st.rerun()