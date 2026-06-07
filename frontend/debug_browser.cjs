const puppeteer = require('puppeteer');

(async () => {
  const browser = await puppeteer.launch();
  const page = await browser.newPage();
  
  page.on('console', msg => {
    if (msg.type() === 'error') console.log('PAGE ERROR:', msg.text());
  });
  page.on('pageerror', error => console.log('UNCAUGHT EXCEPTION:', error.message));

  console.log('Testing /');
  await page.goto(`http://localhost:5173/`, { waitUntil: 'networkidle2' });
  const html = await page.content();
  console.log('HTML Length:', html.length);
  const rootContent = await page.$eval('#root', el => el.innerHTML).catch(e => e.message);
  console.log('Root content length:', rootContent.length);
  if (rootContent.length < 100) {
      console.log('Root content:', rootContent);
  }
  
  await browser.close();
})();
