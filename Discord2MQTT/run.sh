#!/usr/bin/with-contenv bashio
source /app/venv/bin/activate

# Create main config
export DISCORD_BOT_TOKEN=$(bashio::config 'discord_bot_token')
export MQTT_HOST=$(bashio::config 'mqtt_host')
export MQTT_PORT=$(bashio::config 'mqtt_port')
export MQTT_USER=$(bashio::config 'mqtt_user')
export MQTT_PASSWORD=$(bashio::config 'mqtt_password')
export MQTT_BASE_TOPIC=$(bashio::config 'mqtt_topic')
export MQTT_DISCOVERY_PREFIX=$(bashio::config 'mqtt_discovery_prefix')

bashio::log.info "Starting Discord2MQTT script..."
python3 app.py