import os
import discord
import paho.mqtt.client as mqtt
from paho.mqtt.enums import CallbackAPIVersion # Import the versioning enum
import json

# MQTT Configuration
MQTT_HOST = os.getenv("MQTT_HOST")
# Provide a default port and handle potential None values
MQTT_PORT_STR = os.getenv("MQTT_PORT")
MQTT_PORT = int(MQTT_PORT_STR) if MQTT_PORT_STR.isdigit() else 1883

MQTT_USERNAME = os.getenv("MQTT_USER")
MQTT_PASSWORD = os.getenv("MQTT_PASSWORD")
MQTT_BASE_TOPIC = os.getenv("MQTT_BASE_TOPIC")
MQTT_DISCOVERY_PREFIX = os.getenv("MQTT_DISCOVERY_PREFIX")
DISCORD_BOT_TOKEN = os.getenv("DISCORD_BOT_TOKEN")

# Discord bot setup
intents = discord.Intents.default()
intents.guilds = True
intents.voice_states = True
intents.members = True

client = discord.Client(intents=intents)

# FIX: Initialize with CallbackAPIVersion.VERSION2 to remove the warning
mqtt_client = mqtt.Client(CallbackAPIVersion.VERSION2)

# Cache current voice states
voice_channel_states = {}

def setup_mqtt():
    # Only set credentials if a username is actually present
    if MQTT_USERNAME:
        # Paho MQTT handles empty/None passwords gracefully if username is provided
        mqtt_client.username_pw_set(MQTT_USERNAME, MQTT_PASSWORD)
        print(f"MQTT: Authenticating as user '{MQTT_USERNAME}'")
    else:
        print("MQTT: Connecting without authentication (ensure this is intended)")

    mqtt_client.connect(MQTT_HOST, MQTT_PORT, 60)
    mqtt_client.loop_start()

def publish_discovery(guild: discord.Guild):
    components = {}
    for channel in guild.voice_channels:
        topic = f"{MQTT_BASE_TOPIC}/{guild.id}/{channel.id}/state"
        components[channel.name] = {
            "platform": "sensor",
            "unit_of_measurement": "Users",
            "value_template": "{{ value_json.users }}",
            "state_topic": topic,
            "json_attributes_topic": f"{MQTT_BASE_TOPIC}/{guild.id}/{channel.id}/attributes",
            "json_attributes_template": "{\"users\": {{ value_json.users | tojson }}}",
            "unique_id": str(channel.id),
            "name": channel.name
        }
        voice_channel_states[channel.id] = len(channel.members)

    discovery_msg = {
        "device": {
            "ids": [str(guild.id)],
            "name": guild.name,
            "mf": "Discord",
            "mdl": guild.name,
        },
        "origin": {
            "name": "discord2mqtt",
            "sw": "1.0",
            "url": "https://example.com/support"
        },
        "components": components,
        "qos": 2
    }

    mqtt_client.publish(f"{MQTT_DISCOVERY_PREFIX}/{guild.id}/config", json.dumps(discovery_msg), retain=True)

    # Publish initial state for all channels
    for channel in guild.voice_channels:
        publish_channel_update(guild.id, channel)
        publish_channel_attributes(guild.id, channel)

def publish_channel_update(guild_id, channel: discord.VoiceChannel):
    topic = f"{MQTT_BASE_TOPIC}/{guild_id}/{channel.id}/state"
    payload = json.dumps({"users": len(channel.members)})
    mqtt_client.publish(topic, payload)

def publish_channel_attributes(guild_id, channel: discord.VoiceChannel):
    attr_topic = f"{MQTT_BASE_TOPIC}/{guild_id}/{channel.id}/attributes"
    # display_names = [member.display_name for member in channel.members]
    members = []
    for member in channel.members:
        members.append({
            "id": str(member.id),
            "name": member.name,
            "display_name": member.display_name,
            "avatar_url": str(member.avatar.url) if member.avatar else None
        })
    payload = json.dumps({"users": members})
    mqtt_client.publish(attr_topic, payload)

def publish_channel_deletion(guild_id, channel_name):
    minimal_msg = {
        "cmps": {
            channel_name: {
                "p": "sensor"
            }
        }
    }
    mqtt_client.publish(f"{MQTT_DISCOVERY_PREFIX}/{guild_id}/config", json.dumps(minimal_msg), retain=True)
    print(f"Deleted channel config published for: {channel_name}")

@client.event
async def on_ready():
    print(f'Bot connected as {client.user}')
    for guild in client.guilds:
        print(f'Initializing for server: {guild.name} ({guild.id})')
        publish_discovery(guild)
        for channel in guild.voice_channels:
            publish_channel_update(guild.id, channel)

@client.event
async def on_voice_state_update(member, before, after):
    guild = member.guild
    affected_channels = set()

    if before.channel:
        affected_channels.add(before.channel)
    if after.channel:
        affected_channels.add(after.channel)

    for channel in affected_channels:
        publish_channel_update(guild.id, channel)
        publish_channel_attributes(guild.id, channel)

@client.event
async def on_guild_channel_delete(channel):
    if isinstance(channel, discord.VoiceChannel):
        publish_channel_deletion(channel.guild.id, channel.name)

if __name__ == '__main__':
    setup_mqtt()
    if DISCORD_BOT_TOKEN:
        client.run(DISCORD_BOT_TOKEN)
    else:
        print("Error: DISCORD_BOT_TOKEN not found. Check your config or .env file.")
