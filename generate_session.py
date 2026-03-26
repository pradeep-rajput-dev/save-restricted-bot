from pyrogram import Client

api_id = int(input("Enter API_ID: "))
api_hash = input("Enter API_HASH: ")

with Client("session_gen", api_id=api_id, api_hash=api_hash) as app:
    print("\n✅ Your Session String:")
    print(app.export_session_string())
    print("\nCopy this and save as SESSION_STRING environment variable.")
