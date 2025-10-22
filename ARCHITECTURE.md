### CLI Mode Flow

```
┌──────────────────────┐
│ robot_streamer.py    │
│                      │
│ 1. Connect to MQTT   │──┐
│ 2. Publish ONLINE    │  │
│ 3. Loop:             │  │    ┌──────────────────┐
│    - Simulate state  │  ├───►│  MQTT Broker     │
│    - Publish state   │  │    │  localhost:1883  │
│    - Publish viz     │  │    └──────────────────┘
│    - Sleep           │  │              │
└──────────────────────┘  │              │ Subscribe
                          │              │
┌──────────────────────┐  │    ┌─────────▼──────────┐
│ multi_robot_demo.py  │  │    │ process_vda5050_   │
│                      │  │    │ messages.py        │
│ Spawn 3 threads:     │  │    │                    │
│ - Thread 1 ──────────┼──│    │ Display messages   │
│ - Thread 2 ──────────┼──│    │ to console         │
│ - Thread 3 ──────────┼──┘    │                    │
└──────────────────────┘       └────────────────────┘
```

### Web Service Mode Flow

```
┌──────────────────────┐
│  MQTT Broker         │
│  /vda5050/#          │
└──────────┬───────────┘
           │ Subscribe
           │
┌──────────▼───────────┐
│  mqtt_bridge.py      │
│  (Background Thread) │
│                      │
│  on_message():       │
│  - Parse topic       │
│  - Schedule coro ────┼──┐
└──────────────────────┘  │
                          │
           ┌──────────────▼─────────────┐
           │  asyncio Event Loop        │
           │                            │
           │  ┌──────────────────────┐  │
           │  │ robot_state.py       │  │
           │  │                      │  │
           │  │ update_from_mqtt()   │  │
           │  │ - Update state       │  │
           │  │ - Notify subscribers │  │
           │  └──────────┬───────────┘  │
           │             │              │
           │      ┌──────▼──────┐       │
           │      │ Subscribers │       │
           │      │ (Queues)    │       │
           │      └──────┬──────┘       │
           └─────────────┼──────────────┘
                         │
           ┌─────────────▼──────────────┐
           │  api.py - SSE Endpoints    │
           │                            │
           │  /stream                   │
           │  /stream/{mfr}/{serial}    │
           │                            │
           │  event_generator():        │
           │  - Send snapshot           │
           │  - Loop: await q.get()     │
           │  - Yield SSE events        │
           └────────────────────────────┘
                         │
                         │ HTTP/SSE
                         │
           ┌─────────────▼──────────────┐
           │  Browser / Client          │
           │                            │
           │  EventSource('/stream')    │
           │  - Receive updates         │
           │  - Display in real-time    │
           └────────────────────────────┘
```

### Startup Sequence (Web Service)

```
1. FastAPI app.on_event("startup")
   │
   ├─► Create MQTTBridge instance
   │   └─► mqtt.Client.connect(localhost:1883)
   │       └─► mqtt.Client.loop_forever() in thread
   │           └─► Subscribe to /vda5050/#
   │
   └─► uvicorn serves FastAPI app
       └─► asyncio event loop ready
```

### Request Flow (SSE Stream)

```
Client connects to /stream
   │
   ├─► RobotState.subscribe() creates Queue
   │
   ├─► Send initial snapshot
   │
   └─► Loop:
       ├─► await queue.get() (blocks until update)
       │
       ├─► Yield SSE event
       │   └─► data: {"type":"update","data":{...}}\n\n
       │
       └─► Check if client disconnected
           └─► If yes: RobotState.unsubscribe()
```

## Security Considerations

### Current Implementation (Development)
- No authentication
- No TLS/SSL
- MQTT broker on localhost
- Web service on all interfaces (0.0.0.0)

### Production Recommendations
1. Add API key authentication to FastAPI endpoints
2. Use MQTT with TLS and authentication
3. Restrict web service to specific interfaces
4. Add rate limiting
5. Implement proper error handling
6. Add logging and monitoring

---

## Scalability Notes

### Current Limitations
- **In-Memory State**: Lost on restart
- **Single Server**: No horizontal scaling
- **Queue-Based Pub/Sub**: Limited subscribers

### Production Enhancements
- Use Redis for distributed state
- Add message persistence (database)
- Implement WebSocket alternative to SSE
- Add load balancer for multiple web service instances
- Use message queue (RabbitMQ, Kafka) instead of in-memory queues