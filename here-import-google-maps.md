Steps:

1. Google Takeout in JSON format.
2. Open wego.here.com
3. Add a single favorite to the wanted collection to get its ID and CSRF.
4. In JS console Network tab copy the XHR request as Fetch.
5. Paste Google Maps JSON in JS console and assign to `google` var.
6. Convert Google Maps JSON format to HERE JSON format:
  ```
nokia = google.features.map(feature => ({
    name: feature.properties.Title,
    type: 'favoritePlace',
    categories: [{categoryId: 'street-square'}],
    _addToCollections: [YOUR_COLLECTION_ID_HERE],
    location: {position: {
        latitude: feature.geometry.coordinates[1],
        longitude: feature.geometry.coordinates[0],
    }},
}))
  ```
7. Define function that will add a new favorite each second:
  ```
function addFav(places, current = 0) {
    if (current >= places.length) {
        console.log('DONE', current);
    }

    console.log('ADDING:', current);

    return fetch("https://wego.here.com/api/collections/favoritePlace", {
        "credentials": "include",
        "headers": {
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:74.0) Gecko/20100101 Firefox/74.0",
            "Accept": "application/json",
            "Accept-Language": "en-US,en;q=0.5",
            "Cache-Control": "no-cache, no-store, must-revalidate",
            "Pragma": "no-cache",
            "Expires": "0",
            "Content-Type": "application/json;charset=utf-8",
            "CSRF-Token": YOUR_CSRF_TOKEN_HERE
        },
        "referrer": YOUR_REFERRER_HERE,
        "body": JSON.stringify(nokia[current]),
        "method": "POST",
        "mode": "cors"
    }).then(response => {
        console.log('RESULT:', response, current);

        if (response.ok) {
            setTimeout(() => {
                addFav(places, current + 1);
            }, 1_000);
        }
    });
}
  ```
8. Run function: `addFav(nokia)`
