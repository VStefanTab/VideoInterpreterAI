function SendRTSPLink() {
    const rtspLink = document.getElementById("rtsp_link").value;
    if (rtspLink) {
        fetch("/", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({ link: rtspLink })
        })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    window.location.href = data.redirect_url;
                }
            })
            .catch(error => {
                console.error("Error:", error);
            });
    } else {
        alert("Please enter a valid RTSP link.");
    }
}

function StartInterpretor() {
    const prompt = document.getElementById("prompt").value;
    const frame = document.getElementById("video_frame");

    button = document.getElementById("stream");
    button.disabled = true;
    button.innerText = "Running...";

    // Create a canvas and draw the frame onto it
    const canvas = document.createElement("canvas");
    canvas.width = frame.videoWidth || frame.naturalWidth || frame.width;
    canvas.height = frame.videoHeight || frame.naturalHeight || frame.height;
    const ctx = canvas.getContext("2d");
    ctx.drawImage(frame, 0, 0, canvas.width, canvas.height);

    // Get Base64-encoded image data
    const frameData = canvas.toDataURL("image/jpeg");

    const Payload = {
        prompt: prompt,
        frame: frameData
    };

    if (Payload) {
        fetch("/interpreter", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify(Payload)
        })
            .then(response => response.json())
            .then(data => {
                console.log("Interpreter started:", data);
            })
            .catch(error => {
                console.error("Error starting interpreter:", error);
            });
    } else {
        alert("Please enter a prompt.");
    }
}