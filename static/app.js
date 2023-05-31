window.onload = async () => {
    await fetch('/data/Wohnzimmer')
        .then(response => response.json())
        .then(data => {
            console.log(data);
            // TODO
        });
}