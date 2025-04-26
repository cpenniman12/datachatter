document.addEventListener('DOMContentLoaded', function() {
    const chatMessages = document.getElementById('chat-messages');
    const userInput = document.getElementById('user-input');
    const sendButton = document.getElementById('send-button');
    const exampleQueries = document.querySelectorAll('.example-query');

    // Create a typing indicator element
    const typingIndicator = document.createElement('div');
    typingIndicator.className = 'typing-indicator';
    typingIndicator.innerHTML = '<span></span><span></span><span></span>';
    
    // Function to add a new message to the chat
    function addMessage(text, sender) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${sender}`;
        
        const contentDiv = document.createElement('div');
        contentDiv.className = 'message-content';
        
        // Process the message content
        if (sender === 'bot' && text.includes('<sql>')) {
            // Special handling for responses with SQL
            const parts = text.split(/<\/?sql>/);
            
            if (parts.length >= 3) {
                // Add any text before the SQL
                if (parts[0].trim()) {
                    const textPara = document.createElement('p');
                    textPara.textContent = parts[0].trim();
                    contentDiv.appendChild(textPara);
                }
                
                // Add the SQL code block
                const sqlDiv = document.createElement('div');
                sqlDiv.className = 'sql-query';
                sqlDiv.textContent = parts[1].trim();
                contentDiv.appendChild(sqlDiv);
                
                // Add any text after the SQL
                if (parts[2].trim()) {
                    const afterPara = document.createElement('p');
                    afterPara.textContent = parts[2].trim();
                    contentDiv.appendChild(afterPara);
                }
            } else {
                // Fallback if the parsing fails
                const textPara = document.createElement('p');
                textPara.textContent = text;
                contentDiv.appendChild(textPara);
            }
        } else {
            // Regular text message
            const textPara = document.createElement('p');
            textPara.textContent = text;
            contentDiv.appendChild(textPara);
        }
        
        messageDiv.appendChild(contentDiv);
        chatMessages.appendChild(messageDiv);
        
        // Scroll to the bottom of the chat
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }
    
    // Function to handle sending messages
    function sendMessage() {
        const message = userInput.value.trim();
        if (message) {
            // Add user message to chat
            addMessage(message, 'user');
            
            // Clear input
            userInput.value = '';
            
            // Show typing indicator
            showTypingIndicator();
            
            // Send message to backend
            fetch('/query', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ question: message }),
            })
            .then(response => {
                if (!response.ok) {
                    throw new Error('Network response was not ok');
                }
                return response.json();
            })
            .then(data => {
                // Hide typing indicator
                hideTypingIndicator();
                
                // Process the response
                if (data.sql_query && data.results) {
                    // Response with SQL and results
                    const sqlMessage = `I've translated your question into SQL:\n<sql>${data.sql_query}</sql>`;
                    addMessage(sqlMessage, 'bot');
                    
                    // Show results in a structured way
                    showQueryResults(data.results);
                } else if (data.message) {
                    // Simple text response
                    addMessage(data.message, 'bot');
                } else {
                    // Fallback for unexpected response format
                    addMessage("I received your message but couldn't generate a proper response.", 'bot');
                }
            })
            .catch(error => {
                console.error('Error:', error);
                hideTypingIndicator();
                addMessage("Sorry, there was an error processing your request.", 'bot');
            });
        }
    }
    
    // Function to show typing indicator
    function showTypingIndicator() {
        const indicatorDiv = document.createElement('div');
        indicatorDiv.className = 'message bot';
        indicatorDiv.id = 'typing-indicator-message';
        indicatorDiv.appendChild(typingIndicator.cloneNode(true));
        chatMessages.appendChild(indicatorDiv);
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }
    
    // Function to hide typing indicator
    function hideTypingIndicator() {
        const indicator = document.getElementById('typing-indicator-message');
        if (indicator) {
            indicator.remove();
        }
    }
    
    // Function to display query results
    function showQueryResults(results) {
        if (!Array.isArray(results) || results.length === 0) {
            addMessage("The query returned no results.", 'bot');
            return;
        }
        
        // Create message container
        const messageDiv = document.createElement('div');
        messageDiv.className = 'message bot';
        
        const contentDiv = document.createElement('div');
        contentDiv.className = 'message-content';
        
        // Add results heading
        const heading = document.createElement('p');
        heading.className = 'results-heading';
        heading.textContent = `Found ${results.length} results:`;
        contentDiv.appendChild(heading);
        
        // Create table wrapper for scrolling
        const tableWrapper = document.createElement('div');
        tableWrapper.style.overflowX = 'auto';
        tableWrapper.style.maxWidth = '100%';
        tableWrapper.style.marginBottom = '10px';
        
        // Create table for results
        const table = document.createElement('table');
        table.className = 'result-table';
        
        // Table header
        const thead = document.createElement('thead');
        const headerRow = document.createElement('tr');
        
        // Get column names from first result
        const columns = Object.keys(results[0]);
        
        columns.forEach(column => {
            const th = document.createElement('th');
            th.textContent = column;
            headerRow.appendChild(th);
        });
        
        thead.appendChild(headerRow);
        table.appendChild(thead);
        
        // Table body
        const tbody = document.createElement('tbody');
        
        // Add rows (limit to 10 for display)
        const displayResults = results.slice(0, 10);
        
        displayResults.forEach(result => {
            const row = document.createElement('tr');
            
            columns.forEach(column => {
                const td = document.createElement('td');
                // Format numbers nicely
                if (typeof result[column] === 'number') {
                    td.textContent = formatNumber(result[column]);
                } else {
                    td.textContent = result[column] !== null ? result[column] : '';
                }
                row.appendChild(td);
            });
            
            tbody.appendChild(row);
        });
        
        table.appendChild(tbody);
        tableWrapper.appendChild(table);
        contentDiv.appendChild(tableWrapper);
        
        // Add note if showing truncated results
        if (results.length > 10) {
            const note = document.createElement('p');
            note.textContent = `Showing 10 of ${results.length} results.`;
            note.style.fontStyle = 'italic';
            note.style.fontSize = '0.8em';
            note.style.opacity = '0.7';
            note.style.marginTop = '8px';
            contentDiv.appendChild(note);
        }
        
        // Add AI visualization button
        const buttonContainer = document.createElement('div');
        buttonContainer.className = 'button-container';
        
        const aiVisualizeBtn = document.createElement('button');
        aiVisualizeBtn.textContent = 'AI Visualize';
        aiVisualizeBtn.className = 'ai-visualize-btn';
        aiVisualizeBtn.innerHTML = '<i class="fas fa-chart-line"></i> AI Visualize';
        aiVisualizeBtn.onclick = function() {
            generateAIVisualization(results);
        };
        buttonContainer.appendChild(aiVisualizeBtn);
        
        contentDiv.appendChild(buttonContainer);
        
        messageDiv.appendChild(contentDiv);
        chatMessages.appendChild(messageDiv);
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }
    
    // Helper function to format numbers nicely
    function formatNumber(num) {
        if (typeof num !== 'number') return num;
        
        // Format with commas for thousands
        if (Number.isInteger(num)) {
            return num.toLocaleString();
        } else {
            // For floating point numbers, limit decimal places
            return num.toLocaleString(undefined, { 
                minimumFractionDigits: 0,
                maximumFractionDigits: 2 
            });
        }
    }
    
    // Function to generate AI visualization
    function generateAIVisualization(results) {
        // Show loading indicator
        const loadingDiv = document.createElement('div');
        loadingDiv.innerHTML = '<div class="loading-spinner"></div><p>AI generating visualization...</p>';
        loadingDiv.className = 'loading-indicator';
        document.body.appendChild(loadingDiv);
        
        // Send request to the server
        fetch('/generate-visualization', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                results: results
            }),
        })
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            return response.json();
        })
        .then(data => {
            // Remove loading indicator
            document.body.removeChild(loadingDiv);
            
            // Create modal for the visualization
            const modal = document.createElement('div');
            modal.className = 'chart-modal';
            
            const modalContent = document.createElement('div');
            modalContent.className = 'chart-modal-content';
            
            // Add close button
            const closeBtn = document.createElement('span');
            closeBtn.className = 'close-btn';
            closeBtn.innerHTML = '&times;';
            closeBtn.onclick = function() {
                document.body.removeChild(modal);
            };
            
            // Create container for visualization
            const visualContainer = document.createElement('div');
            visualContainer.id = 'ai-visualization-container';
            visualContainer.innerHTML = data.visualization_html;
            
            // Add elements to modal
            modalContent.appendChild(closeBtn);
            modalContent.appendChild(visualContainer);
            modal.appendChild(modalContent);
            document.body.appendChild(modal);
            
            // Execute any scripts in the visualization
            const scripts = visualContainer.querySelectorAll('script');
            scripts.forEach(script => {
                const newScript = document.createElement('script');
                if (script.src) {
                    newScript.src = script.src;
                } else {
                    newScript.textContent = script.textContent;
                }
                document.body.appendChild(newScript);
            });
        })
        .catch(error => {
            // Remove loading indicator
            document.body.removeChild(loadingDiv);
            
            console.error('Error generating visualization:', error);
            alert('Error generating visualization. Please try again.');
        });
    }
    
    // Event listeners
    sendButton.addEventListener('click', sendMessage);
    
    userInput.addEventListener('keypress', function(e) {
        if (e.key === 'Enter') {
            sendMessage();
        }
    });
    
    // Focus the input field when the page loads
    userInput.focus();
    
    // Example queries
    exampleQueries.forEach(query => {
        query.addEventListener('click', function(e) {
            e.preventDefault();
            userInput.value = this.textContent.trim();
            sendMessage();
        });
    });

    // Close modal when clicking the close button
    const closeButton = document.querySelector('.close-btn');
    if (closeButton) {
        closeButton.addEventListener('click', hideVisualizationModal);
    }
    
    // Close modal when clicking outside of it
    const chartModal = document.querySelector('.chart-modal');
    if (chartModal) {
        chartModal.addEventListener('click', function(event) {
            if (event.target === chartModal) {
                hideVisualizationModal();
            }
        });
    }
    
    // Add event delegation for visualization buttons that will be added dynamically
    document.addEventListener('click', function(event) {
        if (event.target.classList.contains('visualization-btn')) {
            const queryId = event.target.getAttribute('data-query-id');
            if (queryId) {
                handleVisualizationRequest(queryId);
            }
        }
    });
});

// Visualization Modal Functions
function showVisualizationModal() {
    document.querySelector('.chart-modal').style.display = 'block';
    document.body.style.overflow = 'hidden'; // Prevent scrolling when modal is open
}

function hideVisualizationModal() {
    document.querySelector('.chart-modal').style.display = 'none';
    document.body.style.overflow = '';
}

function showLoadingIndicator() {
    document.querySelector('.loading-indicator').style.display = 'flex';
}

function hideLoadingIndicator() {
    document.querySelector('.loading-indicator').style.display = 'none';
}

// Function to render visualization in the modal
function renderVisualization(data) {
    hideLoadingIndicator();
    const chartContainer = document.getElementById('chart-content');
    
    // Clear previous chart if any
    chartContainer.innerHTML = '';
    
    // Create a canvas for the chart
    const canvas = document.createElement('canvas');
    chartContainer.appendChild(canvas);
    
    // Render chart using Chart.js
    const ctx = canvas.getContext('2d');
    
    // Parse the data to determine chart type
    const chartType = determineChartType(data);
    createChart(ctx, data, chartType);
}

function determineChartType(data) {
    // Logic to determine best chart type based on data structure
    // For simplicity, defaulting to bar chart
    return 'bar';
}

function createChart(ctx, data, chartType) {
    // Sample implementation - replace with actual data processing logic
    const chart = new Chart(ctx, {
        type: chartType,
        data: {
            labels: data.labels || [],
            datasets: data.datasets || []
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                title: {
                    display: true,
                    text: data.title || 'Data Visualization'
                },
                legend: {
                    position: 'top'
                }
            }
        }
    });
}

// Function to handle visualization button click
function handleVisualizationRequest(queryId) {
    showVisualizationModal();
    showLoadingIndicator();
    
    // Make API request to get visualization data
    fetch(`/api/visualize?query_id=${queryId}`)
        .then(response => {
            if (!response.ok) {
                throw new Error('Failed to fetch visualization data');
            }
            return response.json();
        })
        .then(data => {
            renderVisualization(data);
        })
        .catch(error => {
            console.error('Visualization error:', error);
            document.getElementById('chart-content').innerHTML = 
                `<div class="error-message">Failed to generate visualization: ${error.message}</div>`;
            hideLoadingIndicator();
        });
} 