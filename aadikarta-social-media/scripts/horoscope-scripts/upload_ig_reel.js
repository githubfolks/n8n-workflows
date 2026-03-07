
const https = require('https');
const fs = require('fs');

const uploadUrl = $('Initialize IG Reel').first().json.uri;

// In a native JS Code node, environment variables are accessed via process.env
const accessToken = ($env.FACEBOOK_PAGE_ACCESS_TOKEN || '').trim();
if (!accessToken) {
    throw new Error("Missing FACEBOOK_PAGE_ACCESS_TOKEN in environment!");
}

// Get the specific English sign name for the file, fallback to dummy.mp4
const englishSign = $('Extract Content').first().json.english_sign;
const filePath = englishSign ? `/root/.n8n-files/${englishSign}.mp4` : '/root/.n8n-files/dummy.mp4';

if (!fs.existsSync(filePath)) {
    throw new Error("Video file not found! " + filePath);
}

const fileData = fs.readFileSync(filePath);
const parsedUrl = new URL(uploadUrl);

const options = {
    hostname: parsedUrl.hostname,
    path: parsedUrl.pathname + parsedUrl.search,
    method: 'POST',
    headers: {
        'Authorization': `OAuth ${accessToken}`,
        'offset': '0',
        'file_size': fileData.length.toString(),
        'Content-Length': fileData.length.toString()
    }
};

return new Promise((resolve, reject) => {
    const req = https.request(options, (res) => {
        let responseData = '';
        res.on('data', (chunk) => responseData += chunk);
        res.on('end', () => {
            try {
                resolve([{ json: JSON.parse(responseData || '{}'), status: res.statusCode }]);
            } catch (e) {
                resolve([{ json: { raw: responseData }, status: res.statusCode }]);
            }
        });
    });

    req.on('error', (e) => reject(e));
    req.write(fileData);
    req.end();
});
