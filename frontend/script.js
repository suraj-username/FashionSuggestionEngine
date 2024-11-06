// frontend/script.js

async function submitSearch() {
    const textInput = document.getElementById('textInput').value;
    const imageInput = document.getElementById('imageInput').files[0];

    const formData = new FormData();
    if (textInput) {
        formData.append("textInput", textInput);
    }
    if (imageInput) {
        formData.append("imageInput", imageInput);
    }

    const response = await fetch('http://127.0.0.1:5000/search', {
        method: 'POST',
        body: formData
    });

    const result = await response.json();
    displayResults(result.results); // Show initial search results

    // Clear the input fields after search
    document.getElementById('textInput').value = '';  // Clear text input
    document.getElementById('imageInput').value = ''; // Clear image input
}


function displayResults(results) {
    const resultsContainer = document.getElementById('resultsContainer');
    const reverseSearchContainer = document.getElementById('reverseSearchContainer');
    resultsContainer.innerHTML = ''; // Clear previous search results
    reverseSearchContainer.innerHTML = '';

    results.forEach(item => {
        const resultItem = document.createElement('div');
        resultItem.className = 'link-item';

        // Create a card for each result
        const card = document.createElement('div');
        card.className = 'card'; // New class for the card layout

        const img = document.createElement('img');
        img.src = item.image_url; // Display image from search
        img.alt = item.product_title; // Alternative text for the image
        img.onclick = () => reverseImageSearch(item.image_url);
        card.appendChild(img);

        const title = document.createElement('p');
        title.textContent = item.product_title;
        title.onclick = () => reverseImageSearch(item.image_url);
        card.appendChild(title);
        card.onclick = () => reverseImageSearch(item.image_url);

        resultItem.appendChild(card);
        resultsContainer.appendChild(resultItem); // Append to initial results container
    });
}

async function reverseImageSearch(imageUrl) {
    // Show the loader when the search starts
    const loader = document.querySelector('.loader');
    loader.style.display = 'block'; // Show the loader

    // Perform the reverse image search
    const response = await fetch('http://127.0.0.1:5000/reverse-search', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ image_url: imageUrl })
    });

    // Hide the loader after the response is received
    loader.style.display = 'none'; // Hide the loader

    const result = await response.json();
    displayEcommerceLinks(result.links); // Show reverse search results
}

function displayEcommerceLinks(links) {
    const reverseSearchContainer = document.getElementById('reverseSearchContainer');
    reverseSearchContainer.innerHTML = ''; // Clear previous reverse search results

    links.forEach(link => {
        const linkItem = document.createElement('div');
        linkItem.className = 'link-item';

        // Create a card for each link
        const card = document.createElement('div');
        card.className = 'card'; // New class for the card layout

        const img = document.createElement('img');
        img.src = link.image_url; // Display image from reverse search
        img.alt = link.page_title; // Alternative text for the image
        card.appendChild(img);

        const title = document.createElement('a');
        title.href = link.page_url; // Redirect to the e-commerce page
        title.textContent = link.page_title; // Title of the product
        title.target = "_blank"; // Open in new tab
        card.appendChild(title);

        linkItem.appendChild(card);
        reverseSearchContainer.appendChild(linkItem); // Append to reverse search results container
    });
}
