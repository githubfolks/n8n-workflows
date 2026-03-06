try {
    const https = require('https');
    const fs = require('fs');
    const uploadUrl = $input.first().json.upload_url;

    // Secure Access Token via Memory
    const accessToken = $node["Global Config"].json.fb_token;

    // Identify the dynamic video file name
    const englishSign = $('Extract Content').first().json.english_sign;
    const filePath = "/root/.n8n-files/" + englishSign + ".mp4";

    if (!fs.existsSync(filePath)) {
        throw new Error("Could not find video at: " + filePath);
    }

    // Natively read the binary bytes from disk
    const binaryBuffer = fs.readFileSync(filePath);

    // Manually split the URL into Hostname and Path to bypass the missing URL class
    const urlWithoutProtocol = uploadUrl.substring(8);
    const firstSlashIndex = urlWithoutProtocol.indexOf('/');
    const hostname = urlWithoutProtocol.substring(0, firstSlashIndex);
    const path = urlWithoutProtocol.substring(firstSlashIndex);

    const options = {
        hostname: hostname,
        path: path,
        method: 'POST',
        headers: {
            'Authorization': `OAuth ${accessToken}`,
            'offset': '0',
            'file_size': binaryBuffer.length.toString(),
            'Content-Length': binaryBuffer.length.toString(),
            // THIS is the secret header that Facebook's server requires to parse the payload properly!
            'Content-Type': 'application/x-www-form-urlencoded',
            'Connection': 'keep-alive',
            'Accept': '*/* '
        }
    };

    return await new Promise((resolve, reject) => {
        const req = https.request(options, (res) => {
            let responseData = '';
            res.on('data', (chunk) => responseData += chunk);
            res.on('end', () => resolve([{ json: { body: responseData, status: res.statusCode } }]));
        });

        req.on('error', (e) => resolve([{ json: { execute_error: e.message } }]));
        req.write(binaryBuffer);
        req.end();
    });

} catch (masterError) {
    return [{ json: { CRASH: masterError.message, stack: masterError.stack } }];
}
