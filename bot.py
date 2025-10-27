import discord
from discord import app_commands
import os
import asyncio
from http.server import BaseHTTPRequestHandler, HTTPServer
import threading

# --- Configuration ---
# SECURE METHOD: Read the token from the environment variable (Render Secret)
BOT_TOKEN = os.getenv("DISCORD_TOKEN")
# Render uses the PORT environment variable to tell you which port to bind to.
WEB_PORT = int(os.environ.get("PORT", 8080))

# Check if the token was loaded
if not BOT_TOKEN:
    print("!!! ERROR !!! DISCORD_TOKEN environment variable not set. Please set it in the Render Environment.")
    exit(1)

# --- Web Server to Keep Render Alive ---
# Render requires a Web Service to bind to a port within 60 seconds.
class HealthCheckHandler(BaseHTTPRequestHandler):
    """A minimal HTTP request handler for the health check endpoint."""
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        self.wfile.write(b"<h1>Discord Bot Running</h1><p>This service is online and running the bot process.</p>")

def start_web_server():
    """Starts the simple web server in a separate thread."""
    try:
        webServer = HTTPServer(("", WEB_PORT), HealthCheckHandler)
        print(f"[SERVER] Started web server on port {WEB_PORT} for Render health check.")
        webServer.serve_forever()
    except Exception as e:
        print(f"[SERVER ERROR] Failed to start web server: {e}")

# --- The main bot setup class ---
class ServerLinkBot(discord.Client):
    def __init__(self):
        # Intents are necessary to run a bot
        intents = discord.Intents.default()
        super().__init__(intents=intents)
        # CommandTree is used for application (slash) commands
        self.tree = app_commands.CommandTree(self)
        
    async def on_ready(self):
        print(f"[BOT] Bot logged in as {self.user}!")
        
        # Start command sync immediately after login
        await self.sync_commands()

    async def sync_commands(self):
        """Syncs slash commands and reports success/failure."""
        try:
            # Syncs the /server command to Discord. This may take up to an hour globally.
            await self.tree.sync()
            print("[LOG] Slash commands synced successfully! Try typing /server in Discord.")
        except Exception as e:
            print(f"[LOG] Error syncing commands: {e}")

    # This defines the /server command!
    @app_commands.command(name="server", description="Gives the clickable link to the Murder Mystery 2 private server.")
    async def server_command(self, interaction: discord.Interaction):
        # The long text shown to the user
        display_text = "https://www.roblox.com/games/142823291/Murder-Mystery-2?PrivateServerLinkCode=14645875518154667461580121367692"
        await interaction.response.send_message(display_text, ephemeral=False) # ephemeral=False means everyone can see it

# --- Main execution block ---
if __name__ == "__main__":
    # Start the web server in a separate thread
    web_server_thread = threading.Thread(target=start_web_server)
    web_server_thread.start()

    # Start the Discord bot
    bot = ServerLinkBot()
    # Use run_forever instead of run() in modern discord.py
    try:
        asyncio.run(bot.start(BOT_TOKEN))
    except KeyboardInterrupt:
        pass # Graceful shutdown not required on Render
