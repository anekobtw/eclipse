from mcstatus import JavaServer

server_address = input("Enter a server ip: ")
server = JavaServer.lookup(server_address)

status = server.status()

if status.players.online > 0:
    print(f"Players online ({status.players.online}/{status.players.max}):")
    print(status.players.sample)
    # for player in status.players.sample:
    #     print(f"- {player.name}")
else:
    print("No players are currently online.")
