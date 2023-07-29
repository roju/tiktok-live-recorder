chrome.runtime.onMessage.addListener((request, sender) => {
    console.log('received data from content script:', request);
    if (request.extractedData) {
        sendDataToPythonServer(request.extractedData)
        .then(() => chrome.tabs.remove(sender.tab.id));
        
    }
});

async function sendDataToPythonServer(data) {
    try {
        const response = await fetch("http://localhost:8000", {
            method: "POST",
            headers: {
              "Content-Type": "application/json",
            },
            body: JSON.stringify(data),
        });
        if (response.ok) {
            console.log("POST request successful");
        } else {
            throw Error(`POST request failed with status: ${response.status}`);
        }
    }
    catch(err) {
        console.error('POST request failed, make sure ttlr.py is running and server started');
        console.error(err);
    }
}