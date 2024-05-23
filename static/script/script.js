/*
$ = function(id) {
    return document.getElementById(id);
}

    var show = function(id) {
        $(id).style.display ='block';
}
    var hide = function(id) {
        $(id).style.display ='none';
}
*/
function $(id) {
    return document.getElementById(id);
}

var show = function(id, elementId) {
    var xhr = new XMLHttpRequest();
    xhr.onreadystatechange = function() {
        if (xhr.readyState == 4 && xhr.status == 200) {
            // Select the H1 and p elements
            var h1Element = document.querySelector('#' + id + ' H1');
            var pElement = document.querySelector('#' + id + ' p');
            
            // Set the innerHTML of the H1 element to the elementId
            h1Element.innerHTML = elementId;

            // Set the innerHTML of the p element to the response text
            pElement.innerHTML = xhr.responseText;

            // Show the container element
            $(id).style.display = 'block';
        }
    };

    // Clear previous values
    var h1Element = document.querySelector('#' + id + ' H1');
    var pElement = document.querySelector('#' + id + ' p');
    h1Element.innerHTML = '';
    pElement.innerHTML = '';

    // Send the GET request to the server
    xhr.open("GET", "/get_content?id=" + elementId, true);
    xhr.send();
};


var hide = function(id) {
    $(id).style.display = 'none';
};

const fileInput = document.getElementById('videoFile');

fileInput.addEventListener('change', function() {
    const selectedFile = this.files[0];

    const fileNameElement = document.getElementById('fileName');
    fileNameElement.textContent = selectedFile.name;
});

document.getElementById('uploadButton').addEventListener('click', function() {
    var elementsToHide = ['Container2', 'Container3', 'progressBarContainer', 'videoPlayer2Container', 'speciesContainer', 'Dolphin', 'Eel', 'JellyFish', 'PufferFish', 'Stingray', 'Sea-Urchin', 'Seahorse', 'Pinniped', 'Shark', 'Starfish'];
    elementsToHide.forEach(function(id) {
        var element = document.getElementById(id);
        if (element && (element.style.display === 'block' || element.style.display === 'flex')) {
            element.style.display = 'none';
        }
    });

    var fileInput = document.getElementById('videoFile');
    var file = fileInput.files[0];
    if (file) {
        var formData = new FormData();
        formData.append('videoFile', file);
        fetch('/upload_video', {
            method: 'POST',
            body: formData
        })
        .then(response => response.json())
        .then(data => {
            var Container2 = document.getElementById('Container2');
            Container2.style.display = 'block';
            var videoPlayer = document.getElementById('videoPlayer1');
            videoPlayer.src = URL.createObjectURL(file);
        })
        .catch(error => console.error('Error:', error));
    } else {
        console.log('No file selected.');
    }
});
       
document.getElementById('detectButton').addEventListener('click', function(event) {
    var elementsToHide = ['Container3', 'progressBarContainer', 'videoPlayer2Container', 'speciesContainer', 'Dolphin', 'Eel', 'JellyFish', 'PufferFish', 'Stingray', 'Sea-Urchin', 'Seahorse', 'Pinniped', 'Shark', 'Starfish'];
    elementsToHide.forEach(function(id) {
        var element = document.getElementById(id);
        if (element && (element.style.display === 'block' || element.style.display === 'flex')) {
            element.style.display = 'none';
        }
    });
    const eventSource = new EventSource('/get_second_video_location');

    eventSource.onmessage = function(event) {
        const data = JSON.parse(event.data);
        if (data.progressValue < 100) {
            if(data.progressValue == 0){
                var Container3 = document.getElementById('Container3');
                Container3.style.display = 'block';
                var progressBarContainer = document.getElementById('progressBarContainer');
                progressBarContainer.style.display = 'block';
            }
            updateProgressBar(data.progressValue);
        } else {
            var videoPlayer2Container = document.getElementById('videoPlayer2Container');
            var videoPlayer2 = document.getElementById('videoPlayer2');
            videoPlayer2.src = data.videoLocation;
            videoPlayer2Container.style.display = 'flex';
            var progressBarContainer = document.getElementById('progressBarContainer');
            progressBarContainer.style.display = 'none';

            eventSource.close();
                    
            if(data.selectedObjects.length > 0){
                var speciesContainer = document.getElementById('speciesContainer');
                speciesContainer.style.display = 'block';

                var count = 1;
                data.selectedObjects.forEach(className => {
                    var element = document.getElementById(className);
                    element.style.display = 'block';
                    if(count % 5 == 0){
                        var firstDiv = element.querySelector('div');
                        firstDiv.style.clear = 'left';
                    }
                });
            }
        }
    };
});

var progressBar = new ProgressBar.Circle('#progressBar', {
    color: '#007bff',
    strokeWidth: 5,
    trailWidth: 5,
    duration: 0,
    text: {
    value: '0%'
    }
});

var progressBarContainer = document.getElementById('progressBarContainer');
progressBarContainer.style.width = '400px';
progressBarContainer.style.margin = '0 auto';
progressBarContainer.style.display = 'none';

function updateProgressBar(progressValue) {
    progressBar.animate(progressValue / 100);
    progressBar.setText((progressValue).toFixed(0) + '%');
}