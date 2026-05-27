# 🎤 Talk with AI

Azure OpenAI GPT Realtime API를 활용한 실시간 음성 대화 프로그램입니다.
마이크로 말하면 AI가 실시간으로 인식하고 음성으로 답변해줍니다.

## 주요 기능

- 🎙️ 실시간 마이크 입력 (sounddevice)
- 🔊 AI 음성 응답 스피커 출력
- 📝 대화 내용 텍스트로 출력
- 🌐 한국어/영어 등 다국어 지원

## 사용 기술

- Azure OpenAI GPT Realtime API (`gpt-realtime-mini`)
- Python `asyncio` 비동기 처리
- WebSocket 실시간 통신
- sounddevice 마이크/스피커 제어

## 설치

```bash
pip install -r requirements.txt
```

## 환경 변수 설정

`.env` 파일을 만들고 아래 내용 입력:

```
STT_APIKEY=your-api-key
STT_ENDPOINT=https://your-resource.openai.azure.com
```

## 실행

```bash
python realtime_voice.py
```

말씀하시면 AI가 실시간으로 응답합니다. 종료는 Jupyter에서 ■ 버튼, 터미널에서 Ctrl+C.
