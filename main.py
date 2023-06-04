from fastapi import FastAPI, UploadFile, Form, WebSocket, WebSocketDisconnect,File
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi_socketio import SocketManager
import redis
from datetime import datetime
import json
from AudioStremManager_ws import stream_manager
from AWS_S3 import s3_client

app = FastAPI()
socket_manager = SocketManager(app, cors_allowed_origins='*')
origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Connect to Redis
redis_client = redis.Redis(host='localhost', port=6379, db=0)
CACHE_TTL = 1800 #30mins

@app.get('/')
async def root():
    return {"message": "Welcome to the FastAPI server!"}

@app.post("/audio-stream-polling")
async def process_audio_stream(
    audio_file: UploadFile = File(...),
    video_file: UploadFile = File(None),
    data_id: str = Form(...),
    timestamp: str = Form(...)
):
    # Retrieve the audio content from the uploaded file
    audio_content = await audio_file.read()

    # Retrieve the video content from the uploaded file, if provided
    if video_file:
        video_content = await video_file.read()
    else:
        video_content = None

    # Perform audio analysis and classification here
    # You can use the provided audio_content and video_content variables

    # Store the analyzed result and return the response
    result = {
        "data_id": data_id,
        "audio_file": audio_file.filename,
        "video_file": video_file.filename,
        "class_distribution": {
            "class1": 0.3,
            "class2": 0.7,
            "infant_cry": 0.9
        }
    }
    # Store the analysis result in Redis
    cache_key = f'analysis_result:{data_id}'
    cache_value = {
        'timestamp': str(datetime.now()),
        'result': result
    }
    redis_client.setex(cache_key, CACHE_TTL,json.dumps(cache_value))

    s3_client.put_object_s3(audio_content, data_id + "_audio_"+audio_file.filename)
    if video_file: 
        s3_client.put_object_s3(video_content, data_id + "_video_"+video_file.filename)

    return result

@app.websocket("/audio-stream-websocket")
async def audio_stream(websocket: WebSocket):
    await stream_manager.connect(websocket)

    try:
        while True:
            audio_stream = await websocket.receive_bytes()
            await stream_manager.receive_audio_stream(audio_stream)
    except WebSocketDisconnect:
        stream_manager.disconnect(websocket)



@socket_manager.on("connect")
async def connect(sid, environ):
    print(f'Client {sid} connected')

@socket_manager.on("disconnect")
async def disconnect(sid):
    print(f'Client {sid} disconnected')

@socket_manager.on("audio_stream_socketio")
async def process_audio_stream(sid, data):
    audio_content = data.get('audio_content')
    video_content = data.get('video_content')
    data_id = data.get('data_id')
    timestamp = data.get('timestamp')

    # Perform audio analysis and classification here
    # You can use the provided audio_content and video_content variables

    # Store the analyzed result and emit it back to the client
    result = {
        'data_id': data_id,
        'class_distribution': {
            'class1': 0.3,
            'class2': 0.7,
            'infant_cry': 0.9
        }
    }

    # Store the analysis result in Redis
    cache_key = f'analysis_result:{data_id}'
    cache_value = {
        'timestamp': str(datetime.now()),
        'result': result
    }
    redis_client.setex(cache_key, CACHE_TTL,json.dumps(cache_value))

    await socket_manager.emit('analysis_result', result, room=sid)




        

