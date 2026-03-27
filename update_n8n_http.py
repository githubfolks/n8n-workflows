import json

with open('workflows/story_to_video_workflow.json', 'r') as f:
    data = json.load(f)

# The new HTTP Request node to send the MP4 back to FastAPI
callback_node = {
  "parameters": {
    "method": "POST",
    "url": "http://app:8003/api/v1/story/webhook/n8n/video-completed",
    "sendBody": True,
    "specifyBody": "keypair",
    "bodyParameters": {
      "parameters": [
        {
          "name": "project_id",
          "value": "={{ $node[\"Webhook\"].json.body.project_id }}"
        }
      ]
    },
    "options": {
      "bodyContentType": "multipart-form-data",
      "sendBinaryData": True,
      "binaryPropertyName": "video_file:data"
    }
  },
  "name": "Save Video to Backend",
  "type": "n8n-nodes-base.httpRequest",
  "typeVersion": 4,
  "position": [
    2800,
    400
  ]
}

data['nodes'].append(callback_node)

# Connect Facebook and IG success outputs to this new node
data['connections']['Facebook Response Check'] = {
  "main": [
    [
      {
        "node": "Save Video to Backend",
        "type": "main"
      }
    ]
  ]
}

data['connections']['Instagram Response Check'] = {
  "main": [
    [
      {
        "node": "Save Video to Backend",
        "type": "main",
        "index": 0
      }
    ]
  ]
}

with open('workflows/story_to_video_workflow.json', 'w') as f:
    json.dump(data, f, indent=2)

print("n8n Webhook Node injected.")
