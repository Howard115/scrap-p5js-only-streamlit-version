import streamlit as st
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains
import os
import time
import shutil
import zipfile
import random
from streamlit.components.v1 import html


def initialize_driver():
    chrome_options = Options()
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--start-maximized")
    chrome_options.add_argument(
        "--headless")  # Run in headless mode for Streamlit

    service = Service(ChromeDriverManager().install())

    driver = webdriver.Chrome(service=service, options=chrome_options)
    action_chains = ActionChains(driver)

    return driver, action_chains


def sign_in(driver, action_chains):
    for _ in range(7):
        action_chains.send_keys(Keys.TAB).perform()
    action_chains.send_keys(Keys.ENTER).perform()
    sign_in_link = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, 'a[href="/signin"]')))
    sign_in_link.click()
    time.sleep(1)
    action_chains.send_keys("anxgzmcrnld@gmail.com").perform()
    action_chains.send_keys(Keys.TAB).perform()
    action_chains.send_keys("0000000000").perform()
    for _ in range(3):
        action_chains.send_keys(Keys.TAB).perform()
    action_chains.send_keys(Keys.ENTER).perform()
    time.sleep(3)


def download_random_sketch(driver, action_chains):
    sketch_elements = WebDriverWait(driver, 10).until(
        EC.presence_of_all_elements_located(
            (By.CSS_SELECTOR, "li.sketchLi.col-xs-4.col-sm-3.col-lg-2")))

    if sketch_elements:
        random_sketch = random.choice(sketch_elements)
        random_sketch.click()
    else:
        st.error("No sketch elements found")
        return

    share_button = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable(
            (By.CSS_SELECTOR, "div.icon.icon_share.white")))
    share_button.click()

    download_link = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, 'a#downloadLink')))
    download_link.click()

    wait_for_download()


def wait_for_download():
    download_dir = os.path.expanduser("~/Downloads")
    timeout = 60
    interval = 1

    start_time = time.time()
    while time.time() - start_time < timeout:
        zip_files = [f for f in os.listdir(download_dir) if f.endswith('.zip')]
        if zip_files:
            latest_zip = max(
                [os.path.join(download_dir, f) for f in zip_files],
                key=os.path.getmtime)
            if "sketch" in os.path.basename(latest_zip).lower():
                time.sleep(2)
                return
        time.sleep(interval)

    raise TimeoutError(
        "Download timeout: No sketch zip file found within the specified time."
    )


def process_downloaded_zip():
    download_folder = os.path.join(os.path.dirname(__file__), "downloadFOLDER")
    if os.path.exists(download_folder):
        for item in os.listdir(download_folder):
            item_path = os.path.join(download_folder, item)
            if os.path.isdir(item_path):
                shutil.rmtree(item_path)
                st.write(f"Removed folder: {item_path}")

    download_dir = os.path.expanduser("~/Downloads")

    zip_files = [f for f in os.listdir(download_dir) if f.endswith('.zip')]
    if zip_files:
        latest_zip = max([os.path.join(download_dir, f) for f in zip_files],
                         key=os.path.getmtime)
        if "sketch" not in os.path.basename(latest_zip).lower():
            raise ValueError("Can't find sketchzip")

        sketch_folder_name = os.path.splitext(os.path.basename(latest_zip))[0]
        sketch_id = sketch_folder_name.split('sketch')[-1]

        download_zip_dir = os.path.join(os.path.dirname(__file__),
                                        "downloadZIP")
        os.makedirs(download_zip_dir, exist_ok=True)

        destination = os.path.join(download_zip_dir,
                                   os.path.basename(latest_zip))
        shutil.move(latest_zip, destination)
        st.write(f"Moved {latest_zip} to {destination}")

        download_folder = os.path.join(os.path.dirname(__file__),
                                       "downloadFOLDER")
        os.makedirs(download_folder, exist_ok=True)

        sketch_folder = os.path.join(download_folder, 'sketch')
        os.makedirs(sketch_folder, exist_ok=True)

        with zipfile.ZipFile(destination, 'r') as zip_ref:
            zip_ref.extractall(sketch_folder)

        st.write(
            f"Extracted contents of {os.path.basename(destination)} to {sketch_folder}"
        )

        os.remove(destination)
        st.write(f"Removed original zip file: {destination}")

        return sketch_id
    else:
        st.error("No zip file found in the download directory")
        return None


def read_sketch_files(sketch_folder):
    js_content = ""
    css_content = ""
    for file in os.listdir(sketch_folder):
        file_path = os.path.join(sketch_folder, file)
        if file.endswith('.js'):
            with open(file_path, 'r') as f:
                js_content += f.read() + "\n"
        elif file.endswith('.css'):
            with open(file_path, 'r') as f:
                css_content += f.read() + "\n"
    return js_content, css_content


def main():
    st.title("OpenProcessing Sketch Downloader")

    if st.button("Download Random Sketch"):
        driver, action_chains = initialize_driver()

        try:
            driver.get("https://openprocessing.org/discover/#/trending")
            sign_in(driver, action_chains)
            driver.get("https://openprocessing.org/discover/#/trending")
            download_random_sketch(driver, action_chains)
            sketch_id = process_downloaded_zip()
            if sketch_id:
                st.success(f"Processed sketch: {sketch_id}")
            else:
                st.error("Failed to process sketch")
        except Exception as e:
            st.error(f"An error occurred: {str(e)}")
        finally:
            driver.quit()

    # Add a button to show the p5.js sketch
    if st.button("Show Downloaded Sketch"):
        sketch_folder = os.path.join(os.path.dirname(__file__),
                                     "downloadFOLDER", "sketch")
        if os.path.exists(sketch_folder):
            js_content, css_content = read_sketch_files(sketch_folder)

            # Create a new HTML structure with inline JavaScript and CSS
            p5js_html = f"""
            <!DOCTYPE html>
            <html lang="en">
            <head>
                <script src="https://cdn.jsdelivr.net/npm/p5@1.11.0/lib/p5.js"></script>
                <script src="https://openprocessing.org/openprocessing_sketch.js"></script>
                <script src="https://cdn.jsdelivr.net/npm/p5@1.9.2/lib/addons/p5.sound.min.js"></script>
                <style>
                {css_content}
                </style>
                <script>
                {js_content}
                </script>
            </head>
            <body>
            </body>
            </html>
            """

            # Display the p5.js sketch
            st.components.v1.html(p5js_html, height=600)
        else:
            st.error("No sketch found. Please download a sketch first.")

    # Add custom CSS to ensure the canvas fits within the Streamlit component
    st.markdown("""
    <style>
        iframe {
            width: 100%;
            height: 480px;
            position: fixed;
            top: 65%;
            left: 50%;
            transform: translate(-50%, -50%);
        }
        canvas {
            max-width: 10%;
            max-height: 10%;
        }
    </style>
    """,
                unsafe_allow_html=True)


if __name__ == "__main__":
    main()
