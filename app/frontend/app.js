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