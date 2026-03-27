const fs = require('fs');
const workflowPath = 'n8n_workflow.json';
const workflow = JSON.parse(fs.readFileSync(workflowPath, 'utf8'));

// 1. Create the Initialize IG Reel node
const initializeIgReelNode = {
  "parameters": {
    "url": "={{\"https://graph.facebook.com/v18.0/\" + $env.INSTAGRAM_ACCOUNT_ID + \"/media?access_token=\" + $env.FACEBOOK_PAGE_ACCESS_TOKEN.trim()}}",
    "method": "POST",
    "sendBody": true,
    "sendQuery": false,
    "specifyBody": "json",
    "jsonParameters": true,
    "bodyParametersJson": "={ \"media_type\": \"REELS\", \"upload_type\": \"resumable\", \"caption\": {{ JSON.stringify($node[\"Extract Content\"].json.content) }} }",
    "headerParametersUi": {
      "parameter": [
        {
          "name": "Content-Type",
          "value": "application/json"
        }
      ]
    }
  },
  "name": "Initialize IG Reel",
  "type": "n8n-nodes-base.httpRequest",
  "typeVersion": 4,
  "position": [
    2000,
    500
  ]
};

// 2. Create the Upload IG Reel node
const uploadIgReelNode = {
  "parameters": {
    "jsCode": "\nconst https = require('https');\nconst fs = require('fs');\n\nconst uploadUrl = $('Initialize IG Reel').first().json.uri;\n\n// In a native JS Code node, environment variables are accessed via process.env\nconst accessToken = (process.env.FACEBOOK_PAGE_ACCESS_TOKEN || '').trim();\nif (!accessToken) {\n  throw new Error(\"Missing FACEBOOK_PAGE_ACCESS_TOKEN in environment!\");\n}\n\n// The file name and path from Read Video File\nconst filePath = $('Read Video File').first().json.saved_file || '/root/.n8n-files/dummy.mp4';\n\nif (!fs.existsSync(filePath)) {\n  throw new Error(\"Video file not found! \" + filePath);\n}\n\nconst fileData = fs.readFileSync(filePath);\nconst parsedUrl = new URL(uploadUrl);\n\nconst options = {\n  hostname: parsedUrl.hostname,\n  path: parsedUrl.pathname + parsedUrl.search,\n  method: 'POST',\n  headers: {\n    'Authorization': `OAuth ${accessToken}`,\n    'offset': '0',\n    'file_size': fileData.length.toString(),\n    'Content-Length': fileData.length.toString()\n  }\n};\n\nreturn new Promise((resolve, reject) => {\n  const req = https.request(options, (res) => {\n    let responseData = '';\n    res.on('data', (chunk) => responseData += chunk);\n    res.on('end', () => {\n      try {\n        resolve([{ json: JSON.parse(responseData || '{}'), status: res.statusCode }]);\n      } catch (e) {\n        resolve([{ json: { raw: responseData }, status: res.statusCode }]);\n      }\n    });\n  });\n\n  req.on('error', (e) => reject(e));\n  req.write(fileData);\n  req.end();\n});\n"
  },
  "name": "Upload IG Reel",
  "type": "n8n-nodes-base.code",
  "typeVersion": 2,
  "position": [
    2200,
    500
  ]
};

// 3. Create Publish IG Reel node
const publishIgReelNode = {
  "parameters": {
    "url": "={{\"https://graph.facebook.com/v18.0/\" + $env.INSTAGRAM_ACCOUNT_ID + \"/media_publish?access_token=\" + $env.FACEBOOK_PAGE_ACCESS_TOKEN.trim()}}",
    "method": "POST",
    "sendBody": true,
    "sendQuery": false,
    "specifyBody": "json",
    "jsonParameters": true,
    "bodyParametersJson": "={ \"creation_id\": \"{{ $node[\\\"Initialize IG Reel\\\"].json.id }}\" }",
    "headerParametersUi": {
      "parameter": [
        {
          "name": "Content-Type",
          "value": "application/json"
        }
      ]
    }
  },
  "name": "Publish IG Reel",
  "type": "n8n-nodes-base.httpRequest",
  "typeVersion": 4,
  "position": [
    2400,
    500
  ]
};

// 4. Create Instagram Response Check node
const igResponseCheckNode = {
  "parameters": {
    "jsCode": "if ($json.error) {\n  throw new Error(`INSTAGRAM API ERROR: ${$json.error.message} (Type: ${$json.error.type})`);\n}\nif (!$json.id) {\n  throw new Error(`INSTAGRAM PUBLISH FAILED: Failed to get published media ID. Response: ${JSON.stringify($json)}`);\n}\nreturn [{\n  json: {\n    instagram_success: true,\n    ig_media_id: $json.id,\n    raw_response: $json\n  }\n}];"
  },
  "name": "Instagram Response Check",
  "type": "n8n-nodes-base.code",
  "typeVersion": 2,
  "position": [
    2600,
    500
  ]
};


workflow.nodes.push(initializeIgReelNode, uploadIgReelNode, publishIgReelNode, igResponseCheckNode);

// Update connections for Instagram branch (parallel to Facebook)
if (!workflow.connections['Read Video File']) {
	workflow.connections['Read Video File'] = { main: [ [] ]};
}
// Add to the main output array (array element 0 is the output 1 of the Read Video Node connecting to multiple input nodes)
workflow.connections['Read Video File'].main[0].push({
  "node": "Initialize IG Reel",
  "type": "main",
  "index": 0
});

workflow.connections['Initialize IG Reel'] = {
  "main": [
    [
      {
        "node": "Upload IG Reel",
        "type": "main",
        "index": 0
      }
    ]
  ]
};

workflow.connections['Upload IG Reel'] = {
  "main": [
    [
      {
        "node": "Publish IG Reel",
        "type": "main",
        "index": 0
      }
    ]
  ]
};

workflow.connections['Publish IG Reel'] = {
  "main": [
    [
      {
        "node": "Instagram Response Check",
        "type": "main",
        "index": 0
      }
    ]
  ]
};

fs.writeFileSync(workflowPath, JSON.stringify(workflow, null, 2), 'utf8');
console.log('Successfully updated n8n_workflow.json with Instagram Reels nodes');

