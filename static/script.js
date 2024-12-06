document.addEventListener("DOMContentLoaded", function () {
    const dateInput = document.getElementById("date");
    const timeInput = document.getElementById("time");
    const startLocationInput = document.getElementById("start-location");
    const endLocationInput = document.getElementById("end-location");
    const distanceInput = document.getElementById("distance");
    const priceInput = document.getElementById("price");

    // Set the min date to today and max date to 5 days from now
    const today = new Date();
    const maxDate = new Date(today);
    maxDate.setDate(today.getDate() + 5);

    const formatDate = (date) => date.toISOString().split("T")[0];
    dateInput.min = formatDate(today);
    dateInput.max = formatDate(maxDate);
    dateInput.value = formatDate(today);

    // Populate time slots
    for (let hour = 6; hour <= 20; hour++) {
        for (let minute = 0; minute < 60; minute += 30) {
            const formattedTime = `${hour < 10 ? "0" : ""}${hour}:${minute === 0 ? "00" : minute}`;
            const timeOption = document.createElement("option");
            timeOption.value = formattedTime;
            timeOption.textContent = formattedTime;
            timeInput.appendChild(timeOption);
        }
    }

    // Initialize the map
    const map = L.map("map").setView([32.7266, 74.8570], 12); // Jammu City Coordinates

    // Add OpenStreetMap tiles
    L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
        maxZoom: 19,
    }).addTo(map);

    // Add a search bar for locations
    const geocoder = L.Control.geocoder({
        collapsed: false,
        position: 'topright',
    }).addTo(map);

    let startPoint = null;
    let endPoint = null;
    const markers = [];

    // Handle search result
    geocoder.on("markgeocode", function (e) {
        const latlng = e.geocode.center;
        map.setView(latlng, 14);

        // If start and end are not set, assign them
        if (!startPoint) {
            startPoint = latlng;
            startLocationInput.value = `${startPoint.lat.toFixed(6)}, ${startPoint.lng.toFixed(6)}`;
            const marker = L.marker(latlng, { title: "Start Location" }).addTo(map);
            markers.push(marker);
        } else if (!endPoint) {
            endPoint = latlng;
            endLocationInput.value = `${endPoint.lat.toFixed(6)}, ${endPoint.lng.toFixed(6)}`;
            const marker = L.marker(latlng, { title: "End Location" }).addTo(map);
            markers.push(marker);

            // Add the route between start and end points
            const routingControl = L.Routing.control({
                waypoints: [startPoint, endPoint],
                routeWhileDragging: true,
            }).addTo(map);

            routingControl.on("routesfound", function (e) {
                const route = e.routes[0];
                const distance = (route.summary.totalDistance / 1000).toFixed(2); // Distance in km
                distanceInput.value = distance;

                // Calculate price (₹10 per km)
                const price = distance * 10;
                priceInput.value = price.toFixed(2);
            });
        }
    });

    // Handle clicks on the map to set start and end points
    map.on("click", function (e) {
        if (!startPoint) {
            startPoint = e.latlng;
            startLocationInput.value = `${startPoint.lat.toFixed(6)}, ${startPoint.lng.toFixed(6)}`;
            const marker = L.marker(startPoint, { title: "Start Location" }).addTo(map);
            markers.push(marker);
        } else if (!endPoint) {
            endPoint = e.latlng;
            endLocationInput.value = `${endPoint.lat.toFixed(6)}, ${endPoint.lng.toFixed(6)}`;
            const marker = L.marker(endPoint, { title: "End Location" }).addTo(map);
            markers.push(marker);

            // Add the route between start and end points
            const routingControl = L.Routing.control({
                waypoints: [startPoint, endPoint],
                routeWhileDragging: true,
            }).addTo(map);

            routingControl.on("routesfound", function (e) {
                const route = e.routes[0];
                const distance = (route.summary.totalDistance / 1000).toFixed(2); // Distance in km
                distanceInput.value = distance;

                // Calculate price (₹10 per km)
                const price = distance * 10;
                priceInput.value = price.toFixed(2);
            });
        }
    });

    // Reset map on form reset or new selection
    document.getElementById("booking-form").addEventListener("reset", function () {
        startPoint = null;
        endPoint = null;
        startLocationInput.value = "";
        endLocationInput.value = "";
        distanceInput.value = "";
        priceInput.value = "";
        markers.forEach((marker) => map.removeLayer(marker));
        markers.length = 0;
    });
});
