# How to Post Horoscopic Content with my_n8n
The my_n8n stack is a powerful AI-driven automation system that can generate and post horoscopic content (text, images, and videos) automatically.

# Workflow Overview
The system follows a 4-step process orchestrated by n8n:

# Content Generation: 
The backend uses OpenAI to generate a horoscope caption, hashtags, and a visual description (image prompt) based on your selected zodiac sign.
# Image Generation: 
The backend calls the Image Service, which uses Stable Diffusion to create a stunning high-quality visual for the horoscope.
# Video Generation (Optional): 
The Video Service can combine images and text into a short video clip (Reel/Short style) using FFmpeg.
# Social Posting: 
The generated media is uploaded to MinIO storage and then posted to Facebook, Instagram, or X (Twitter) using n8n nodes.
Detailed Instructions

# 1. Access the Orchestrator
Go to http://localhost:5678 to access your n8n dashboard.
kumavikram@gmail.com
8cSV!DsTbqWYU4q

# 2. Configure the Workflow
If you haven't imported the workflow yet:

Click Workflows > Import from File.
Select the 
n8n_workflow.json
 file from your project root.
In the Generate Content node, set the topic parameter to your desired horoscope (e.g., "Daily Horoscope for Aries").
Set the tone to "astrological" or "mystical".

# 3. Setup Credentials
In n8n, go to Credentials.
Add your credentials for Facebook, Instagram, and Twitter.
You will also need a Header Auth credential for the backend (it expects the secret key configured in your 
.env
).
4. Trigger the Posting
Manual: Click Execute Workflow in n8n for an immediate post.
Scheduled: The workflow is currently set to run every day at 9:00 AM. You can adjust the Cron Trigger node to change this.
# Assets Check
You can view all generated images and videos at http://localhost:9001 (MinIO Console).

TIP

To automate for all 12 zodiac signs, you can add a Loop node in n8n that iterates through a list of signs and calls the "Generate Content" node for each.

==========================
# Generate Horoscope

{
  "model": "gpt-4o-mini",
  "messages": [
    {
      "role": "user",
      "content": "आज की तारीख: {{$now}}\nराशि: {{$json.signs}}\n150 शब्दों में वैदिक राशिफल लिखें। करियर, प्रेम, स्वास्थ्य, उपाय, शुभ रंग, शुभ अंक शामिल करें।"
    }
  ]
}

# Generate Voice:
elevenlabs-header-auth

https://api.elevenlabs.io/v1/text-to-speech/pqHfZKP75CvOlQylNhV4

{
  "text": "{{$json.horoscope}}",
  "model_id": "eleven_multilingual_v2",
  "voice_settings": {
    "stability": 0.4,
    "similarity_boost": 0.8
  }
}

# Save to PostgreSQL
Open the "Save to PostgreSQL" node.
Look for the Columns setting.
Change it from "Auto-Map Input Data" to "Define Below" (or "Map Manually").
Under the Mapping section that appears, click "Add Assignment" twice.
Setup the mapping like this:
Column sign = ={{ $json.sign }}
Column content = ={{ $json.content }}

# Initialize Reel
Open the "Initialize Reel" node.
Scroll to the bottom and click Add Header.
Name: Content-Type
Value: application/json
Ensure Send Body is set to true, Specify Body to JSON, and JSON Parameters is true (if visible) or just paste { "upload_phase": "start" } into the Body input.
 
[https://developers.facebook.com/tools/explorer/]

# Upload Reel

offset: 0
file_size: {{$binary.data.fileSize || $binary.data.data.length}}
Content-Length: {{$binary.data.fileSize || $binary.data.data.length}}
accept: application/json

# Publish Reel
Name: upload_phase | Value: finish
Name: video_id | Value (Expression): ={{ $('Initialize Reel').first().json.video_id }}
Name: video_state | Value: PUBLISHED
Name: description | Value (Expression): ={{ $('Extract Content').first().json.content }}