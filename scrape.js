const fs = require('fs');
const puppeteer = require('puppeteer');
const https = require('https');

const BOT_TOKEN = '8178015065:AAGe_FPh7RWxPjZCYTu-DW-JCs-i8HdNesk';
const CHAT_ID = '7148139336';

(async () => {
  const browser = await puppeteer.launch({ headless: 'new' });
  const page = await browser.newPage();
  await page.goto('https://exesimulation.created.app/', { waitUntil: 'networkidle2' });

  await page.evaluate(() => {
    const btn = document.querySelector('a[href="https://created.app/"]');
    if (btn) btn.remove();
  });

  const html = await page.content();
  fs.writeFileSync('final.html', html);
  console.log('Saved as final.html');

  // Send to Telegram
  const boundary = 'xXx';
  const data = [
    `--${boundary}`,
    `Content-Disposition: form-data; name="chat_id"`,
    '',
    CHAT_ID,
    `--${boundary}`,
    `Content-Disposition: form-data; name="document"; filename="final.html"`,
    'Content-Type: text/html',
    '',
    html,
    `--${boundary}--`
  ].join('\r\n');

  const req = https.request({
    hostname: 'api.telegram.org',
    path: `/bot${BOT_TOKEN}/sendDocument`,
    method: 'POST',
    headers: {
      'Content-Type': `multipart/form-data; boundary=${boundary}`,
      'Content-Length': Buffer.byteLength(data)
    }
  });

  req.write(data);
  req.end();

  req.on('response', res => {
    console.log(`Sent to Telegram: ${res.statusCode}`);
  });

  await browser.close();
})();
