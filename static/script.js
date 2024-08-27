document.addEventListener('DOMContentLoaded', function() {
    const pdfForm = document.getElementById('pdf-question-form');
    const chatForm = document.getElementById('chat-form');
    const pdfAnswerDiv = document.getElementById('pdf-answer');
    const chatBox = document.getElementById('chat-box');
    const sendButton = document.getElementById('send-button');

    // Handle PDF upload and question submission
    pdfForm.addEventListener('submit', function(e) {
        e.preventDefault();
        const formData = new FormData(pdfForm);

        // Display "Processing..." message
        pdfAnswerDiv.textContent = 'Processing...';

        fetch('/', {
            method: 'POST',
            body: formData
        })
        .then(response => response.json())
        .then(data => {
            if (data.error) {
                pdfAnswerDiv.textContent = 'Error: ' + data.error;
            } else {
                pdfAnswerDiv.textContent = data.message || data.answer;
            }
        })
        .catch(error => {
            console.error('Error:', error);
            pdfAnswerDiv.textContent = 'An error occurred. Please try again.';
        });
    });

    // Handle chat message submission
    chatForm.addEventListener('submit', function(e) {
        e.preventDefault();
        const userMessage = document.getElementById('message').value;
        const formData = new FormData();
        formData.append('message', userMessage);

        // Append user message to chat box
        chatBox.innerHTML += `<div class="user-message">${userMessage}</div>`;
        document.getElementById('message').value = ''; // Clear input field

        fetch('/', {
            method: 'POST',
            body: formData
        })
        .then(response => response.json())
        .then(data => {
            if (data.error) {
                chatBox.innerHTML += `<div class="error-message">Error: ${data.error}</div>`;
            } else {
                chatBox.innerHTML += `<div class="ai-message">${data.answer}</div>`;
            }
            chatBox.scrollTop = chatBox.scrollHeight; // Scroll to the bottom
        })
        .catch(error => {
            console.error('Error:', error);
            chatBox.innerHTML += `<div class="error-message">An error occurred. Please try again.</div>`;
            chatBox.scrollTop = chatBox.scrollHeight; // Scroll to the bottom
        });
    });

    // Prevent file input from being cleared on form reset
    pdfForm.addEventListener('reset', function(e) {
        e.preventDefault();
        pdfForm.reset();
        fileInput.value = ''; // Clear file input manually
    });
});
