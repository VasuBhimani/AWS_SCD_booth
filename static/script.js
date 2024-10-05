// Modified JavaScript code
const video = document.getElementById('video');
const canvas = document.getElementById('canvas');
const countdownDisplay = document.getElementById('countdown');
const context = canvas.getContext('2d');

// Access the device camera and set canvas size to video size
navigator.mediaDevices.getUserMedia({ video: true })
    .then(stream => {
        video.srcObject = stream;

        // Wait for video to load metadata and set canvas size accordingly
        video.addEventListener('loadedmetadata', () => {
            canvas.width = video.videoWidth;
            canvas.height = video.videoHeight;
        });
    })
    .catch(err => {
        console.error("Error accessing the camera: " + err);
    });

// Initialize the countdown timer
let countdown = 8;
countdownDisplay.textContent = countdown;

// Create a countdown interval
const countdownInterval = setInterval(() => {
    countdown--;
    countdownDisplay.textContent = `Capturing in ${countdown}`;

    if (countdown === 0) {
        clearInterval(countdownInterval);
        countdownDisplay.textContent = "Click!";
        
        // Capture the image from the video and send it to the server
        context.drawImage(video, 0, 0, canvas.width, canvas.height);
        const imageData = canvas.toDataURL('image/jpg');

        // Stop the camera stream
        video.srcObject.getTracks().forEach(track => track.stop());

        // Send the image data to the server for saving
        fetch('http://ec2-3-109-55-174.ap-south-1.compute.amazonaws.com:5000/save-image', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ image: imageData })
        })
        .then(response => response.json()
    )
        .then(data => {
            console.log("Image saved, starting API call", data);
            datasend(); // This is optional, but ensure the function `datasend()` works

        })
        .catch(error => console.error("Error:", error));

        window.location.href = nextPageUrl;
    }
}, 1000);
