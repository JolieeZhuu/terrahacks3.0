// Access user's microphone
navigator.mediaDevices.getUserMedia({ audio: true })
  .then(function(stream) {
    // Create MediaRecorder instance
    let mediaRecorder = new MediaRecorder(stream);

    // Initialize data chunks array
    let chunks = [];

    // Event handler for data available
    mediaRecorder.ondataavailable = function(event) {
      chunks.push(event.data);
    };

    // Event handler for recording stop
    mediaRecorder.onstop = function() {
      // Combine data chunks into a single Blob
      let blob = new Blob(chunks, { type: 'audio/mp3' });
      
      // Do something with the recorded audio Blob
      // For example, you could upload it to a server or play it back to the user
    };

    // Start recording
    mediaRecorder.start();

    // Stop recording after 5 seconds (for demonstration purposes)
    setTimeout(function() {
      mediaRecorder.stop();
    }, 5000);
  })
  .catch(function(err) {
    console.error('Error accessing microphone:', err);
  });