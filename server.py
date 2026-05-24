import asyncio
import websockets
import json

players = {}  # name -> state


async def broadcast():
    """Send full world state to all clients"""
    if not connected:
        return

    msg = json.dumps({
        "type": "state",
        "data": players
    })

    await asyncio.gather(*[
        ws.send(msg) for ws in connected
    ])


connected = set()


async def handler(ws):
    connected.add(ws)
    player_name = None

    try:
        async for message in ws:
            data = json.loads(message)

            msg_type = data.get("type")
            player_name = data.get("player", player_name)

            # JOIN
            if msg_type == "join":
                players[player_name] = {
                    "x": 0,
                    "y": 0,
                    "hp": 10
                }

            # ACTION
            elif msg_type == "action":
                if player_name not in players:
                    continue

                action = data.get("data", {})

                if action.get("move") == "up":
                    players[player_name]["y"] -= 1
                if action.get("move") == "down":
                    players[player_name]["y"] += 1
                if action.get("move") == "left":
                    players[player_name]["x"] -= 1
                if action.get("move") == "right":
                    players[player_name]["x"] += 1

            # CHAT
            elif msg_type == "chat":
                msg = json.dumps({
                    "type": "chat",
                    "player": player_name,
                    "data": data.get("data")
                })

                await asyncio.gather(*[
                    ws.send(msg) for ws in connected
                ])

            await broadcast()

    finally:
        connected.remove(ws)
        if player_name in players:
            del players[player_name]


async def main():
    print("WebSocket server running on port 8765")
    async with websockets.serve(handler, "0.0.0.0", 8765):
        await asyncio.Future()


asyncio.run(main())
