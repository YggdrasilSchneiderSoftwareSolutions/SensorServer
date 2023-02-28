window.onload = async () => {
    await fetch('/data')
        .then(response => response.json())
        .then(data => {
            console.log(data);
            // TODO
        });
}