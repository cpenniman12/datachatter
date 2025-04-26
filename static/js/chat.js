document.addEventListener('DOMContentLoaded', function() {
    const chatForm = document.getElementById('chat-form');
    const userInput = document.getElementById('user-input');
    const chatMessages = document.getElementById('chat-messages');
    const typingIndicator = document.getElementById('typing-indicator');
    
    // Function to add a message to the chat
    function addMessage(content, isUser = false) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${isUser ? 'user-message' : 'bot-message'}`;
        
        const messageContent = document.createElement('div');
        messageContent.className = 'message-content';
        
        // Parse markdown for bot messages
        if (!isUser) {
            messageContent.innerHTML = marked.parse(content);
        } else {
            messageContent.textContent = content;
        }
        
        // Add timestamp
        const timeElement = document.createElement('div');
        timeElement.className = 'message-time';
        const now = new Date();
        timeElement.textContent = now.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
        
        messageDiv.appendChild(messageContent);
        messageDiv.appendChild(timeElement);
        chatMessages.appendChild(messageDiv);
        
        // Scroll to bottom
        chatMessages.scrollTop = chatMessages.scrollHeight;
        
        return messageContent; // Return message content element for streaming updates
    }
    
    // Function to format SQL analysis response
    function formatSQLResponse(response) {
        let formattedContent = '';
        
        // Add SQL query
        if (response.sql_query) {
            formattedContent += "**Generated SQL:**\n```sql\n" + response.sql_query + "\n```\n\n";
        }
        
        // Add analysis
        if (response.analysis) {
            formattedContent += "### Analysis\n" + response.analysis + "\n\n";
        }
        
        // Add suggestions if present
        if (response.suggestions) {
            formattedContent += "### Suggested follow-up queries\n" + response.suggestions + "\n\n";
        }
        
        // Add product recommendations if present
        if (response.product_recommendations) {
            formattedContent += "### Product Recommendations\n" + response.product_recommendations;
        }
        
        return formattedContent;
    }
    
    // Show typing indicator
    function showTypingIndicator() {
        typingIndicator.style.display = 'block';
    }
    
    // Hide typing indicator
    function hideTypingIndicator() {
        typingIndicator.style.display = 'none';
    }
    
    // Submit handler
    chatForm.addEventListener('submit', function(e) {
        e.preventDefault();
        
        const message = userInput.value.trim();
        if (!message) return;
        
        // Add user message to chat
        addMessage(message, true);
        
        // Clear input
        userInput.value = '';
        
        // Show typing indicator
        showTypingIndicator();
        
        // Create a placeholder for bot's response
        const botMessageContent = addMessage('', false);
        
        // Send message to API with streaming
        fetch('/api/chat', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ message: message })
        })
        .then(response => {
            // Hide typing indicator
            hideTypingIndicator();
            
            // Check if response is ok
            if (!response.ok) {
                throw new Error(`Server responded with ${response.status}: ${response.statusText}`);
            }
            
            // Get reader from response body stream
            const reader = response.body.getReader();
            const decoder = new TextDecoder();
            let receivedText = '';
            
            // Function to read stream
            function readStream() {
                return reader.read().then(({ done, value }) => {
                    if (done) {
                        return;
                    }
                    
                    // Decode the chunk
                    const chunk = decoder.decode(value, { stream: true });
                    receivedText += chunk;
                    
                    // Update bot message with current accumulated text
                    botMessageContent.innerHTML = marked.parse(receivedText);
                    
                    // Scroll to bottom
                    chatMessages.scrollTop = chatMessages.scrollHeight;
                    
                    // Continue reading
                    return readStream();
                });
            }
            
            // Start reading the stream
            return readStream();
        })
        .catch(error => {
            hideTypingIndicator();
            console.error('Error:', error);
            
            // Update the message with error
            botMessageContent.innerHTML = marked.parse("⚠️ **Error:** " + error.message);
        });
    });
    
    // Function to set a query example
    window.setQuery = function(query) {
        userInput.value = query;
        userInput.focus();
    };
}); 