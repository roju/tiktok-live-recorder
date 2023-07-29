try {
    console.log('ttlr roominfo url loaded');
    const bodyText = document.body.innerText;
    // console.log(`body text: ${bodyText}`);
    const obj = JSON.parse(bodyText);
    const extractedData = {
        username: obj.data.owner.display_id, 
        live_url: obj.data.stream_url.rtmp_pull_url
    }
    chrome.runtime.sendMessage({extractedData})
    .then(() => console.log('sent extracted data to worker:', extractedData));
}
catch(err) {
    console.error(err);
}