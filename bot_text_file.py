# TODO update this file with detailed steam-updates instructions
help_text = """ 
    !hello - Greet the bot
    !poll <question> - Create a poll with the given question
    !help - Show this help message
    !join - Bot joins your voice channel
    !play <url or search term> - Play audio from a youtube URL or search term
    !stop - Stop the current audio
    !leave - Bot leaves the voice channel
    !ask <question> - Ask a question to the AI
    !check <app name> - Check for the latest update of a specific Steam app
    !8ball <question> - Ask the magic 8-ball a question
    !steamupdates - Instructions for using the steam tracking feature
    """

steamupdates_instructions = """
**Steam Update Tracking Instructions:** 
   Discord must have a channel called `steam-updates` where the bot has permission to post updates. 
1. **Add a Game to Track:**
   Use the command `!add <AppID>` to start tracking a game. 
   - Example: `!add 730 `
   - You can find the AppID on the game's Steam store page URL (e.g., for Counter-Strike 2, it's 730).
2. **View Tracked Games:**
   Use the command `!list` to see a list of all games currently being tracked.
3. **Remove a Game from Tracking:**
   Use the command `!remove <number>` to stop tracking a game.
   - Example: `!remove <number>` (where `<number>` is the index of the game in the tracked list shown by `!list`).
   """

responses = [
        "It is certain.",
        "It is decidedly so.",
        "Without a doubt.",
        "Yes - definitely.",
        "You may rely on it.",
        "As I see it, yes.",
        "Most likely.",
        "Outlook good.",
        "Yes.",
        "Signs point to yes.",
        "Better not tell you now.",
        "Don't count on it.",
        "My reply is no.",
        "My sources say no.",
        "Outlook not so good.",
        "Very doubtful."
    ]