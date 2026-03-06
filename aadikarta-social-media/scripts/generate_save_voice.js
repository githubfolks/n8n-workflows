const fs = require('fs');
const englishSign = $node["Extract Content"].json.english_sign || 'unknown';
const filePath = `/root/.n8n-files/${englishSign}.mp4`;

// Ensure directory exists
if (!fs.existsSync('/root/.n8n-files/')) {
    fs.mkdirSync('/root/.n8n-files/', { recursive: true });
}

fs.copyFileSync('/data/n8n-work/dummy.mp4', filePath);

return [{
    json: {
        ...$json,
        saved_file: filePath,
        dummy_mode: true
    }
}];