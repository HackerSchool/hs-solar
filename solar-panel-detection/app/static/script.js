   // fetches image prediction result after submission and displays it on page 
    document.getElementById("uploadForm").addEventListener("submit", async function(event) {
        event.preventDefault();
        
        const formData = new FormData();
        const fileInput = document.getElementById("imageInput");
        
        if (fileInput.files.length === 0) {
            alert("Please select an image.");
            return;
        }
        
        formData.append("image", fileInput.files[0]);
        
        try {
            const response = await fetch("/predict", {
                method: "POST",
                body: formData
            });
            
            const text = await response.text();
            let result;
            try {
                result = JSON.parse(text);
            } catch (jsonError) {
                alert("Invalid response from server, not JSON.");
                return;
            }
                
            console.log(result)
            if (result.image) {
                const imgElement = document.getElementById("result");
                imgElement.src = result.image;
                imgElement.style.display = "block";
            } else {
                alert("Invalid response from server, missing result image URL.");
            }
        } catch (error) {
            console.error("Error uploading image:", error);
        }
    });