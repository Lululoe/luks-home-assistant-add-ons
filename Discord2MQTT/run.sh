#!/usr/bin/with-contenv bashio
source /app/venv/bin/activate

# Mandatory fields
export DISCORD_BOT_TOKEN=$(bashio::config 'discord_bot_token')
export MQTT_BASE_TOPIC=$(bashio::config 'mqtt_base_topic')
export MQTT_DISCOVERY_PREFIX=$(bashio::config 'mqtt_discovery_prefix')

# Optional fields

if bashio::config.has_value 'mqtt_host';     then export MQTT_HOST=$(bashio::config 'mqtt_host'); fi
if bashio::config.has_value 'mqtt_port';     then export MQTT_PORT=$(bashio::config 'mqtt_port'); fi
if bashio::config.has_value 'mqtt_user';     then export MQTT_USER=$(bashio::config 'mqtt_user'); fi
if bashio::config.has_value 'mqtt_password'; then export MQTT_PASSWORD=$(bashio::config 'mqtt_password'); fi

bashio::log.info "Starting Discord2MQTT script..."

python3 app.py