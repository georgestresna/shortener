async function shorten() {
    const url = document.getElementById('url').value;
    const res = await fetch('/api/shorten', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({url})
    });
    const data = await res.json();
    document.getElementById('result').innerHTML = 
        `Shortened: <a href="/r/${data.code}" target="_blank">/r/${data.code}</a>`;
}

// functia shorten():
// const url: ia inputul din HTML
// const res = apeleaza un POST din api, stringify url:<url-ul>
// const data = asateapta rezultatul din api, il pune in json
// schimba apoi innerHTML cu un link direct catre backend /r/codul si pune acest hyperlink pe insusi textul codului shortened 