# MEGA File Renamer Telegram Bot

A Telegram bot that renames all files in your MEGA account to sequential names (sam_1, sam_2, etc.)

## Features
- Rename ALL MEGA files sequentially
- Preserve file extensions
- Fast parallel processing
- Progress tracking
- Safe confirmation system

## Commands
- `/start` - Start the bot
- `/rename` - Begin renaming process
- `/status` - Check bot status
- `/help` - Get instructions
- `/cancel` - Cancel operation

## Deployment
### Vercel Deployment
1. Fork this repository
2. Connect to Vercel
3. Set environment variables
4. Deploy

## Environment Variables
- `BOT_TOKEN` - Your Telegram bot token
- `MEGA_EMAIL` - MEGA account email
- `MEGA_PASSWORD` - MEGA account password
- `OWNER_USERNAME` - Bot owner username

## Warning
⚠️ This bot permanently renames ALL files in your MEGA account. Use with caution!
