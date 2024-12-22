document.addEventListener('DOMContentLoaded', () => {
    const userInput = document.getElementById('user-input');
    const sendButton = document.getElementById('send-btn');
    const messages = document.getElementById('messages');

    const addMessage = (text, sender) => {
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${sender}`;
        messageDiv.textContent = text;
        messages.appendChild(messageDiv);
        messages.scrollTop = messages.scrollHeight;
        return messageDiv;
    };

    const addLoadingIndicator = () => {
        const loadingDiv = document.createElement('div');
        loadingDiv.className = 'loading-indicator bot';
        loadingDiv.innerHTML = '<span></span><span></span><span></span>';
        messages.appendChild(loadingDiv);
        messages.scrollTop = messages.scrollHeight;
        return loadingDiv;
    };

    const removeLoadingIndicator = (loadingDiv) => {
        if (loadingDiv) {
            messages.removeChild(loadingDiv);
        }
    };

    const showCustomDialog = (question) => {
        return new Promise((resolve) => {
            const overlay = document.createElement('div');
            overlay.className = 'dialog-overlay';

            const dialogBox = document.createElement('div');
            dialogBox.className = 'dialog-box';

            const dialogMessage = document.createElement('p');
            dialogMessage.textContent = `What should be the answer for "${question}"?`;
            dialogBox.appendChild(dialogMessage);

            const inputField = document.createElement('input');
            inputField.type = 'text';
            inputField.placeholder = 'Type your answer here...';
            dialogBox.appendChild(inputField);

            const buttonContainer = document.createElement('div');
            buttonContainer.className = 'dialog-buttons';

            const submitButton = document.createElement('button');
            submitButton.textContent = 'Submit';
            submitButton.onclick = () => {
                resolve(inputField.value.trim());
                document.body.removeChild(overlay);
            };

            const cancelButton = document.createElement('button');
            cancelButton.textContent = 'Cancel';
            cancelButton.onclick = () => {
                resolve(null);
                document.body.removeChild(overlay);
            };

            buttonContainer.appendChild(submitButton);
            buttonContainer.appendChild(cancelButton);
            dialogBox.appendChild(buttonContainer);

            overlay.appendChild(dialogBox);
            document.body.appendChild(overlay);
        });
    };

    const sendMessage = async () => {
        const message = userInput.value.trim();
        if (!message) return;

        addMessage(message, 'user');
        userInput.value = '';

        const loadingIndicator = addLoadingIndicator();

        setTimeout(async () => {
            try {
                const response = await fetch('/get_response', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ message })
                });

                const data = await response.json();
                removeLoadingIndicator(loadingIndicator);
                addMessage(data.response, 'bot');

                if (data.response === "I don't know the answer to that. Please teach me!") {
                    const answer = await showCustomDialog(message);
                    if (answer) {
                        await fetch('/teach_bot', {
                            method: 'POST',
                            headers: { 'Content-Type': 'application/json' },
                            body: JSON.stringify({ question: message, answer })
                        });
                        addMessage("Thanks for teaching me!", 'bot');
                    }
                }
            } catch (error) {
                removeLoadingIndicator(loadingIndicator);
                addMessage("An error occurred. Please try again.", 'bot');
            }
        }, 2000);
    };

    sendButton.addEventListener('click', sendMessage);
    userInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') sendMessage();
    });
});
