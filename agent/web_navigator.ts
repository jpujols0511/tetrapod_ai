// const puppeteer = require('puppeteer-extra');


import puppeteer from "puppeteer-extra";
import StealthPlugin from 'puppeteer-extra-plugin-stealth'
import fs from "fs";
puppeteer.use(StealthPlugin());

// const url = process.argv[2];
const timeout = 15000;

(async () => {


    const browser = await puppeteer.launch({
        headless: false,
        executablePath: '/Applications/Brave\ Browser\ Nightly.app/Contents/MacOS/Brave\ Browser\ Nightly',
        userDataDir: '/Users/joanpujols/Library/Application\ Support/BraveSoftware/Brave-Browser-Nightly/Default',
    });
    
    //close all browser tabs & resolve promise when done
    const pages = await browser.pages();
    await Promise.all(pages.map(async page => await page.close()));

    const page = await browser.newPage();


    // Load cookies
    await loadCookies(page);

    await page.setViewport({
        width: 1200,
        height: 1200,
        deviceScaleFactor: 1,
    });

    await page.goto('https://www.stake.com', {
        waitUntil: "domcontentloaded",
        timeout: timeout,
    });

    // Wait 5 seconds
    new Promise(r => setTimeout(r, timeout));

    console.log("Network Requests ", + await page.evaluate(() => window.performance.getEntriesByType("resource").length));

    // Save cookies
    await saveCookies(page);

    await page.screenshot({
        path: "screenshot.jpg",
        fullPage: true,
    });

    await browser.close();
})();


async function saveCookies(page) {
    const cookies = await page?.cookies();
    await fs.writeFile('./cookies.json', JSON.stringify(cookies, null, 2), (err) => {
        if (err)
            console.log(err);
        else {
            console.log("File written successfully\n");
            console.log("The written has the following contents:");

        }
    });
}

async function loadCookies(page) {
    try {
        // Reading cookies from the specified file
        const cookiesJson = fs.readFileSync('./cookies.json', 'utf-8');
        const cookies = JSON.parse(cookiesJson);

        // Setting the cookies in the current page

        cookies.forEach(async (cookie) => {
            await page?.setCookie(cookie);
        });
        // Cookies have been loaded successfully
        return true;
    } catch (error) {
        // An error occurred while loading cookies
        console.error('Error loading cookies:', error);
        return false;
    }

}