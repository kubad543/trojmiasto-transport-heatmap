var map = L.map('map').setView([54.5, 18.67], 13);

L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
}).addTo(map);

// Define the keys for latitude and longitude
const latKey = 'latitude';  // Adjust this to your JSON key for latitude
const lonKey = 'longitude';  // Adjust this to your JSON key for longitude

// Function to convert coordinates to decimal degrees
function convertToDecimal(degree, direction) {
    let decimal = parseFloat(degree);
    if (isNaN(decimal)) {
        return null; // Handle invalid input
    }
    // Negate the value for South or West
    if (direction === 'S' || direction === 'W') {
        decimal *= -1; 
    }
    return decimal;
}

// Function to process coordinates
function getCoordinates(point) {
    let latitude, longitude;

    // Process latitude
    if (point.lat) {
        const latParts = point.lat.trim().split(' ');
        if (latParts.length === 2) {
            latitude = convertToDecimal(latParts[0], latParts[1]);
        } else {
            latitude = parseFloat(point.lat); // Fallback to numeric value
        }
    } else if (typeof point[latKey] === 'number') {
        latitude = point[latKey];
    } else if (typeof point[latKey] === 'string') {
        latitude = parseFloat(point[latKey]); // Fallback to numeric value
    }

    // Process longitude
    if (point.lon) {
        const lonParts = point.lon.trim().split(' ');
        if (lonParts.length === 2) {
            longitude = convertToDecimal(lonParts[0], lonParts[1]);
        } else {
            longitude = parseFloat(point.lon); // Fallback to numeric value
        }
    } else if (typeof point[lonKey] === 'number') {
        longitude = point[lonKey];
    } else if (typeof point[lonKey] === 'string') {
        longitude = parseFloat(point[lonKey]); // Fallback to numeric value
    }

    return { latitude, longitude };
}

fetch('poi.json')
    .then(response => response.json())
    .then(data => {
        console.log(`Total points fetched: ${data.length}`); // Log total number of points

        data.forEach(point => {
            const coords = getCoordinates(point);

            // If coordinates are valid, add the marker to the map
            if (coords) {
                const { latitude, longitude } = coords;
                console.log(`Processing Point: ${point.name || 'Unnamed'}, Latitude: ${latitude}, Longitude: ${longitude}`);

                if (latitude !== null && longitude !== null) {
                    L.marker([latitude, longitude]).addTo(map)
                        .bindPopup('Name: ' + (point.name || 'Unnamed') + '<br>Latitude: ' + latitude + '<br>Longitude: ' + longitude);
                } else {
                    console.error(`Invalid coordinates for point: ${point.name || 'Unnamed'}`);
                }
            } else {
                console.error(`Unable to get coordinates for point: ${point.name || 'Unnamed'}`);
            }
        });
    })
    .catch(error => {
        console.error('Error fetching POI data:', error);
    });
