import streamlit as st
from langchain_community.document_loaders import WebBaseLoader

from chain import Chain
from portfolio import Portfolio
from utils import clean_text
from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import time

import os

load_dotenv()
os.getenv('GROK_API_KEY')

def get_page_content_with_js(url):
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--log-level=3")

    # Auto-manage ChromeDriver
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)

    try:
        driver.get(url)
        time.sleep(5)
        html = driver.page_source
    finally:
        driver.quit()

    return html


def create_streamlit_app(llm, portfolio, clean_text):
    st.title("📧 Cold Mail Generator")
    url_input = st.text_input("Enter a URL:")    
    submit_button = st.button("Submit")

    if submit_button and url_input:
        try:
            headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/115.0.0.0 Safari/537.36"}
            loader = WebBaseLoader([url_input], header_template=headers)
            html = get_page_content_with_js(url_input)
            data = clean_text(html)
            portfolio.load_portfolio()
            jobs = llm.extract_jobs(data)
            for job in jobs:
                if not job or not isinstance(job, dict):
                    continue
                skills = job.get('skills', [])
                links = portfolio.query_links(skills)
                email = llm.write_mail(job, links)
                st.code(email, language='markdown')


        except Exception as e:
            st.error(f"An Error Occurred: {e}")


if __name__ == "__main__":
    chain = Chain()
    portfolio = Portfolio()
    st.set_page_config(layout="wide", page_title="Cold Email Generator", page_icon="📧")
    create_streamlit_app(chain, portfolio, clean_text)