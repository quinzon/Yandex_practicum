#!/bin/bash

# Enable strict error handling
set -e

# Load environment variables from .env
set -o allexport
source .env
set +o allexport

# Split topics string into array
IFS=',' read -r -a TOPICS <<< "$KAFKA_TOPICS"

# Function to create a topic
create_topic() {
  local TOPIC="$1"
  kafka-topics.sh --create \
    --bootstrap-server "$KAFKA_BROKER" \
    --topic "$TOPIC" \
    --partitions "$KAFKA_PARTITIONS" \
    --replication-factor "$KAFKA_REPLICATION_FACTOR" \
    --if-not-exists
}

# Main loop to create topics
for TOPIC in "${TOPICS[@]}"; do
  echo "Creating topic: $TOPIC"
  create_topic "$TOPIC"
done

echo "All topics created successfully."

exit 0
