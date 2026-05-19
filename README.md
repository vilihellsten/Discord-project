# Discord-bot (Still a work in process)

A Discord bot written in Python that provides three main capabilities:
- Play music from YouTube in voice channels
- Track Steam application updates and post them to a designated channel
- Answer user questions using Gemini AI

## Architecture

The bot is built with `discord.py` and uses a cog-based architecture.

- `main.py` - Bot entrypoint and core command/event handlers
- `src/Cogs/music.py` - Music playback commands and interactive controls
- `src/Cogs/steam_updates.py` - Steam update tracking and scheduled update checks
- `src/Cogs/gemini.py` - Gemini command scaffold (not currently loaded from `main.py`)
- `src/Data/bot_text_file.py` - Help text, Steam instructions, and 8-ball responses
- `src/Data/steamapps.json` - Steam AppID lookup data
- `src/Data/tracked_games.json` - Persistent tracked Steam games

## Features

### Core commands in `main.py`
- `!help` - Displays available bot commands
- `!hello` - Greets the user
- `!poll <question>` - Creates a simple thumbs-up/thumbs-down poll
- `!8ball <question>` - Returns a magic 8-ball style answer
- `!steamupdates` - Displays instructions for using Steam tracking features

### Music Cog (`src/Cogs/music.py`)
- `!join` - Bot joins the user’s current voice channel
- `!play <url or search term>` - Plays music from a YouTube URL or search query
- `!leave` - Disconnects the bot from voice channel
- `!stop` - Stops playback and clears the queue
- `!skip` - Skips the current song when a queue exists
- Visual controls - Buttons for `Stop` and `Skip` are shown in the now-playing embed

The music system uses `yt-dlp` to resolve YouTube audio and `FFmpegOpusAudio` for voice playback.

### Steam Updates Cog (`src/Cogs/steam_updates.py`)
- `!add <AppID>` - Begin tracking Steam updates for a game
- `!list` - Show currently tracked games
- `!remove <number>` - Remove a tracked app by its list index
- `!check <appname>` - Trigger a manual check for a specific tracked app

The cog also runs a background task every 60 minutes to check for new Steam announcements and post updates to a channel named `steam-updates`.

### Gemini AI Integration
- Gemini is used in `main.py` with the `gemini-2.5-flash-lite` model.
- The bot expects `GEMINI_API_KEY` in environment variables.
- `!ask <question>` - Sends a prompt to Gemini AI and replies with the result

## Data Files

- `src/Data/bot_text_file.py` - Holds bot response text, help content, and Steam tracking instructions
- `src/Data/steamapps.json` - Local Steam app database used to resolve game names from AppIDs
- `src/Data/tracked_games.json` - Stores currently tracked games and latest update IDs for persistence

## Dependencies

Python dependencies are listed in `requirements.txt`:
- `discord.py==2.6.3`
- `yt-dlp==2025.9.26`
- `python-dotenv==1.1.1`
- `aiohttp==3.12.15`
- `google` package for Gemini API integration

The project also includes a `package.json` with a Node dependency on `dotenv`, but the bot is primarily a Python application.

## Setup

1. Create a `.env` file in the project root with:
   ```text
   DISCORD_TOKEN=your_discord_bot_token
   GEMINI_API_KEY=your_gemini_api_key
   ```
2. Install Python dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Start the bot:
   ```bash
   python main.py
   ```

## Notes

- The Steam updates feature requires a channel named `steam-updates` in Discord.
- The music cog joins the user’s voice channel and supports queueing additional songs.
- `src/Cogs/gemini.py` is present but not currently loaded by `main.py`.
- Logging is written to `discord.log`.
