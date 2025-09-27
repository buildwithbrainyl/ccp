import json
import os
import logging
import boto3
from typing import Optional, Dict, Any

logger = logging.getLogger()
logger.setLevel(logging.INFO)

ec2 = boto3.client("ec2")
FALLBACK_INSTANCE_ID = os.getenv("INSTANCE_ID", "").strip()

def extract_instance_id_from_alarm(alarm: Dict[str, Any]) -> Optional[str]:
    trigger = alarm.get("Trigger", {}) or {}
    dims = trigger.get("Dimensions") or trigger.get("dimensions") or []
    for d in dims:
        name = (d.get("name") or d.get("Name") or "").lower()
        if name == "instanceid":
            return d.get("value") or d.get("Value")
    desc = alarm.get("AlarmDescription") or alarm.get("alarmDescription") or ""
    if "i-" in desc:
        for token in desc.replace(",", " ").split():
            if token.startswith("i-"):
                return token
    return None

def stop_instance(instance_id: str) -> None:
    d = ec2.describe_instances(InstanceIds=[instance_id])
    state = d["Reservations"][0]["Instances"][0]["State"]["Name"]
    logger.info(f"Instance {instance_id} current state: {state}")
    if state in ("stopped", "stopping", "shutting-down", "terminated"):
        logger.info(f"No action needed; instance {instance_id} is {state}.")
        return
    if state == "pending":
        logger.info(f"Instance {instance_id} is pending; cannot stop yet.")
        return
    logger.info(f"Stopping instance {instance_id}...")
    ec2.stop_instances(InstanceIds=[instance_id])
    logger.info(f"StopInstances called for {instance_id}")

def lambda_handler(event, _context):
    logger.info("Event: %s", json.dumps(event))
    errors = []
    for record in event.get("Records", []):
        try:
            body = json.loads(record["body"])
            if "Message" not in body:
                logger.warning("SQS body missing SNS 'Message': %s", body)
                continue
            alarm = json.loads(body["Message"])
            new_state = (alarm.get("NewStateValue") or "").upper()
            if new_state != "ALARM":
                logger.info(f"Skipping (state={new_state})")
                continue
            instance_id = extract_instance_id_from_alarm(alarm) or FALLBACK_INSTANCE_ID
            if not instance_id:
                raise ValueError("Could not determine InstanceId from alarm and no fallback provided.")
            stop_instance(instance_id)
        except Exception as e:
            logger.exception("Failed to process record")
            errors.append(str(e))
    if errors:
        raise RuntimeError("One or more records failed: " + "; ".join(errors))
    return {"status": "ok"}
