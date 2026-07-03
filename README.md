# Real-Time Server Management Bot

Small chat bot that allows you to manage your personal game server via commands, using concurrent tasks and WebSockets to provide real-time execution and feedback.

> This bot only works with Minecraft servers hosted on a Pterodactyl.

## Architecture

Leverages the discord.py and Pterodactyl APIs to connect the user and server through a command handler and WebSocket manager that route each command to its respective action.

```
Discord (slash commands)
        │
        ▼
  Command Handler ◄─────────────┐
        │                       │
        ▼                       │
  WebSocket Manager ◄────┐      │
        │                │      │
        ▼                │      │
   Pterodactyl Wings ────┘      │
        │                       │
        ├──► Snapshot State ────┘
        │                       │
        ├──► Waiters Dict ──────┘
        │
        └──► Event Queue ───► Event Logger
```

## Design Features

### Data Flow

The server sends back two kinds of information: things that are constantly changing (player count, status) and things that happen occasionally (the server finished starting, the server went offline). To decouple the bot's front end from its back end, it uses a hybrid design pattern to handle each kind differently.

#### Snapshot State

For frequently updated information, the bot stores the current truth in a single-writer snapshot state owned by the WebSocket manager and only read by the command handler without requiring any locks. This skips the process of sending a request to the server and awaiting a response every time a command needs an answer. This is sufficient for state that's read often and doesn't need a response guarantee, like `/status` or `/players`.

#### Event Queue

For infrequent events, the WebSocket manager packages the information into an envelope and sends it into an event queue to be read by any consumers. Currently, the only consumer is the event logger.

#### Waiters Dictionary

Some commands require feedback from infrequent events not stored in the snapshot state. To avoid race conditions, these commands skip the event queue entirely and read from a waiters dictionary keyed by event type instead.

Each server event envelope has a UUID, but this is only for logging purposes. The reason for using event type as the key instead of the UUID is that the Pterodactyl API has no knowledge of it, so the WebSocket manager would have nowhere to route the incoming message back to. Instead, when a new server event arrives, it's packed into an envelope, sent into the event queue, and checked against the waiters dictionary, resolving the future directly without polling or race conditions. Since each command type with a waiter can only be executed once at a time, this solution is suficient.

## Future Plans

#### Multi-Stage Docker Build

The current image bundles build-time dependencies into the runtime image. Splitting the build into two stages to drop those dependencies would reduce image size by an estimated 50%.

#### Tests

Testing is currently manual. Adding tests for the core mechanisms would streamline the development process, catch regressions automatically, and provide more confidence when refactoring.

#### Restart Command

Currently, the only power controls are `/start` and `/stop`. A future `/restart` command will cover this case directly.

#### Whitelist System

Currently, any user in the same Discord server as the bot can obtain the member role via `/join`, but there's no way to add a Minecraft username to the server's whitelist directly. An admin needs to whitelist new players manually through the panel or in-game. Future functionality will let users request access and submit their Minecraft username through the bot, with an admin able to approve or reject the request. Approved requests get whitelisted automatically.

---

> **Note:** This project only supports Minecraft servers hosted with Pterodactyl. There are no current plans to expand to other games or server panels.
