
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import StreamingResponse, JSONResponse
import asyncio
import json
from app.core.robot_state import RobotState
from app.mqtt_bridge import MQTTBridge

app = FastAPI(title="VDA5050 REST + SSE Gateway")

# create singleton robot state
robot_state = RobotState.get_instance()

# start MQTT bridge when app starts
@app.on_event("startup")
async def startup_event():
    loop = asyncio.get_event_loop()
    mqtt = MQTTBridge(broker_host="localhost", broker_port=1883, loop=loop)
    mqtt.start()
    # attach to app state for possible later use
    app.state.mqtt = mqtt

@app.get("/health")
async def health():
    return {"status": "ok"}

@app.get("/robots")
async def list_robots():
    snapshot = await robot_state.get_snapshot()
    return JSONResponse(content=snapshot)

@app.get("/stream")
async def stream_all(request: Request):
    """SSE stream for all robot updates. Each event is a JSON string."""
    q = await robot_state.subscribe()

    async def event_generator():
        try:
            # when client connects, send a snapshot first
            snapshot = await robot_state.get_snapshot()
            yield f"data: {json.dumps({"type":"snapshot","data": snapshot})}\n\n"

            while True:
                # if client disconnected, break
                if await request.is_disconnected():
                    break
                try:
                    item = await asyncio.wait_for(q.get(), timeout=15.0)
                    # SSE data line
                    yield f"data: {json.dumps({"type":"update","data": item})}\n\n"
                except asyncio.TimeoutError:
                    # send a comment as a keepalive
                    yield ": keepalive\n\n"
        finally:
            await robot_state.unsubscribe(q)

    return StreamingResponse(event_generator(), media_type="text/event-stream")

@app.get("/stream/{manufacturer}/{serial}")
async def stream_robot(manufacturer: str, serial: str, request: Request):
    q = await robot_state.subscribe()
    key = f"{manufacturer}/{serial}"

    async def event_generator():
        try:
            # send initial snapshot for this robot only
            snapshot = await robot_state.get_snapshot()
            if key in snapshot:
                yield f"data: {json.dumps({"type":"snapshot","data": {key: snapshot[key]}})}\n\n"

            while True:
                if await request.is_disconnected():
                    break
                try:
                    item = await asyncio.wait_for(q.get(), timeout=15.0)
                    # filter only messages for this robot
                    if item.get('topic') == key:
                        yield f"data: {json.dumps({"type":"update","data": item})}\n\n"
                except asyncio.TimeoutError:
                    yield ": keepalive\n\n"
        finally:
            await robot_state.unsubscribe(q)

    return StreamingResponse(event_generator(), media_type="text/event-stream")

# optional: post command to robot (example)
@app.post("/command/{manufacturer}/{serial}")
async def send_command(manufacturer: str, serial: str, request: Request):
    body = await request.json()
    # publish to MQTT if needed
    mqtt: MQTTBridge = app.state.mqtt
    topic = f"/vda5050/{manufacturer}/{serial}/command"
    # assume payload is JSON serializable
    mqtt.client.publish(topic, json.dumps(body))
    return {"status": "published", "topic": topic}