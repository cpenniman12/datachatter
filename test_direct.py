import anthropic
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Get API key from environment variable
api_key = os.getenv("ANTHROPIC_API_KEY")

if not api_key:
    print("Error: ANTHROPIC_API_KEY environment variable not set.")
    print("Please create a .env file with ANTHROPIC_API_KEY=your_key")
    exit(1)

print(f"Using API key from environment variable (first 10 chars): {api_key[:10]}...")

try:
    # Initialize Anthropic client
    client = anthropic.Anthropic(api_key=api_key)
    
    # Make a simple API call
    message = client.messages.create(
        model="claude-3-haiku-20240307",  # Using Haiku - smaller model
        max_tokens=100,
        temperature=0,
        messages=[
            {"role": "user", "content": "Hello, Claude! This is a test message."}
        ]
    )
    
    # Print the response
    print("\nSuccess! Claude's response:")
    print(message.content[0].text)
    
except Exception as e:
    print(f"\nError calling Anthropic API: {str(e)}") 