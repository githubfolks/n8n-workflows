const https = require('https');

const videoId = $node["Initialize Reel"].json.video_id;
const description = $node["Extract Content"].json.content;
const pageId = $node["Global Config"].json.fb_page_id;

// Securely access Token globally via Docker Env Mapping
const accessToken = $node["Global Config"].json.fb_token;


const payload = JSON.stringify({
    upload_phase: 'finish',
    video_id: videoId,
    video_state: 'PUBLISHED',
    description: description,
    access_token: accessToken    // THIS WAS THE MISSING KEY CAUSING THE NULL CRASH!
});

const options = {
    hostname: 'graph.facebook.com',
    path: `/v18.0/${pageId}/video_reels`, // Clean URL, no query string
    method: 'POST',
    headers: {
        'Content-Type': 'application/json',
        'Content-Length': Buffer.byteLength(payload)
    }
};

return await new Promise((resolve, reject) => {
    const req = https.request(options, (res) => {
        let responseData = '';
        res.on('data', chunk => responseData += chunk);
        res.on('end', () => resolve([{ json: { body: JSON.parse(responseData || '{}'), status: res.statusCode } }]));
    });
    req.on('error', e => resolve([{ json: { execute_error: e.message } }]));
    req.write(payload);
    req.end();
});
