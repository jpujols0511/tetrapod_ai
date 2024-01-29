import puppeteer from "puppeteer-extra";
import StealthPlugin from 'puppeteer-extra-plugin-stealth'
import fs from "fs";
import WebSocket from 'ws';

puppeteer.use(StealthPlugin());

const timeout = 5000;

const socket = new WebSocket('ws://localhost:8080');

const defaultGameState = [
    0, 0, 0, 0, 0,
    0, 0, 0, 0, 0,
    0, 0, 0, 0, 0,
    0, 0, 0, 0, 0,
    0, 0, 0, 0, 0
];

(async () => {
    const config = {
        type: "new_game",
        reward: null,
        game: "mines",
        games: 10,
        game_number: 0,
        bet: 0,
        betActive: false,
        multiplier: 0,
        over: true,
        cashout: false,
        nonce: 0,
        gems: 0,
        mines: 0,
        seed: 42,
        client_seed: "8749b355efa78e22",
        playing: false,
        playing_auto: false,
        balance: 0,
        move: null,
        state: defaultGameState,
        wins: 0,
        looses: 0
    }


    // Launch browser
    const browser = await puppeteer.launch({
        headless: false,
        executablePath: '/Applications/Brave\ Browser\ Nightly.app/Contents/MacOS/Brave\ Browser\ Nightly',
        userDataDir: '/Users/joanpujols/Library/Application\ Support/BraveSoftware/Brave-Browser-Nightly/Default',
    });

    // Create new tab
    const page = await browser.newPage();

    // Get all tabs
    const pages = await browser.pages();

    // Load cookies
    await loadCookies(page);

    await page.setViewport({
        width: 1200,
        height: 1200,
        deviceScaleFactor: 1,
    });
    

    await page.goto('https://stake.com/casino/games/mines', {
        waitUntil: "domcontentloaded",
        timeout: timeout,
    });
   
    // Close empty tab after loading the page
    await pages[0].close();

    async function getGameState() {
        
        const gameState = await page.$$eval('.game-content > div:nth-child(1) > button', (el) => {
            const allElems = el.map((e) => {

                const num = e?.getAttribute('class')?.includes('idle') ? 0 : e.getAttribute('class').includes('mine') ? -1 : e.getAttribute('class').includes('gem') ? 1 : 0
                console.log(`getting state for ` + e?.getAttribute('class'))
                return num;
            })
            return allElems
        })
        return gameState;
    }

    async function cashout() {
        return await page.click('.game-sidebar > *:nth-child(6)' , { delay: 1000 })

    }

    async function processMessage(data) {
        
        // Start game
        if (data.playing === true && data.over === true && data.game_number < data.games) {
           
            console.log('playing game....')
            // Click on bet
            await new Promise(r => setTimeout(r, 1500))
            await page.click('.game-sidebar > *:nth-child(4)', { delay: 2000, count: 3 })
            await new Promise(r => setTimeout(r, 2000))

            data.state = [...defaultGameState];

            data.game_number += 1;

            data.over = false;

            console.log('data before sending ' + JSON.stringify(data))

            await socket.send(JSON.stringify(data));

        }
        
        // Game in progress
        if (data.playing === true && !!data.state && data.game_number > 0 && data.over === false && data.game_number <= data.games) {
            if(!!data.move){
                console.log('Placing tile.... at ' + data['move'])
                // Click on tile
                await page.click(`.game-content > div:nth-child(1) > button:nth-child(${data['move']}) > div:nth-child(1)`, { delay: 2000 })

                await new Promise(r => setTimeout(r, 2000));

                const reward =  await page.$eval(`.game-content > div:nth-child(1) > button:nth-child(${data['move']})`, (el) => {   
                    return el.getAttribute('class').includes('idle') ? 0 : el.getAttribute('class').includes('mine') ? -1 : el.getAttribute('class').includes('gem') ? 1 : 0
                })
                
                data.reward = reward

                data.state[data.move] = reward

                console.log(data.reward)

                if (data.reward === 1){
                    data.gems = data.state.filter((e) => e === 1).length;

                    if (data.gems === 1) {
                        data.cashout= true;
                        data.over = true;
                        data.state = [...defaultGameState];
                        data.wins += 1;
                    }
                } else if (data.reward === -1){
                    data.over = true;
                    data.mines += 1;
                    data.state = [...defaultGameState];
                    data.looses += 1;
                }

                if(data.cashout === true){
                    await cashout();
                    data.cashout = false;
                }
                
                console.log(data) 
                // Send game state
                await socket.send(JSON.stringify(data));

            }

        }

            // console.log(classes)    
            
           
            // await page.click(`.game-content > div:nth-child(1) > button:nth-child(3) > div:nth-child(1)`, { delay: 1000 })

            // await waitUntil(2000)

            

            // //cashout 
            // const cashoutButton = await page.$eval(`.game-sidebar > button[data-test="cashout-button"]`, (el) => { 
            //     return el.dispatchEvent(new Event('click'));
            // })

            // if(!!cashoutButton){
            //     // await page.click('.game-sidebar > button[data-test="cashout-button"]', { delay: 1000 })
            // }

            

            // console.log(classes)

    }

    await socket.send(JSON.stringify(config));


    await socket.addEventListener('message', async function (event) {

        const data = await JSON.parse(event.data.toString());
        
        await processMessage(data)

    });

    
    await socket.addEventListener('close', async function (event) {
        console.log('Connection closed');

        await page.screenshot({
            path: "../../screenshots/screenshot.jpg",
            fullPage: true,
        });

        // Save cookies
        await saveCookies(page);

        await page.close()

        await browser.close();

        socket.close();
    });



    // // Wait for action
    // socket.addEventListener('message' ,async function (event) {
    //     const data = event.data.toString();

    //     // Parse data from server
    //     const response = JSON.parse(data);

    //     // Check if is a new game
      
    //     page.click('.game-sidebar > button')

    

    //     console.log(classes)

    //     // const countTiles =  buttons.

    //     if(!!response['move'] && response['move'].length > 0) {
    //         // Click on tile
    //         // ${response['move'][0]}
    //         page.click(`.game-content > div:nth-child(1) > button > div:nth-child(1)`)
    //     }

    //     if(!!response['cashout']) {

    //         // Click on 'Cashout' button
    //         page.click('.game-sidebar > button')
    //     }

    //     if(!!response['bet']) {
    //         // Click on 'Bet' button
    //         page.click('.game-sidebar > button')
    //     }

    //     if(response['over']) {
    //         // Click on cashout button
    //         page.click('.game-sidebar > button')
    //     }
    // });


    // Click on 'Bet' button
    // page.click('.game-sidebar > button')
    // waitUntil(5000)

    // Click on a tile
    // page.click('.game-content > div:nth-child(1) > button > div:nth-child(1)')

    // Check if gem or mine
    // On gem check if is the last one
    // If is the last one, click on 'Cashout' button
    // Wait 3 seconds


    // On mine click on 'Bet' button
    // Wait 3 seconds
    // Wait for an action from server

    //identify if is gem or mine

    // cashout or bet again
    
    // await page.setRequestInterception(true);
    // const intercept = async (event) => {
    //     console.log(event)
    // }

    // await client.on('Network.requestIntercepted', async (event) => {
    //     await intercept(event)
    // })


    // page.on('request', async (request) => {
    //     console.log(request)


    //     request.continue()
    // });

    // page.on('requestfinished', async (request) => {
    //     console.log(request.hasPostData())
    //     const response = await request.response();

    //     const responseHeaders = response?.headers();
    //     let responseBody;
    //     if (request.redirectChain().length === 0) {
    //         // body can only be access for non-redirect responses
    //         responseBody = await response?.buffer();

    //         console.log(responseBody.toString())
    //     }

    

    //     request.continue()
    // });

    // console.log(results)

    

})();



function waitUntil(timeout) {
    return new Promise(r => setTimeout(r, timeout));
}


async function saveCookies(page) {
    //
    const cookies = await page?.cookies();
    await fs.writeFile('./cookies.json', JSON.stringify(cookies, null, 2), (err) => {
        if (err)
            console.log(err);
        else {
            console.log("File written successfully\n");
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