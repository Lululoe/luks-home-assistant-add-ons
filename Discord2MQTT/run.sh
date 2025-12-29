#!/usr/bin/with-contenv bashio
source /app/venv/bin/activate

# Mandatory fields
export DISCORD_BOT_TOKEN=$(bashio::config 'discord_bot_token')
export MQTT_BASE_TOPIC=$(bashio::config 'mqtt_base_topic')
export MQTT_DISCOVERY_PREFIX=$(bashio::config 'mqtt_discovery_prefix')

# Optional fields

if bashio::config.has_value 'mqtt_host';     then export MQTT_HOST=$(bashio::config 'mqtt_host'); else export MQTT_HOST=$(bashio::services mqtt "host"); fi
if bashio::config.has_value 'mqtt_port';     then export MQTT_PORT=$(bashio::config 'mqtt_port'); else export MQTT_PORT=$(bashio::services mqtt "port"); fi
if bashio::config.has_value 'mqtt_user';     then export MQTT_USER=$(bashio::config 'mqtt_user'); else export MQTT_USER=$(bashio::services mqtt "username"); fi
if bashio::config.has_value 'mqtt_password'; then export MQTT_PASSWORD=$(bashio::config 'mqtt_password'); else export MQTT_PASSWORD=$(bashio::services mqtt "password"); fi

bashio::log.info "Configuration:
  DISCORD_BOT_TOKEN: ****
  MQTT_HOST: ${MQTT_HOST}
  MQTT_PORT: ${MQTT_PORT}
  MQTT_USER: ${MQTT_USER}
  MQTT_PASSWORD: ****
  MQTT_BASE_TOPIC: ${MQTT_BASE_TOPIC}
  MQTT_DISCOVERY_PREFIX: ${MQTT_DISCOVERY_PREFIX}"
bashio::log.info "Starting Discord2MQTT script..."

if [ "${MQTT_HOST}" = "null" ] || [ "${MQTT_PORT}" = "null" ] || [ "${MQTT_USER}" = "null" ] || [ "${MQTT_PASSWORD}" = "null" ] || [ "${MQTT_BASE_TOPIC}" = "null" ] || [ "${MQTT_DISCOVERY_PREFIX}" = "null" ]; then
    bashio::log.fatal "MQTT configuration is missing! Please check your settings."
    exit 1
fi

if [ "${DISCORD_BOT_TOKEN}" = "null" ]; then
    bashio::log.fatal "Discord Bot Token is missing! Please check your settings."
    exit 1
fi

exec python3 -u app.py