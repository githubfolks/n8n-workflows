# Text-to-Video Quality Testing Script

This directory contains a script to test the complete text-to-video pipeline by chaining the Image Generation API and Video Generation API endpoints.

## Requirements

Ensure you have the required dependencies installed. We recommend using a virtual environment:

```bash
python3 -m venv venv
source venv/bin/activate
pip install httpx
```

## Usage

Since the backend API endpoints require authentication, first generate a test token using the included helper script:

```bash
source venv/bin/activate
python3 generate_token.py --base-url "http://localhost:8003"
```

Once you have the token, you can run the test pipeline and generate a video from your text prompt. Run the script from the command line:

```bash
python3 test_text_to_video.py --prompt "A futuristic city skyline at neon sunset, cinematic, 4k" --base-url "http://localhost:8003" --token "<YOUR_TOKEN_HERE>"
```

### Options for `test_text_to_video.py`

*   `--prompt`: (Required) The text prompt to describe the scene you want to generate.
*   `--base-url`: (Optional) The base URL of your API server. Defaults to `http://localhost:8000`.
*   `--token`: (Optional) The Bearer token if backend authentication is required.
*   `--output-dir`: (Optional) The directory to save the output files (`generated_image.png` and `generated_video.mp4`). Defaults to locally created `results/` folder.

## What It Does

1. **Step 1:** Sends your text to `POST /api/v1/generate/image` and saves the resulting image to disk.
2. **Step 2:** Takes the generated image and sends it via form-data to `POST /api/v1/generate/video`.
3. **Step 3:** Saves the resulting generated video binary stream to your disk as an `mp4` file so you can inspect its quality.
