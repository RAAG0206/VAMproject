function validateFileSize() {
    var input = document.getElementById("file-upload");
    var fileSize = input.files[0].size;
    var maxSize = 1000000 // size in bytes

    if (fileSize > maxSize) {
        alert("File size exceeds the limit. Please choose a smaller file.")
        input.value = ""
    }
}

document.getElementById("resolution").addEventListener("change", e => {
    console.log(e.target.value)
    document.getElementById("res-value").innerHTML = `${e.target.value}`;
})

document.getElementById("uploadForm").addEventListener("submit", function (event) {
    event.preventDefault();

    var formData = new FormData();
    formData.append("stl", document.getElementById("file-upload").files[0]);
    formData.append("resolution", document.getElementById("resolution").value);

    if (typeof (formData.get("stl")) === "undefined" || typeof (formData.get("stl")) === null) {
        alert("Please select a file to upload.")
        return
    }

    // Prevent form submission if CAPTCHA is not completed
    /*
    var captchaResponse = grecaptcha.getResponse();
    if (captchaResponse.length == 0) {
        event.preventDefault();
        alert("Please complete the CAPTCHA.");
        return
    }
    */ 

    fetch("/check_access/", {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
            "X-CSRFToken": window.csrfToken
        },
        body: JSON.stringify({}),
    })
        .then(response => response.json())
        .then(data => {
            if (data.allowed) {
                // User is allowed to perform the action

                fetch("/", {
                    method: "POST",
                    headers: {
                        "X-CSRFToken": window.csrfToken
                    },
                    body: formData
                })
                .then(response => response.json())
                .then(responseData => {
                    const scene = document.getElementById("threed-scene");

                    // Clear the current content of the scene
                    while (scene.firstChild) {
                        scene.removeChild(scene.firstChild);
                    }

                    // Parse the X3D content
                    const parser = new DOMParser();
                    const x3dDocument = parser.parseFromString(responseData.x3d_content, "application/xml");

                    // Append all child nodes to the scene
                    Array.from(x3dDocument.documentElement.childNodes).forEach(node => {
                        scene.appendChild(document.importNode(node, true));
                    });

                    console.log("X3D content processed and displayed.");
                })
                .catch(error => {
                    alert("Error when submitting the file:");
                    console.log(error);
                });
            } else {
                // User is not allowed
                alert("Access denied, processing limit exceeded. Please wait 48 hours to try again.");
            }
        })
        .catch(error => {
            console.error('Error:', error);
        });
});