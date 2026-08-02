# TikTok Trend Music Bot

Telegram bot: https://t.me/toktrends_bot

## Overview

This project is a Telegram bot that finds trending TikTok music tracks and sends them to users as playable audio files, together with source video previews.

## Main Features

- **Trending track search** with `/trends` based on user filters.
- **Flexible search settings** with `/settings`:
  - keywords
  - country/region
  - publish time period
  - sort mode (relevance or likes)
  - number of tracks and videos per track
- **Audio delivery in Telegram**: tracks are downloaded and sent as Telegram audio messages.
- **Source video context**: previews and links to videos where each track is used.
- **Paid subscription access**:
  - `/subscribe` to buy access via Telegram Stars
  - `/mysub` to check subscription status
  - `/refund` for last Stars payment refund flow
- **Admin subscription management**:
  - `/grant` to issue/extend subscription
  - `/revoke` to cancel subscription
  - `/subinfo` to check any user subscription
- **Automatic user data persistence**:
  - saved search settings
  - saved subscription state

## How It Works

1. User configures filters in `/settings`.
2. User activates subscription in `/subscribe`.
3. User runs `/trends`.
4. Bot collects trending tracks from TikTok API, downloads audio, and sends results to Telegram.
