import streamlit as st
import requests
from bs4 import BeautifulSoup
from duckduckgo_search import DDGS
import speech_recognition as sr
import json
import os
from PIL import Image
from io import BytesIO


BOOKMARK_FILE = "bookmarks.json"

def load_bookmarks():
    if os.path.exists(BOOKMARK_FILE):
        with open(BOOKMARK_FILE, "r") as f:
            return json.load(f)
    return []

def save_bookmark(title, url):
    bookmarks = load_bookmarks()
    bookmarks.append({"title": title, "url": url})
    with open(BOOKMARK_FILE, "w") as f:
        json.dump(bookmarks, f, indent=4)

st.set_page_config(page_title="Bharat", layout="wide")

st.title("Bharat")

tab1, tab2, tab3 = st.tabs(["Search", "Browse URL", "Bookmarks"])

with tab1:
    col1, col2 = st.columns([4, 1])
    with col1:
        query = st.text_input("Search something:")
    with col2:
        if st.button("🎙️ Voice Search"):
            recognizer = sr.Recognizer()
            with sr.Microphone() as source:
                st.info("Listening...")
                audio = recognizer.listen(source)
                try:
                    query = recognizer.recognize_google(audio)
                    st.success(f"You said: {query}")
                except sr.UnknownValueError:
                    st.error("Sorry, could not understand.")
                except sr.RequestError:
                    st.error("Speech recognition failed!")

    if st.button("Search DuckDuckGo"):
        if query:
            results = []
            with DDGS() as ddgs:
                for r in ddgs.text(query, region='in-en', safesearch='moderate', max_results=5):
                    results.append(r)

            for result in results:
                st.markdown(f"### [{result['title']}]({result['href']})")
                st.write(result['body'])
                st.write("---")

with tab2:
    url = st.text_input("Enter URL (https://...)")
    screenshot = st.checkbox("📸 Show Screenshot Preview")

    if st.button("Open Page"):
        try:
            response = requests.get(url, timeout=5)
            soup = BeautifulSoup(response.text, "html.parser")
            title = soup.title.string if soup.title else "No Title"
            st.subheader(f"{title}")
            st.code(url)

            if st.button(" Save Bookmark"):
                save_bookmark(title, url)
                st.success("Bookmark saved!")

            st.text_area("Page Snippet:", soup.get_text()[:1000], height=300)

            # Screenshot preview
            if screenshot:
                api_url = f"https://image.thum.io/get/width/900/{url}"
                img_response = requests.get(api_url)
                if img_response.status_code == 200:
                    image = Image.open(BytesIO(img_response.content))
                    st.image(image, caption="Page Screenshot", use_column_width=True)
                else:
                    st.warning("Couldn't load screenshot.")

        except Exception as e:
            st.error(f"Error: {e}")

with tab3:
    st.subheader("🔖 Your Bookmarks")
    bookmarks = load_bookmarks()
    if bookmarks:
        for b in bookmarks:
            st.markdown(f"### [{b['title']}]({b['url']})")
            st.write("---")
    else:
        st.info("No bookmarks yet.")
