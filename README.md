# OpenProcessing Sketch Downloader

This Streamlit application allows users to download and display random sketches from OpenProcessing.org. It uses Selenium for web scraping and p5.js for rendering the sketches.

## Features

1. **Download Random Sketch**: With a single click, the app downloads a random sketch from OpenProcessing's trending page.
2. **Display Downloaded Sketch**: Users can view the downloaded sketch directly in the Streamlit interface.

## How it works

1. The app uses Selenium WebDriver to navigate OpenProcessing.org.
2. It logs in to an OpenProcessing account (credentials are hardcoded for demonstration purposes).
3. A random sketch is selected from the trending page and downloaded.
4. The downloaded sketch is extracted and processed.
5. Users can then display the sketch using p5.js within the Streamlit app.

## Requirements

- Python 3.7+
- Streamlit
- Selenium
- Chrome WebDriver

## Setup

1. Install the required packages:
   ```
   pip install -r requirements.txt
   ```
2. Ensure you have Chrome and ChromeDriver installed.
3. Run the Streamlit app:
   ```
   streamlit run app.py
   ```

## Note

This app is for educational purposes only. Please respect OpenProcessing's terms of service and the copyrights of sketch creators when using this tool.
