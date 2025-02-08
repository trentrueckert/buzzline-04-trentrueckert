"""
project_consumer_rueckert.py

Consumes json messages from a Kafka topic and updates a real-time pie chart which displays the frequency of adjectives.

"""

#####################################
# Import Modules
#####################################

import os
import json
from collections import defaultdict
from dotenv import load_dotenv
import matplotlib.pyplot as plt
import matplotlib.animation as animation

# Import Kafka only if available
try:
    from kafka import KafkaConsumer
    KAFKA_AVAILABLE = True
except ImportError:
    KAFKA_AVAILABLE = False

# Import functions from local modules
from utils.utils_consumer import create_kafka_consumer
from utils.utils_logger import logger

#####################################
# Load Environment Variables
#####################################

load_dotenv()

#####################################
# Define the adjectives and colors
#####################################

ADJECTIVES = ["amazing", "funny", "boring", "exciting", "weird"]

COLORS = ["#FF0000", "#00FF00", "#0000FF", "#FFFF00", "#FF00FF"]

adjective_counts = defaultdict(int)

#####################################
# Getter Functions for .env Variables
#####################################

def get_kafka_topic() -> str:
    return os.getenv("PROJECT_TOPIC", "buzzline-topic")

def get_kafka_server() -> str:
    return os.getenv("KAFKA_SERVER", "localhost:9092")

topic = get_kafka_topic()
kafka_server = get_kafka_server()

consumer = None
if KAFKA_AVAILABLE:
    try:
        consumer = KafkaConsumer(
            topic,
            bootstrap_servers=kafka_server,
            value_deserializer=lambda x: json.loads(x.decode("utf-8")),
            auto_offset_reset="earliest",
            group_id="action-consumer-group"
        )
        logger.info(f"Kafka consumer connected to {kafka_server}, listening on topic '{topic}'")
    except Exception as e:
        logger.error(f"Kafka connection failed: {e}")
        consumer = None
else:
    logger.warning("Kafka is not available. Running in local mode.")

#################################
# Create Kafka consumer
#################################

consumer = KafkaConsumer(
    topic,
    bootstrap_servers=kafka_server,
    value_deserializer=lambda x: json.loads(x.decode("utf-8")),
    auto_offset_reset="earliest",
    group_id="action-consumer-group"
)

# Create figure for live chart
fig, ax = plt.subplots(figsize=(3, 3))

def consume_messages():
    """Consume messages from Kafka and update adjective counts."""
    global adjective_counts

    for message in consumer:
        data = message.value
        text = data.get("message", "")

        # Update counts for each adjective found in the message
        for adjective in ADJECTIVES:
            if adjective in text:
                adjective_counts[adjective] += 1
                print(f"Updated count for '{adjective}': {adjective_counts[adjective]}")

        break

def update_chart(i):
    """Update the live pie chart with the latest adjective counts."""
    global adjective_counts

    # Consume messages in a non-blocking way (single iteration)
    consume_messages()

    # Prevent NaN errors and handle no data condition
    if all(value == 0 for value in adjective_counts.values()):
        labels = ["Waiting for data..."]
        sizes = [1]
        colors = ["red"]
    else:
        labels = list(adjective_counts.keys())
        sizes = list(adjective_counts.values())
        colors = COLORS

    # Clear and update the pie chart
    ax.clear()
    ax.pie(sizes, labels=labels, colors=colors, autopct='%1.1f%%')
    ax.set_title("Trent Analytics: Real-Time Adjective Frequency")
    
    # Use tight_layout() to automatically adjust the padding
    plt.tight_layout()

    # Ensure the plot is rendered in each update
    plt.draw()

def main():
    """Main function to start the consumer and plot."""
    print("Starting consumer...")

    # Set up animation to update the chart every 2 seconds
    ani = animation.FuncAnimation(fig, update_chart, interval=2000)

    # Show the plot (blocking call)
    plt.show()

if __name__ == "__main__":
    main()