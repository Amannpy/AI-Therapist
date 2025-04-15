document.addEventListener('DOMContentLoaded', function() {
    const messageForm = document.getElementById('message-form');
    const messageInput = document.getElementById('message-input');
    const chatHistory = document.getElementById('chat-history');
    const typingIndicator = document.getElementById('typing-indicator');
    
    // Initialize chat history
    loadChatHistory();
    
    // Submit message on form submit
    messageForm.addEventListener('submit', function(e) {
        e.preventDefault();
        const message = messageInput.value.trim();
        
        if (message) {
            sendMessage(message);
            messageInput.value = '';
        }
    });
    
    // Listen for Enter key (but allow Shift+Enter for new lines)
    messageInput.addEventListener('keydown', function(e) {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            messageForm.dispatchEvent(new Event('submit'));
        }
    });
    
    // Function to load chat history
    function loadChatHistory() {
        // Scroll to bottom of chat
        scrollToBottom();
        
        // Add click handlers for existing feedback buttons
        addFeedbackHandlers();
    }
    
    // Function to send message to backend
    function sendMessage(message) {
        // Add user message to UI immediately
        addMessageToUI(message, true);
        
        // Show typing indicator
        typingIndicator.style.display = 'block';
        
        // Send to backend
        fetch('/api/send_message', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ message }),
        })
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            return response.json();
        })
        .then(data => {
            // Hide typing indicator
            typingIndicator.style.display = 'none';
            
            // Add AI response to UI
            addMessageToUI(data.message, false, data.emotion, data.ai_message_id);
            
            // Check for crisis
            if (data.crisis_detected) {
                showCrisisAlert();
            }
            
            // Show API error notification if needed
            if (data.api_error) {
                showApiErrorAlert();
            }
        })
        .catch(error => {
            console.error('Error sending message:', error);
            typingIndicator.style.display = 'none';
            
            // Show error message
            addMessageToUI("I'm sorry, I'm having trouble connecting. Please try again in a moment.", false);
        });
    }
    
    // Function to add message to UI
    function addMessageToUI(message, isUser, emotion = null, messageId = null) {
        const messageElement = document.createElement('div');
        messageElement.className = isUser ? 'message user-message' : 'message ai-message';
        
        // Format the message content
        let messageContent = `<div class="message-content">${formatMessage(message)}</div>`;
        
        // Add emotion badge for user messages
        if (isUser && emotion) {
            messageContent += `<div class="emotion-badge">${emotion}</div>`;
        }
        
        // Add feedback buttons for AI messages
        if (!isUser && messageId) {
            messageContent += `
                <div class="feedback-buttons" data-message-id="${messageId}">
                    <button class="btn btn-sm btn-outline-success feedback-button" data-feedback="positive">
                        <i class="fas fa-thumbs-up"></i>
                    </button>
                    <button class="btn btn-sm btn-outline-danger feedback-button" data-feedback="negative">
                        <i class="fas fa-thumbs-down"></i>
                    </button>
                </div>
            `;
        }
        
        messageElement.innerHTML = messageContent;
        chatHistory.appendChild(messageElement);
        
        // Add feedback handlers for new message
        if (!isUser && messageId) {
            const feedbackButtons = messageElement.querySelectorAll('.feedback-button');
            feedbackButtons.forEach(button => {
                button.addEventListener('click', handleFeedback);
            });
        }
        
        // Scroll to bottom
        scrollToBottom();
    }
    
    // Function to format message (convert links, line breaks, etc.)
    function formatMessage(text) {
        // Convert line breaks to <br>
        text = text.replace(/\n/g, '<br>');
        
        // Convert URLs to clickable links
        text = text.replace(
            /(https?:\/\/[^\s]+)/g, 
            '<a href="$1" target="_blank" rel="noopener noreferrer">$1</a>'
        );
        
        return text;
    }
    
    // Function to handle feedback clicks
    function handleFeedback(e) {
        const button = e.currentTarget;
        const messageId = button.parentElement.dataset.messageId;
        const isPositive = button.dataset.feedback === 'positive';
        
        // Disable all feedback buttons for this message
        const buttonsContainer = button.parentElement;
        const allButtons = buttonsContainer.querySelectorAll('.feedback-button');
        allButtons.forEach(btn => {
            btn.disabled = true;
            btn.classList.remove('btn-outline-success', 'btn-outline-danger');
            btn.classList.add('btn-secondary');
        });
        
        // Highlight the selected button
        button.classList.remove('btn-secondary');
        button.classList.add(isPositive ? 'btn-success' : 'btn-danger');
        
        // Show thank you message
        const thankYou = document.createElement('span');
        thankYou.className = 'feedback-thanks';
        thankYou.textContent = 'Thanks for your feedback!';
        buttonsContainer.appendChild(thankYou);
        
        // Send feedback to backend
        fetch('/api/feedback', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ 
                message_id: messageId,
                is_positive: isPositive
            }),
        })
        .catch(error => {
            console.error('Error sending feedback:', error);
        });
    }
    
    // Function to add click handlers to all feedback buttons
    function addFeedbackHandlers() {
        const feedbackButtons = document.querySelectorAll('.feedback-button');
        feedbackButtons.forEach(button => {
            button.addEventListener('click', handleFeedback);
        });
    }
    
    // Function to scroll chat to bottom
    function scrollToBottom() {
        chatHistory.scrollTop = chatHistory.scrollHeight;
    }
    
    // Function to show crisis alert
    function showCrisisAlert() {
        const alertElement = document.createElement('div');
        alertElement.className = 'alert alert-danger crisis-alert';
        alertElement.innerHTML = `
            <strong>Important:</strong> If you're having thoughts of harming yourself or feeling suicidal, 
            please reach out for immediate help:
            <ul>
                <li>National Suicide Prevention Lifeline: <strong>988</strong> (call or text)</li>
                <li>Crisis Text Line: Text <strong>HOME</strong> to <strong>741741</strong></li>
                <li>Or go to your nearest emergency room</li>
            </ul>
            <p>You're not alone, and help is available.</p>
        `;
        
        // Insert at top of chat
        chatHistory.insertBefore(alertElement, chatHistory.firstChild);
    }
    
    // Function to show API error alert
    function showApiErrorAlert() {
        const alertElement = document.createElement('div');
        alertElement.className = 'alert alert-warning api-error-alert';
        alertElement.innerHTML = `
            <strong>Notice:</strong> The AI service is currently experiencing some limitations. 
            <p>The administrator has been notified. In the meantime, your conversation history is still being saved.</p>
        `;
        
        // Insert at top of chat
        chatHistory.insertBefore(alertElement, chatHistory.firstChild);
        
        // Remove the alert after 10 seconds
        setTimeout(() => {
            alertElement.remove();
        }, 10000);
    }
});
