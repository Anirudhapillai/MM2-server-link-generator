import discord
from discord import app_commands
from discord.ext import commands
import os
import asyncio
import http.server
import socketserver
import threading

# --- Configuration ---
# SECURE METHOD: Read the token from the environment variable (GitHub Secret)
# The variable name is DISCORD_TOKEN
BOT_TOKEN = os.getenv("DISCORD_TOKEN")

# Check if the token was loaded
if not BOT_TOKEN:
    print("!!! ERROR !!!: DISCORD_TOKEN environment variable not set. Please set it in the GitHub repository secrets.")
    exit(1)

# --- Web Server Setup ---
# This simple server prevents GitHub Actions from terminating the script.
PORT = 8080 # GitHub Actions runners can usually use any high port
Handler = http.server.SimpleHTTPRequestHandler

def run_server():
    try:
        with socketserver.TCPServer(("", PORT), Handler) as httpd:
            print(f"[SERVER] Serving HTTP on port {PORT} to keep the runner alive...")
            # Serve forever until the script is manually terminated or the action timeout occurs (6 hours)
            httpd.serve_forever()
    except Exception as e:
        print(f"[SERVER] Error running HTTP server: {e}")

# Start the web server in a separate thread
# The thread must be a daemon so it exits when the main thread (the bot) exits
server_thread = threading.Thread(target=run_server, daemon=True)
server_thread.start()

# --- Bot Setup ---
# Intents are necessary to run a bot
intents = discord.Intents.default()
bot = commands.Bot(command_prefix='!', intents=intents)

# This runs once when the bot successfully logs in
@bot.event
async def on_ready():
    print(f"Bot logged in as {bot.user}!")
    
    # Syncs the /server command to Discord. This may take up to an hour globally.
    try:
        synced = await bot.tree.sync()
        print(f"[LOG] Synced {len(synced)} slash commands successfully! Try typing /server in Discord.")
    except Exception as e:
        print(f"Error syncing commands: {e}")

# This defines the /server command!
@bot.tree.command(name="server", description="Gives the clickable link to the Murder Mystery 2 private server.")
async def server_command(interaction: discord.Interaction):
    # The long text shown to the user
    # NOTE: This link is a placeholder. You must update this with your actual private server link.
    display_text = "https://www.roblox.com/games/142823291/Murder-Mystery-2?PrivateServerLinkCode=14645875518154687461580121367692"

    await interaction.response.send_message(
        f"**Here is your current MM2 Private Server Link:**\n\n{display_text}",
        ephemeral=True # Makes the reply only visible to the user who typed the command
    )

# --- Final Execution ---
# Now run the bot using the token
try:
    bot.run(BOT_TOKEN)
except discord.errors.LoginFailure:
    print("!!! FATAL ERROR !!!: The bot token provided is invalid or incorrect. Please check your DISCORD_TOKEN secret.")
    # Exit gracefully if login fails
    exit(1)
