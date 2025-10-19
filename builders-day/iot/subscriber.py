# Minimal MQTT5 subscriber (mTLS)
from awsiot import mqtt5_client_builder
from awscrt import mqtt5
import argparse, uuid, threading

p = argparse.ArgumentParser()
p.add_argument("--endpoint", required=True)
p.add_argument("--cert", required=True)
p.add_argument("--key", required=True)
p.add_argument("--ca_file", default=None)
p.add_argument("--topic", default="demo/topic")
p.add_argument("--client_id", default=f"mqtt5-sub-{uuid.uuid4().hex[:8]}")
a = p.parse_args()

connected = threading.Event()
subscribed = threading.Event()

def on_conn_ok(d):
    connected.set()
    print("Connected to AWS IoT Core")

def on_message(data):
    try:
        packet = data.publish_packet
        payload = packet.payload.decode('utf-8')
        print(f"\n[Received from '{packet.topic}']")
        print(payload)
        print("-" * 50)
    except Exception as e:
        print(f"Error decoding message: {e}")

client = mqtt5_client_builder.mtls_from_path(
    endpoint=a.endpoint,
    cert_filepath=a.cert,
    pri_key_filepath=a.key,
    ca_filepath=a.ca_file,
    client_id=a.client_id,
    on_lifecycle_connection_success=on_conn_ok,
    on_publish_received=on_message,
)

print(f"Starting subscriber with client_id: {a.client_id}")
client.start()

if not connected.wait(30):
    raise TimeoutError("Connection timeout")

print(f"Subscribing to topic: {a.topic}")
sub_packet = mqtt5.SubscribePacket(
    subscriptions=[mqtt5.Subscription(topic_filter=a.topic, qos=mqtt5.QoS.AT_LEAST_ONCE)]
)
client.subscribe(sub_packet).result(30)
print(f"Successfully subscribed to '{a.topic}'")
print("Waiting for messages... (Press Ctrl+C to exit)")

try:
    # Keep the subscriber running
    threading.Event().wait()
except KeyboardInterrupt:
    print("\n\nShutting down...")
    client.stop()
    print("Done.")

