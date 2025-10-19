# Minimal MQTT5 publisher (mTLS)
from awsiot import mqtt5_client_builder
from awscrt import mqtt5
import argparse, time, uuid, threading, json

p = argparse.ArgumentParser()
p.add_argument("--endpoint", required=True)
p.add_argument("--cert", required=True)
p.add_argument("--key", required=True)
p.add_argument("--ca_file", default=None)
p.add_argument("--topic", default="demo/topic")
p.add_argument("--message", default="Hello from mqtt5 publisher")
p.add_argument("--count", type=int, default=5)
p.add_argument("--client_id", default=f"mqtt5-pub-{uuid.uuid4().hex[:8]}")
a = p.parse_args()

connected = threading.Event()
def on_conn_ok(d): connected.set()

client = mqtt5_client_builder.mtls_from_path(
    endpoint=a.endpoint,
    cert_filepath=a.cert,
    pri_key_filepath=a.key,
    ca_filepath=a.ca_file,
    client_id=a.client_id,
    on_lifecycle_connection_success=on_conn_ok,
)

client.start()
if not connected.wait(30):
    raise TimeoutError("Connection timeout")

for i in range(1, (a.count if a.count > 0 else 1_000_000) + 1):
    payload = {
        "message": a.message,
        "count": i,
        "timestamp": time.time()
    }
    payload_json = json.dumps(payload)
    print(f"Publishing to '{a.topic}': {payload_json}")
    fut = client.publish(mqtt5.PublishPacket(
        topic=a.topic, payload=payload_json.encode('utf-8'), qos=mqtt5.QoS.AT_LEAST_ONCE))
    fut.result(30)  # wait for PubAck
    time.sleep(1.0)

client.stop()
print("Done.")