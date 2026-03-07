import json
import os

input_path = "workflows/horoscopes_workflow.json"
output_path = "workflows/story_to_video_workflow.json"

with open(input_path, "r") as f:
    orig = json.load(f)

# Nodes we want to keep exactly as is
keep_nodes = [
    "Initialize Reel", "Upload Reel", "Publish Reel", "Facebook Response Check",
    "Initialize IG Reel", "Upload IG Reel", "Publish IG Reel", "Instagram Response Check",
    "Read Video File"
]

new_nodes = []

# 1. Add Webhook Trigger
new_nodes.append({
    "parameters": {
        "httpMethod": "POST",
        "path": "generate-video",
        "responseMode": "onReceived",
        "options": {}
    },
    "name": "Webhook",
    "type": "n8n-nodes-base.webhook",
    "typeVersion": 1,
    "position": [200, 400],
    "webhookId": "generate-video-story-webhook"
})

# 2. Add Extract Content node to map webhook shape to expected shape
extract_code = """
const fs = require('fs');
const filePath = '/root/.n8n-files/story_video.mp4';

// For now, testing with dummy video
if (!fs.existsSync('/root/.n8n-files/')){
    fs.mkdirSync('/root/.n8n-files/', { recursive: true });
}
if (!fs.existsSync(filePath)) {
    try {
        fs.copyFileSync('/data/n8n-work/dummy.mp4', filePath);
    } catch (e) {
        console.log('Dummy video not found, continuing anyway.');
    }
}

return [{
  json: {
    content: $json.body.story,
    scenes: $json.body.scenes,
    english_sign: 'story_video',
    saved_file: filePath,
    dummy_mode: true
  }
}];
"""

new_nodes.append({
    "parameters": {
        "jsCode": extract_code
    },
    "name": "Extract Content",
    "type": "n8n-nodes-base.code",
    "typeVersion": 2,
    "position": [400, 400]
})

# Add logic nodes from horoscope workflow
for n in orig.get("nodes", []):
    if n["name"] in keep_nodes:
        new_nodes.append(n)

# Build connections
# Webhook -> Extract Content -> Read Video File -> FB & IG
connections = {
    "Webhook": {
        "main": [
            [{"node": "Extract Content", "type": "main", "index": 0}]
        ]
    },
    "Extract Content": {
        "main": [
            [{"node": "Read Video File", "type": "main", "index": 0}]
        ]
    }
}

# Preserve FB/IG upload connections
for src, targets in orig.get("connections", {}).items():
    if src in keep_nodes:
        # filter targets to only keep_nodes
        filtered_targets = []
        for tg_list in targets.get("main", []):
            new_tg_list = []
            for t in tg_list:
                if t["node"] in keep_nodes:
                    new_tg_list.append(t)
            filtered_targets.append(new_tg_list)
        if any(filtered_targets):
            connections[src] = {"main": filtered_targets}

# Add Read Video File mapping
connections["Read Video File"] = {
    "main": [
        [
            {"node": "Initialize Reel", "type": "main", "index": 0},
            {"node": "Initialize IG Reel", "type": "main", "index": 0}
        ]
    ]
}

new_workflow = {
    "name": "Story to Video (Webhook)",
    "nodes": new_nodes,
    "connections": connections
}

with open(output_path, "w") as f:
    json.dump(new_workflow, f, indent=2)

print(f"Successfully generated {output_path}")
