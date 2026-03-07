
# Access the Orchestrator
Go to http://localhost:5678 to access your n8n dashboard.
kumavikram@gmail.com
8cSV!DsTbqWYU4q

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
Column sign: ={{ $json.sign }}
Column content: ={{ $json.content }}

# Initialize Reel
Open the "Initialize Reel" node.
Scroll to the bottom and click Add Header.
Name: Content-Type
Value: application/json
Body to JSON: { "upload_phase": "start" }

[https://developers.facebook.com/tools/explorer/]

# Upload Reel

offset: 0
file_size: {{$binary.data.fileSize || $binary.data.data.length}}
Content-Length: {{$binary.data.fileSize || $binary.data.data.length}}
accept: application/json

# Publish Reel
upload_phase: finish
video_id: ={{ $('Initialize Reel').first().json.video_id }}
video_state: PUBLISHED
description: ={{ $('Extract Content').first().json.content }}

# Upload IG Reel
{
  "upload_type":"resumable",
  "media_type":"REELS"
}

# Publish IG Reel
creation_id: {{ $node["Initialize IG Reel"].json.id }}
