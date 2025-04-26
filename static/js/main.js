// Visualization Modal Functions
function openVisualizationModal() {
    document.querySelector('.chart-modal').style.display = 'block';
    document.querySelector('.loading-indicator').style.display = 'block';
    document.getElementById('chart-content').style.display = 'none';
}

function closeVisualizationModal() {
    document.querySelector('.chart-modal').style.display = 'none';
    // Clear the chart content when closing
    document.getElementById('chart-content').innerHTML = '';
}

function createVisualization(data) {
    console.warn("createVisualization is deprecated - all visualizations are now handled by Claude");
    // Redirect to visualizeData function which uses Claude
    document.querySelector('.loading-indicator').style.display = 'none';
    document.getElementById('chart-content').style.display = 'block';
    document.getElementById('chart-content').innerHTML = '<div class="redirecting-message">Redirecting to Claude visualization...</div>';
    
    // Convert data if needed
    const processedData = typeof data === 'string' ? JSON.parse(data) : data;
    
    // Use the Claude-powered visualization
    setTimeout(() => visualizeData(Array.isArray(processedData) ? processedData : [processedData]), 500);
}

function createBarChart(canvas, data) {
    console.warn("createBarChart is deprecated - all visualizations are now handled by Claude");
}

function createLineChart(canvas, data) {
    console.warn("createLineChart is deprecated - all visualizations are now handled by Claude");
}

function createPieChart(canvas, data) {
    console.warn("createPieChart is deprecated - all visualizations are now handled by Claude");
}

// Event listeners for modal interactions
document.addEventListener('DOMContentLoaded', function() {
    // Get DOM elements
    const chatMessages = document.getElementById('chat-messages');
    const queryForm = document.getElementById('query-form');
    const questionInput = document.getElementById('question');
    const chartModal = document.getElementById('chart-modal');
    const closeBtn = document.querySelector('.close-btn');
    const loadingSpinner = document.querySelector('.loading-spinner');

    // Initialize event listeners
    if (queryForm) {
        queryForm.addEventListener('submit', handleFormSubmit);
    }

    if (closeBtn) {
        closeBtn.addEventListener('click', function() {
            chartModal.style.display = 'none';
        });
    }

    // Close modal when clicking outside the content
    window.addEventListener('click', function(event) {
        if (event.target === chartModal) {
            chartModal.style.display = 'none';
        }
    });

    // Handle form submission
    async function handleFormSubmit(e) {
        e.preventDefault();
        
        const question = questionInput.value.trim();
        
        if (!question) {
            alert('Please enter a question');
            return;
        }
        
        // Add user message to chat
        addMessage(question, 'user');
        
        // Add "thinking" indicator
        const thinkingIndicator = addThinkingIndicator();
        
        // Clear input
        questionInput.value = '';
        
        try {
            const response = await fetch('/query', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    question: question
                }),
            });
            
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            
            const data = await response.json();
            
            // Remove thinking indicator
            thinkingIndicator.remove();
            
            // Display response
            displayResponse(data);
            
            // Scroll to bottom of chat
            scrollToBottom();
            
        } catch (error) {
            console.error('Error:', error);
            
            // Remove thinking indicator
            thinkingIndicator.remove();
            
            // Add error message
            addMessage('Sorry, there was an error processing your request. Please try again.', 'bot');
        }
    }
    
    // Add message to chat
    function addMessage(text, type) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${type}-message`;
        
        const messageContent = document.createElement('div');
        messageContent.className = 'message-content';
        
        // If message contains newlines, create multiple paragraphs
        if (text.includes('\n')) {
            const paragraphs = text.split('\n').filter(p => p.trim() !== '');
            paragraphs.forEach(paragraph => {
                const p = document.createElement('p');
                p.textContent = paragraph;
                messageContent.appendChild(p);
            });
        } else {
            const messageParagraph = document.createElement('p');
            messageParagraph.textContent = text;
            messageContent.appendChild(messageParagraph);
        }
        
        messageDiv.appendChild(messageContent);
        chatMessages.appendChild(messageDiv);
        
        scrollToBottom();
        return messageDiv;
    }
    
    // Add thinking indicator
    function addThinkingIndicator() {
        const thinkingDiv = document.createElement('div');
        thinkingDiv.className = 'message bot-message thinking';
        thinkingDiv.innerHTML = `
            <span></span>
            <span></span>
            <span></span>
        `;
        chatMessages.appendChild(thinkingDiv);
        scrollToBottom();
        return thinkingDiv;
    }
    
    // Scroll to bottom of chat
    function scrollToBottom() {
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }
    
    // Display response from the server
    function displayResponse(data) {
        // Handle text message responses or error messages
        if (data.message) {
            // Check if it's an error message
            if (data.has_error || data.no_sql) {
                // Add error message with different styling
                const errorDiv = document.createElement('div');
                errorDiv.className = 'message bot-message error-message';
                
                const errorContent = document.createElement('div');
                errorContent.className = 'message-content';
                
                const errorParagraph = document.createElement('p');
                errorParagraph.textContent = data.message;
                errorParagraph.style.color = '#d32f2f';
                
                errorContent.appendChild(errorParagraph);
                errorDiv.appendChild(errorContent);
                chatMessages.appendChild(errorDiv);
            } else {
                // Regular message
                addMessage(data.message, 'bot');
            }
            
            scrollToBottom();
            return;
        }
        
        // Always show the SQL query if available
        if (data.sql_query) {
            // Add SQL code message
            const sqlDiv = document.createElement('div');
            sqlDiv.className = 'message bot-message sql-message';
            
            const sqlContent = document.createElement('div');
            sqlContent.className = 'message-content';
            
            const sqlPre = document.createElement('pre');
            sqlPre.textContent = data.sql_query;
            
            sqlContent.appendChild(sqlPre);
            sqlDiv.appendChild(sqlContent);
            chatMessages.appendChild(sqlDiv);
        }
        
        // Handle empty results specifically
        if (data.empty_results) {
            const emptyDiv = document.createElement('div');
            emptyDiv.className = 'message bot-message';
            
            const emptyContent = document.createElement('div');
            emptyContent.className = 'message-content';
            
            const emptyParagraph = document.createElement('p');
            emptyParagraph.innerHTML = '<i class="fas fa-info-circle"></i> The query executed successfully but returned no results.';
            emptyParagraph.style.color = '#ff9800';
            
            emptyContent.appendChild(emptyParagraph);
            emptyDiv.appendChild(emptyContent);
            chatMessages.appendChild(emptyDiv);
            
            scrollToBottom();
            return;
        }
        
        // Add results message if we have results
        if (data.results && Array.isArray(data.results) && data.results.length > 0) {
            // Create results message
            const resultsDiv = document.createElement('div');
            resultsDiv.className = 'message bot-message results-message';
            
            const resultsContent = document.createElement('div');
            resultsContent.className = 'message-content';
            
            // Add results header
            const resultsHeader = document.createElement('div');
            resultsHeader.className = 'results-header';
            resultsHeader.textContent = `Query Results (${data.results.length} rows)`;
            resultsContent.appendChild(resultsHeader);
            
            // Add results body
            const resultsBody = document.createElement('div');
            resultsBody.className = 'results-body';
            
            // Create table container
            const tableContainer = document.createElement('div');
            tableContainer.className = 'table-container';
            
            // Create table
            const table = createTableFromData(data.results);
            tableContainer.appendChild(table);
            resultsBody.appendChild(tableContainer);
            
            // Add visualization button if data is visualizable
            if (canVisualize(data.results)) {
                const visualizeBtn = document.createElement('button');
                visualizeBtn.className = 'visualize-btn';
                visualizeBtn.innerHTML = '<i class="fas fa-chart-bar"></i> Visualize Data';
                
                // Add a pulse animation to draw attention
                visualizeBtn.style.animation = 'pulse 2s infinite';
                
                // Add CSS for the pulse animation if not already in the stylesheet
                if (!document.getElementById('pulse-animation-style')) {
                    const style = document.createElement('style');
                    style.id = 'pulse-animation-style';
                    style.textContent = `
                        @keyframes pulse {
                            0% { box-shadow: 0 0 0 0 rgba(76, 175, 80, 0.4); }
                            70% { box-shadow: 0 0 0 10px rgba(76, 175, 80, 0); }
                            100% { box-shadow: 0 0 0 0 rgba(76, 175, 80, 0); }
                        }
                    `;
                    document.head.appendChild(style);
                }
                
                // Enhanced click event with animation and logging
                visualizeBtn.addEventListener('click', function() {
                    console.log("Visualize button clicked");
                    // Remove pulse animation when clicked
                    this.style.animation = 'none';
                    // Add a small visual feedback
                    this.classList.add('clicked');
                    // Call the visualization function
                    visualizeData(data.results);
                });
                
                // Add button in a prominent container
                const buttonContainer = document.createElement('div');
                buttonContainer.className = 'button-container';
                buttonContainer.style.textAlign = 'center';
                buttonContainer.style.width = '100%';
                buttonContainer.style.marginTop = '15px';
                buttonContainer.appendChild(visualizeBtn);
                
                resultsBody.appendChild(buttonContainer);
                
                // Log that the button was added
                console.log("Visualization button added to results");
            } else {
                console.log("Data cannot be visualized:", data.results);
            }
            
            resultsContent.appendChild(resultsBody);
            resultsDiv.appendChild(resultsContent);
            chatMessages.appendChild(resultsDiv);
        } else if (!data.has_error && !data.empty_results) {
            // No results but not due to an error or empty results
            addMessage('No data was returned for this query.', 'bot');
        }
        
        // Scroll to bottom after adding all content
        scrollToBottom();
    }
    
    // Create table from data
    function createTableFromData(data) {
        const table = document.createElement('table');
        const thead = document.createElement('thead');
        const tbody = document.createElement('tbody');
        
        // Create table header
        const headerRow = document.createElement('tr');
        const columns = Object.keys(data[0]);
        
        columns.forEach(column => {
            const th = document.createElement('th');
            th.textContent = column;
            headerRow.appendChild(th);
        });
        
        thead.appendChild(headerRow);
        table.appendChild(thead);
        
        // Create table rows (limit to 10 rows for display in chat)
        const displayLimit = Math.min(data.length, 10);
        
        for (let i = 0; i < displayLimit; i++) {
            const row = document.createElement('tr');
            
            columns.forEach(column => {
                const td = document.createElement('td');
                const value = data[i][column];
                
                // Format value based on type
                if (value === null) {
                    td.textContent = 'NULL';
                    td.style.color = '#999';
                } else if (typeof value === 'number') {
                    td.textContent = formatNumber(value);
                } else {
                    td.textContent = value;
                }
                
                row.appendChild(td);
            });
            
            tbody.appendChild(row);
        }
        
        table.appendChild(tbody);
        
        // Add limited data note if needed
        if (data.length > displayLimit) {
            const note = document.createElement('caption');
            note.style.captionSide = 'bottom';
            note.textContent = `Showing ${displayLimit} of ${data.length} rows.`;
            table.appendChild(note);
        }
        
        return table;
    }

    // Check if data can be visualized
    function canVisualize(data) {
        if (!data || !Array.isArray(data) || data.length < 1) {
            console.log("Not enough data points for visualization");
            return false;
        }
        
        // Ensure data contains objects
        if (typeof data[0] !== 'object' || data[0] === null) {
            console.log("Data is not in correct format for visualization");
            return false;
        }
        
        // Check if there are numeric columns for visualization
        const firstRow = data[0];
        const columns = Object.keys(firstRow);
        
        if (columns.length === 0) {
            console.log("No columns found in data");
            return false;
        }
        
        // Check for SQL results with meaningful column names
        const hasNameColumn = columns.some(col => 
            col.toLowerCase().includes('name') || 
            col.toLowerCase().includes('ticker') ||
            col.toLowerCase().includes('company') ||
            col.toLowerCase().includes('category')
        );

        const hasValueColumn = columns.some(col => 
            col.toLowerCase().includes('value') || 
            col.toLowerCase().includes('income') || 
            col.toLowerCase().includes('price') ||
            col.toLowerCase().includes('revenue') ||
            col.toLowerCase().includes('sales') ||
            col.toLowerCase().includes('profit') ||
            col.toLowerCase().includes('amount') ||
            col.toLowerCase().includes('quantity') ||
            typeof firstRow[col] === 'number'
        );
        
        // Check if we have structured data suitable for visualization
        if (hasNameColumn && hasValueColumn) {
            console.log("SQL data can be visualized with category and value columns");
            return true;
        }
        
        // For the purposes of this app, always consider data as visualizable
        // if it has at least one row with numeric values
        // Checking for numeric columns
        const hasNumericColumn = columns.some(column => {
            // Check for numeric values in the data
            return data.some(row => {
                const value = row[column];
                return (
                    typeof value === 'number' || 
                    (typeof value === 'string' && !isNaN(parseFloat(value)) && 
                    value.trim() !== '')
                );
            });
        });
        
        console.log("Data can be visualized:", hasNumericColumn);
        return hasNumericColumn;
    }

    // Format number for display
    function formatNumber(num) {
        if (Number.isInteger(num)) {
            return num.toLocaleString();
        } else {
            return num.toLocaleString(undefined, {
                minimumFractionDigits: 0,
                maximumFractionDigits: 2
            });
        }
    }

    // Visualize data in a chart
    function visualizeData(data) {
        // Show modal
        const chartModal = document.getElementById('chart-modal');
        const loadingSpinner = document.querySelector('.loading-spinner');
        const chartContainer = document.getElementById('chart-content');
        
        if (!chartModal || !loadingSpinner || !chartContainer) {
            console.error("Required DOM elements for visualization not found");
            alert("Visualization components not found. Please refresh the page and try again.");
            return;
        }
        
        // Clear previous content and show spinner
        chartContainer.innerHTML = '';
        chartModal.style.display = 'block';
        loadingSpinner.style.display = 'block';
        
        // Always use the Claude API for visualizations
        console.log("Sending data for Claude visualization:", data.length, "records");
        
        // Get data to visualize
        fetch('/generate-visualization', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                results: data
            }),
        })
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok: ' + response.status);
            }
            return response.json();
        })
        .then(data => {
            console.log("Visualization response received");
            // Hide loading spinner
            loadingSpinner.style.display = 'none';
            
            // Use DOMParser to handle the incoming HTML string
            const parser = new DOMParser();
            const doc = parser.parseFromString(data.visualization_html, 'text/html');
            
            // Clear previous content
            chartContainer.innerHTML = ''; 

            // Append non-script elements from the parsed body
            Array.from(doc.body.childNodes).forEach(node => {
                if (node.nodeName !== 'SCRIPT') {
                    chartContainer.appendChild(node.cloneNode(true)); // Append HTML elements
                }
            });

            // Find and execute script elements separately
            const scripts = Array.from(doc.querySelectorAll('script'));
            scripts.forEach(script => {
                const newScript = document.createElement('script');
                // Copy attributes like src
                Array.from(script.attributes).forEach(attr => newScript.setAttribute(attr.name, attr.value));
                // Copy inline content
                if (script.textContent) {
                    newScript.textContent = script.textContent;
                }
                // Append the new script to the container to execute it in context
                chartContainer.appendChild(newScript); 
            });
        })
        .catch(error => {
            console.error('Error generating visualization:', error);
            loadingSpinner.style.display = 'none';
            chartContainer.innerHTML = `
                <div class="error-message">
                    <p>Error generating visualization: ${error.message}</p>
                    <p>Please try again or use a different dataset.</p>
                </div>
            `;
        });
    }
});

// Add event listeners for schema sidebar toggle
document.addEventListener('DOMContentLoaded', (event) => {
    const toggleButton = document.getElementById('toggle-schema-btn');
    const closeButton = document.getElementById('close-schema-btn');
    const sidebar = document.getElementById('schema-sidebar');
    const body = document.body;

    if (toggleButton && sidebar) {
        toggleButton.addEventListener('click', () => {
            sidebar.classList.toggle('open');
            body.classList.toggle('schema-open'); // Optional class for body adjustments
        });
    }

    if (closeButton && sidebar) {
        closeButton.addEventListener('click', () => {
            sidebar.classList.remove('open');
            body.classList.remove('schema-open');
        });
    }
    
    // Optional: Close sidebar if clicking outside of it
    document.addEventListener('click', (event) => {
        if (sidebar && sidebar.classList.contains('open')) {
            const isClickInsideSidebar = sidebar.contains(event.target);
            const isClickOnToggleButton = toggleButton ? toggleButton.contains(event.target) : false;
            
            if (!isClickInsideSidebar && !isClickOnToggleButton) {
                sidebar.classList.remove('open');
                body.classList.remove('schema-open');
            }
        }
    });
}); 