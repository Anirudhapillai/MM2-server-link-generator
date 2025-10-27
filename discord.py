import discord
from discord import app_commands
import os

# --- Configuration ---
# 🚨 SECURE METHOD: Read the token from the environment variable (Discloud Secret)
# The variable is named DISCORD_TOKEN on the Discloud dashboard.
BOT_TOKEN = os.getenv("DISCORD_TOKEN") 

# Check if the token was loaded
if not BOT_TOKEN:
    print("!!! ERROR !!!: DISCORD_TOKEN environment variable not set. Please set it in the Discloud dashboard.")
    exit()

# The main bot setup class
class ServerLinkBot(discord.Client):
    def __init__(self):
        # Intents are necessary to run a bot
        intents = discord.Intents.default()
        super().__init__(intents=intents)
        self.tree = app_commands.CommandTree(self)

    # This runs once when the bot successfully logs in
    async def on_ready(self):
        print(f'Bot logged in as {self.user}!')
        try:
            # Syncs the /server command to Discord. This may take up to an hour globally.
            await self.tree.sync() 
            print("Slash commands synced successfully! Try typing /server in Discord.")
        except Exception as e:
            print(f"Error syncing commands: {e}")

    # This defines the /server command!
    @app_commands.command(
        name="server",
        description="Gives the clickable link to the Murder Mystery 2 private server."
    )
    async def server_command(self, interaction: discord.Interaction):
        # The long text shown to the user
        display_text = "https://www.roblox.com/games/142823291/Murder-Mystery-2?privateServerLinkCode=14645875518154687461580121367692"
        
        # The actual short URL that is clicked (This is the trick!)
        target_url = "https://rbx-url.com/ihyYhu9-"
        
        # Formats the message as a clickable link
        link_message = f"**🎉 Join the MM2 Private Server! 🎉**\n\n**[{display_text}]({target_url})**"
        
        # Send the final message
        await interaction.response.send_message(link_message)

# Starts the bot
bot = ServerLinkBot()
try:
    bot.run(BOT_TOKEN)
except Exception as e:
    # Provides a clear error if the token is wrong
    if "401" in str(e) or "LoginFailure" in str(e):
        print("!!! LOGIN FAILED !!!: Check the DISCORD_TOKEN secret in your Discloud dashboard.")
    else:
        print(f"An unexpected error occurred: {e}")
