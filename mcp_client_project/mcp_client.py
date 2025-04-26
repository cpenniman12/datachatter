import mcp
# Remove the mcp websocket client import
# from mcp.client.websocket import websocket_client
import json
import base64
import asyncio
import ssl
import websockets # Import the websockets library

# Configuration (empty as per instructions)
config = {}
# Encode config in base64
config_b64 = base64.b64encode(json.dumps(config).encode()).decode('utf-8') # Decode to string for URL

# --- IMPORTANT: Replace with your actual API key ---
# smithery_api_key = "your-api-key"
# Using the key provided by the user
smithery_api_key = "d59a955c-bf44-4962-b4f9-26fd3670bc50"

# Create server URL
# Using the specific Smithery server URL from the instructions
# Corrected server name based on GitHub README
# server_name = "@Magic-Sauce/quickchart-mcp-server"
server_name = "@gongrzhe/quickchart-mcp-server"
url = f"wss://server.smithery.ai/{server_name}/ws?config={config_b64}&api_key={smithery_api_key}"

async def main():
    print(f"Attempting to connect to: {url}")

    # Create an SSL context that doesn't verify certificates
    # WARNING: This bypasses security checks. Not recommended for production.
    ssl_context = ssl.create_default_context()
    ssl_context.check_hostname = False
    ssl_context.verify_mode = ssl.CERT_NONE

    try:
        # Use websockets.connect directly with the custom SSL context
        async with websockets.connect(url, ssl=ssl_context) as ws:
            print("WebSocket connection established using websockets library.")
            # Manually create the stream pair for MCP
            # Assuming ws object acts as both reader and writer for MCP
            streams = (ws, ws)
            async with mcp.ClientSession(*streams) as session:
                print("MCP ClientSession created.")
                # Initialize the connection
                print("Initializing MCP session...")
                await session.initialize()
                print("MCP session initialized.")

                # List available tools
                print("Listing available tools...")
                tools_result = await session.list_tools()
                print(f"Successfully listed tools.")

                if tools_result.tools:
                    tool_names = [t.name for t in tools_result.tools]
                    print(f"Available tools: {', '.join(tool_names)}")
                else:
                    print("No tools found on the server.")

                # Example of calling a tool (commented out):
                # print("Attempting to call a tool (example)...")
                # try:
                #     # Replace 'tool-name' and arguments as needed based on listed tools
                #     result = await session.call_tool("tool-name", arguments={"arg1": "value"})
                #     print(f"Tool call result: {result}")
                # except Exception as tool_error:
                #     print(f"Error calling tool: {tool_error}")

    except websockets.exceptions.InvalidStatusCode as e:
        print(f"WebSocket connection failed with status code: {e.status_code}")
        print(f"Headers: {e.headers}")
    except Exception as e:
        print(f"An error occurred: {e}")
        import traceback
        traceback.print_exc() # Print detailed traceback for other errors

if __name__ == "__main__":
    # It's good practice to check if an event loop is already running
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:  # No running event loop
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

    loop.run_until_complete(main())
    # Clean up the loop if we created it
    if not asyncio.get_event_loop().is_running():
        loop.close()

print("Script finished.") # Added to see when the script ends 