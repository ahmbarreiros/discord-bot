# Jacaré Músicas 🐊

Welcome to Jacaré Músicas! This Discord bot allows you to stream audio from YouTube directly into your voice channels. You can play music, control playback, and provide an enjoyable listening experience to your server members.

## Features

- Stream audio from YouTube videos.
- Play, pause, skip, and control the volume of the music.
- Search for songs and add them to the queue.
- Loop and shuffle playback options.
- Support for multiple servers.

## Prerequisites

Before you can run the bot, make sure you have the following prerequisites installed:

- Python 3.11.5 or higher
- Discord Developer Application with a Bot Token
- Wavelink v2.6.3
- Lavalink 3.7.8

## Getting Started

1. Clone this repository to your local machine:
   ```bash
   https://github.com/ahmbarreiros/jacare-musicas-discord-bot.git
   cd jacare-musicas-discord-bot
   ```
   
2. Install requirements:
   ```bash
   pip install requirements.txt
   ```
   
3. Configure YAML file:
   - Create an application.yml file and fill it accordinly to LavaLink instructions:
     - https://github.com/lavalink-devs/Lavalink/blob/master/LavalinkServer/application.yml.example
    
4. Configure the bot:
   - Create a .env file and add your Discord Bot Token and YouTube Data API Key:
   ```makefile
   DISC_TOKEN = YOUR_DISCORD_TOKEN
   WAVELINK_URI = https://localhost
   WAVELINK_PASSWORD = YOUR_WAVELINK_PASSWORD
   ```

5. Start the bot:
   ```bash
   cd src/
   java -jar Lavalink.jar
   python main.py
   ```

6. Invite the bot to your Discord server using the provided OAuth2 URL.
  
7. Use bot commands to start playing music!]

## Bot Commands
  - `$entrar` - enters voice channel
  - `$sair` - leaves voice channel
  - `$musica [song]` - plays music or add it to queue
  - `$playlist [URL]` - adds songs of playlist to queue
  - `$pular [position]` - skips song to a position in queue
  - `$pausar` - pauses song
  - `$voltar` - unpauses song
  - `$parar` - stop song
  - `$loop` - loops song
  - `$fila` - shows next 10 songs of queue
  - `$reiniciar` - restart the song
  - `$retroceder [position]` - go back to one of the last 5 songs played
  - `$ir [hh:mm:ss]` - goes to timestamp of video
  - `$volume [value]` - changes bot's volume from 0 to 200, beware that above 120 it can lose audio quality
  - `$tocando` - shows current video playing
  - `$jacare` - if you feel brave, you can try our playlist!

## Acknowledgments
Special thanks to the Discord.py, Wavelink and Lavalink for their valuable resources and support.

## Contact
If you have any questions or need assistance, feel free to reach out to me at ahmbarreiros.cs@gmail.com

<b>Enjoy!</b>
