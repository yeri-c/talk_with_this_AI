import base64
import asyncio
import sounddevice as sd
import numpy as np
from openai import AsyncOpenAI

import os
from dotenv import load_dotenv
load_dotenv()

token = os.getenv("STT_APIKEY")
endpoint = os.getenv("STT_ENDPOINT", "https://10ai000-openai.openai.azure.com")
deployment_name = "gpt-realtime-mini"

SAMPLE_RATE = 24000
CHANNELS = 1
CHUNK_DURATION = 0.1

async def main():
    base_url = endpoint.replace("https://", "wss://").rstrip("/") + "/openai/v1"
    client = AsyncOpenAI(websocket_base_url=base_url, api_key=token)
    
    async with client.realtime.connect(model=deployment_name) as connection:
        await connection.session.update(session={
            "type": "realtime",
            "instructions": "You are a helpful assistant. Respond in the same language as the user.",
            "output_modalities": ["audio"],
            "audio": {
                "input": {
                    "transcription": {"model": "whisper-1"},
                    "format": {"type": "audio/pcm", "rate": 24000},
                    "turn_detection": {
                        "type": "server_vad",
                        "threshold": 0.5,
                        "prefix_padding_ms": 300,
                        "silence_duration_ms": 500,
                        "create_response": True
                    }
                },
                "output": {
                    "voice": "alloy",
                    "format": {"type": "audio/pcm", "rate": 24000}
                }
            }
        })

        print("🎤 말씀하세요! (종료: Ctrl+C)\n")

        audio_output_queue = asyncio.Queue()

        async def play_audio():
            stream = sd.OutputStream(samplerate=SAMPLE_RATE, channels=1, dtype='int16')
            stream.start()
            try:
                while True:
                    chunk = await audio_output_queue.get()
                    stream.write(chunk)
            finally:
                stream.stop()

        async def send_audio():
            loop = asyncio.get_event_loop()
            queue = asyncio.Queue()

            def callback(indata, frames, time, status):
                loop.call_soon_threadsafe(queue.put_nowait, indata.copy())

            with sd.InputStream(samplerate=SAMPLE_RATE, channels=CHANNELS,
                                dtype='int16', callback=callback,
                                blocksize=int(SAMPLE_RATE * CHUNK_DURATION)):
                while True:
                    chunk = await queue.get()
                    audio_b64 = base64.b64encode(chunk.tobytes()).decode()
                    await connection.input_audio_buffer.append(audio=audio_b64)

        async def receive_events():
            async for event in connection:
                if event.type == "response.output_audio.delta":
                    # 스피커 출력
                    audio_bytes = base64.b64decode(event.delta)
                    audio_array = np.frombuffer(audio_bytes, dtype=np.int16)
                    await audio_output_queue.put(audio_array)
                elif event.type == "response.output_audio_transcript.delta":
                    # 텍스트 출력
                    print(event.delta, end="", flush=True)
                elif event.type == "response.output_audio_transcript.done":
                    print()
                elif event.type == "conversation.item.input_audio_transcription.completed":
                    print(f"\n🙋 나  : {event.transcript}")
                    print("🤖 AI : ", end="", flush=True)
                elif event.type == "error":
                    print(f"\n❌ 오류: {event.error.message}")

        tasks = [
            asyncio.create_task(send_audio()),
            asyncio.create_task(receive_events()),
            asyncio.create_task(play_audio()),
        ]
        try:
            await asyncio.gather(*tasks)
        except (KeyboardInterrupt, asyncio.CancelledError):
            print("\n👋 종료합니다.")
            for t in tasks:
                t.cancel()

if __name__ == "__main__":
    asyncio.run(main())