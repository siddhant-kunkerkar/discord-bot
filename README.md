# Personal Discord Bot

A personal Discord bot originally created in 2021 while learning Python and Discord bot development.

The project started as a learning sandbox for experimenting with Python, Discord APIs, bot commands, and game mechanics. Over time, it evolved into a collection of utilities, automation tools, mini-games, and personal productivity features, including AI-powered expense tracking and Google Sheets automation.

## Features

- Basic server moderation
- Expense logging to Google Sheets
- Engineering calculators for college assignments
- Virtual currency system
- Mini games
- Utility commands

## Commands

### Expense Tracking

#### /expense-log

Process a receipt image and log it to a Google Sheets file.

**Features**

- Expense type categorization
- Payment method identification and categorization
- Google Sheets integration
- Multi-item receipt support

#### /setup enable

Enable expense tracking commands in the current channel.

#### /setup disable

Disable expense tracking commands in the current channel.

### Calculator Utilities

#### get interpolate

Calculate a linearly interpolated value between two known points.

**Aliases**

```text
get interpolate
get inpolate
get ip
```

**Example**

```text
get ip 10 100 20 200 15
```

#### get rseries

Generate a Renard-style geometric series between a lower and upper limit.

**Example**

```text
get rseries R10 1 100
```

### Economy System

#### get grind

Earn a random amount of virtual currency.

**Alias**

```text
get search
```

#### get beg

Fun economy-style command inspired by Dank Memer.

#### get gamble

Gamble virtual currency against the bot.

**Aliases**

```text
get gamble
get diceroll
get bet
get roll
```

#### get bal

Display your current virtual currency balance.

**Alias**

```text
get cred
```

#### get pay

Transfer virtual currency to another user.

**Aliases**

```text
get share
get give
```

### Games

#### get rps

Play Rock-Paper-Scissors-Lizard-Spock.

**Aliases**

```text
get rspls
get rpsls
```

**Example**

```text
get rps rock
```

### Utility Commands

#### get ping

Check bot latency and response time.

#### get invite

Display the bot invitation link.

**Alias**

```text
get inv
```

#### get clear

Delete messages from a channel.

**Aliases**

```text
get clr
get purge
```

#### get cleardm

Delete recent bot messages from a DM conversation.

## Installation

```bash
pip install -r requirements.txt
```

## Usage

```bash
python main.py
```

## Notes

This project was originally created as a personal learning project while studying Python. Rather than remaining a one-time experiment, it continues to serve as a platform for testing new ideas, learning APIs, building automation workflows, and solving day-to-day problems through software.
