# CarePill Voice-First Architecture Design

**Document Version**: 1.0
**Date**: 2025-10-01
**Target Branch**: `develop-voice`
**Project**: CarePill Django Medicine Analysis System

---

## Table of Contents

1. [Executive Summary](#executive-summary)
2. [System Architecture Overview](#system-architecture-overview)
3. [Component Design](#component-design)
4. [Voice Processing Pipeline](#voice-processing-pipeline)
5. [Data Models & Database Schema](#data-models--database-schema)
6. [API Design](#api-design)
7. [NLU Intent & Entity Schema](#nlu-intent--entity-schema)
8. [Error Handling Strategy](#error-handling-strategy)
9. [Performance Optimization](#performance-optimization)
10. [Deployment Architecture](#deployment-architecture)
11. [Implementation Roadmap](#implementation-roadmap)
12. [File Structure & Code Organization](#file-structure--code-organization)

---

## Executive Summary

### Project Goal
Add voice-first interaction to CarePill Django application with always-listening capability, Korean wake word "케어필", and natural language command processing for medication management.

### Core Requirements
- **Always Listening**: Continuous standby mode with low resource usage
- **Wake Word**: "케어필" (Korean) triggers command capture
- **Flexible Commands**: Natural Korean language understanding
- **Full Voice Interaction**: Complete medication management without screen
- **<3 Second Latency**: Wake word to voice response under 3 seconds

### Technology Stack
- **STT**: Naver Clova Speech Recognition (Korean)
- **TTS**: Naver Clova Voice (Korean)
- **Wake Word**: Porcupine by Picovoice (custom "케어필" model)
- **NLU**: OpenAI GPT-4 with function calling
- **Backend**: Django 4.2.7 REST API
- **Audio**: PyAudio for capture/playback
- **Async**: asyncio for concurrent API calls

### Architecture Decision
**Standalone Voice Service + Django REST API Backend**

- Voice service runs as separate Python process (Django management command for MVP)
- Django provides REST API for medication operations
- Clean separation of concerns: audio processing vs business logic
- Independent scaling and debugging capabilities

---

## System Architecture Overview

### High-Level Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────┐
│                         USER INTERACTION                            │
│                    (Voice Commands in Korean)                       │
└────────────────────────────────┬────────────────────────────────────┘
                                 │
                                 ▼
┌─────────────────────────────────────────────────────────────────────┐
│                      VOICE SERVICE LAYER                            │
│                   (Standalone Python Process)                       │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │  Audio Input → Wake Word → STT → NLU → TTS → Audio Output  │   │
│  └─────────────────────────────────────────────────────────────┘   │
│                                                                     │
│  Components:                                                        │
│  • PyAudio (Microphone Capture)                                    │
│  • Porcupine (Wake Word Detection: "케어필")                        │
│  • Audio Buffer Manager (Rolling 5-second buffer)                  │
│  • Naver Clova STT Client                                          │
│  • OpenAI NLU Service (Intent/Entity Extraction)                   │
│  • Naver Clova TTS Client                                          │
│  • Conversation Context Manager                                    │
└────────────────────────────┬────────────────────────────────────────┘
                             │
                             │ REST API Calls
                             │ (HTTP/JSON)
                             ▼
┌─────────────────────────────────────────────────────────────────────┐
│                    DJANGO BACKEND (REST API)                        │
│                                                                     │
│  ┌──────────────────────┐      ┌──────────────────────┐           │
│  │  medicine_analyzer   │      │  voice_assistant     │           │
│  │  (Existing App)      │      │  (New App)           │           │
│  │                      │      │                      │           │
│  │  • Image Analysis    │◄─────┤  • Voice API         │           │
│  │  • Medicine ID       │      │  • Schedule Mgmt     │           │
│  │  • OpenAI Vision     │      │  • Medication Logs   │           │
│  └──────────────────────┘      │  • Reminder Logic    │           │
│                                │  • Context Storage   │           │
│                                └──────────────────────┘           │
└────────────────────────────┬────────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────────┐
│                      DATABASE LAYER                                 │
│                       (SQLite / PostgreSQL)                         │
│                                                                     │
│  • MedicineAnalysis (existing)                                     │
│  • MedicationSchedule (new)                                        │
│  • MedicationLog (new)                                             │
│  • VoiceInteraction (new)                                          │
│  • ConversationContext (new)                                       │
│  • ReminderSettings (new)                                          │
└─────────────────────────────────────────────────────────────────────┘
```

### Architecture Principles

1. **Separation of Concerns**: Voice processing separate from business logic
2. **API-First**: Django exposes REST API for all medication operations
3. **Async by Default**: Voice service uses asyncio for concurrent API calls
4. **Stateless API**: Django API is stateless, voice service manages conversation state
5. **Fail-Safe**: Graceful degradation when APIs unavailable

---

## Component Design

### 1. Voice Service Layer

**Responsibility**: Continuous audio monitoring, wake word detection, voice command processing, and audio output.

**Components**:

#### 1.1 Audio Input Manager (`audio_manager.py`)
```python
class AudioInputManager:
    """
    Manages continuous microphone input with circular buffering.

    Responsibilities:
    - Capture audio from microphone (16kHz, mono, 16-bit PCM)
    - Maintain rolling 5-second circular buffer
    - Provide audio chunks to wake word detector
    - Capture command audio after wake word trigger
    """
```

**Configuration**:
- Sample Rate: 16000 Hz
- Channels: 1 (mono)
- Format: 16-bit PCM
- Frame Length: 512 samples (~32ms per frame)
- Buffer Size: 5 seconds (80,000 samples)

#### 1.2 Wake Word Detector (`wake_word_detector.py`)
```python
class WakeWordDetector:
    """
    Porcupine-based wake word detection for "케어필".

    Responsibilities:
    - Load custom Porcupine model for "케어필"
    - Process audio frames in real-time
    - Trigger command capture on detection
    - Return to listening mode after command processing
    """
```

**Key Features**:
- Runs locally (no network calls)
- ~30ms latency per frame
- Sensitivity tunable (0.0-1.0, default 0.5)
- False positive rate: <1% with proper tuning

#### 1.3 STT Service (`stt_service.py`)
```python
class NaverClovaSTTService:
    """
    Naver Clova Speech-to-Text integration.

    Responsibilities:
    - Convert captured audio to text (Korean)
    - Handle API authentication
    - Retry logic for transient failures
    - Return transcript with confidence score
    """

    async def transcribe_audio(self, audio_data: bytes) -> STTResult:
        """
        Args:
            audio_data: Raw audio bytes (WAV format)

        Returns:
            STTResult with transcript and confidence
        """
```

**API Details**:
- Endpoint: `https://naveropenapi.apigw.ntruss.com/recog/v1/stt?lang=Kor`
- Method: POST
- Headers: `X-NCP-APIGW-API-KEY-ID`, `X-NCP-APIGW-API-KEY`
- Max Audio Length: 60 seconds
- Expected Latency: <1 second for 3-5 second audio

#### 1.4 NLU Service (`nlu_service.py`)
```python
class OpenAINLUService:
    """
    OpenAI GPT-4 based natural language understanding.

    Responsibilities:
    - Extract intent and entities from Korean text
    - Use function calling for structured output
    - Consider conversation context
    - Handle ambiguous commands
    """

    async def extract_intent(
        self,
        transcript: str,
        context: ConversationContext
    ) -> NLUResult:
        """
        Args:
            transcript: STT output text
            context: Previous conversation context

        Returns:
            NLUResult with intent, entities, confidence
        """
```

**Function Schema** (defined in NLU Intent section below)

#### 1.5 TTS Service (`tts_service.py`)
```python
class NaverClovaTTSService:
    """
    Naver Clova Text-to-Speech integration.

    Responsibilities:
    - Convert response text to speech (Korean)
    - Cache common responses
    - Handle voice parameters (speaker, speed, pitch)
    - Return audio data for playback
    """

    async def synthesize_speech(
        self,
        text: str,
        speaker: str = "nara"
    ) -> bytes:
        """
        Args:
            text: Korean text to synthesize
            speaker: Voice model (nara, jinho, etc.)

        Returns:
            MP3 audio data
        """
```

**API Details**:
- Endpoint: `https://naveropenapi.apigw.ntruss.com/tts-premium/v1/tts`
- Method: POST
- Supported Voices: nara (female), jinho (male), etc.
- Expected Latency: <1 second for typical responses

#### 1.6 Audio Output Manager (`audio_output.py`)
```python
class AudioOutputManager:
    """
    Manages audio playback for TTS responses.

    Responsibilities:
    - Play MP3 audio through speakers
    - Handle playback queue
    - Pause microphone during playback (avoid feedback)
    - Resume listening after playback
    """
```

#### 1.7 Conversation Context Manager (`context_manager.py`)
```python
class ConversationContextManager:
    """
    Manages conversation state across multiple turns.

    Responsibilities:
    - Store last intent, entities, medicine references
    - Resolve anaphora ("이 약", "그거")
    - Maintain context TTL (30 minutes)
    - Sync context with Django backend
    """
```

#### 1.8 Django API Client (`django_client.py`)
```python
class DjangoAPIClient:
    """
    REST client for Django backend communication.

    Responsibilities:
    - Call Django API endpoints
    - Handle authentication (if needed)
    - Retry logic and error handling
    - Request/response serialization
    """

    async def get_medication_schedule(self, time_period: str) -> dict:
    async def log_medication_intake(self, schedule_id: int) -> dict:
    async def get_medication_info(self, medicine_id: int) -> dict:
    # ... more endpoints
```

### 2. Django Backend Layer

**Responsibility**: Business logic, data persistence, medication management API.

#### 2.1 New App: `voice_assistant`

**Purpose**: Handle all voice-related functionality separate from image analysis.

**Structure**:
```
voice_assistant/
├── __init__.py
├── models.py                    # Data models
├── views.py                     # Web views (if needed)
├── api_views.py                 # REST API endpoints
├── serializers.py               # DRF serializers
├── urls.py                      # URL routing
├── admin.py                     # Django admin
├── services/                    # Business logic services
│   ├── __init__.py
│   ├── schedule_service.py      # Schedule management
│   ├── log_service.py           # Medication logging
│   └── reminder_service.py      # Reminder logic
├── management/
│   └── commands/
│       └── run_voice_service.py # Voice service runner
└── tests/
    ├── test_models.py
    ├── test_api.py
    └── test_services.py
```

#### 2.2 Integration with `medicine_analyzer`

- `voice_assistant` calls `medicine_analyzer` for image-based identification
- Shared user model (Django's built-in User or custom)
- MedicationSchedule references MedicineAnalysis for linked data

---

## Voice Processing Pipeline

### Scenario 1: Simple Medication Request

**User**: "케어필 아침약 줘"

```
┌─────────────────────────────────────────────────────────────────────┐
│ STEP 1: Wake Word Detection                                        │
├─────────────────────────────────────────────────────────────────────┤
│ Audio stream → Porcupine → Wake word "케어필" detected             │
│ Latency: ~30ms                                                      │
│ Action: Start command capture (next 5 seconds)                     │
└─────────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────────┐
│ STEP 2: Command Capture                                            │
├─────────────────────────────────────────────────────────────────────┤
│ Capture audio: "아침약 줘"                                          │
│ Duration: ~2-3 seconds (voice activity detection)                  │
│ Action: Save audio buffer as WAV file                              │
└─────────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────────┐
│ STEP 3: Speech-to-Text                                             │
├─────────────────────────────────────────────────────────────────────┤
│ Input: WAV audio file                                              │
│ API: Naver Clova STT                                               │
│ Output: "아침약 줘" (confidence: 0.95)                              │
│ Latency: ~800ms                                                     │
└─────────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────────┐
│ STEP 4: Natural Language Understanding                             │
├─────────────────────────────────────────────────────────────────────┤
│ Input: "아침약 줘"                                                  │
│ Context: (none - first command)                                    │
│ API: OpenAI GPT-4 with function calling                            │
│ Output:                                                             │
│   {                                                                 │
│     "intent": "TAKE_MEDICINE",                                     │
│     "entities": {                                                   │
│       "time_period": "morning",                                    │
│       "meal_timing": null                                          │
│     },                                                              │
│     "confidence": 0.92                                             │
│   }                                                                 │
│ Latency: ~600ms                                                     │
└─────────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────────┐
│ STEP 5: Django API Call                                            │
├─────────────────────────────────────────────────────────────────────┤
│ Endpoint: POST /api/voice/medication/dispense/                     │
│ Payload: {"time_period": "morning"}                                │
│ Response:                                                           │
│   {                                                                 │
│     "status": "success",                                           │
│     "medicine": {                                                   │
│       "name": "타이레놀 500mg",                                     │
│       "dosage": "1정",                                              │
│       "schedule_id": 42                                            │
│     },                                                              │
│     "message": "아침약 타이레놀 500mg 1정을 준비했습니다"           │
│   }                                                                 │
│ Latency: ~200ms                                                     │
└─────────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────────┐
│ STEP 6: Text-to-Speech                                             │
├─────────────────────────────────────────────────────────────────────┤
│ Input: "아침약 타이레놀 500mg 1정을 준비했습니다"                   │
│ API: Naver Clova TTS                                               │
│ Output: MP3 audio data                                             │
│ Latency: ~900ms                                                     │
└─────────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────────┐
│ STEP 7: Audio Playback                                             │
├─────────────────────────────────────────────────────────────────────┤
│ Play MP3 through speakers                                          │
│ Duration: ~3 seconds                                                │
│ Action: Return to wake word listening mode                         │
└─────────────────────────────────────────────────────────────────────┘

TOTAL LATENCY: ~2.5 seconds (within <3 second target)
```

### Scenario 2: Status Check with Context

**User**: "케어필 오늘 약 먹었어?"

```
STEP 1-3: Same as above (Wake Word → Capture → STT)
  Output: "오늘 약 먹었어?"

STEP 4: NLU Processing
  Input: "오늘 약 먹었어?"
  Output: {
    "intent": "MEDICINE_STATUS",
    "entities": {
      "date": "today",
      "time_period": null  // Not specified
    },
    "confidence": 0.89
  }

STEP 5: Django API Call
  Endpoint: GET /api/voice/medication/status/?date=today
  Response: {
    "status": "success",
    "logs": [
      {"time_period": "morning", "taken": true, "taken_at": "2025-10-01T08:30:00Z"},
      {"time_period": "lunch", "taken": false, "scheduled_time": "12:00:00"},
      {"time_period": "evening", "taken": false, "scheduled_time": "19:00:00"}
    ],
    "message": "오늘 아침약은 드셨고, 점심약과 저녁약은 아직 안 드셨습니다"
  }

STEP 6-7: TTS and Playback
  Voice: "오늘 아침약은 드셨고, 점심약과 저녁약은 아직 안 드셨습니다"

CONTEXT UPDATE:
  Store last_intent="MEDICINE_STATUS", last_date="today"
  Enables follow-up: "케어필 점심약은?" (uses today context)
```

### Scenario 3: Ambiguous Command Resolution

**User**: "케어필 약 정보 알려줘"

```
STEP 4: NLU Processing
  Input: "약 정보 알려줘"
  Problem: No specific medicine mentioned

  Check Context:
    - Last medicine: "타이레놀 500mg" (from previous TAKE_MEDICINE)
    - Context age: 5 minutes (within 30-minute TTL)

  Output: {
    "intent": "MEDICINE_INFO",
    "entities": {
      "medicine_id": 42  // Resolved from context
    },
    "confidence": 0.75  // Lower due to ambiguity
  }

If NO context available:
  TTS Response: "어떤 약의 정보를 알려드릴까요?"
  Wait for clarification
```

---

## Data Models & Database Schema

### 1. MedicationSchedule Model

**Purpose**: Store user's regular medication schedule.

```python
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class MedicationSchedule(models.Model):
    """
    Represents a scheduled medication for a user.
    """
    TIME_PERIOD_CHOICES = [
        ('morning', '아침'),
        ('lunch', '점심'),
        ('evening', '저녁'),
        ('bedtime', '자기전'),
    ]

    MEAL_TIMING_CHOICES = [
        ('before', '식전'),
        ('after', '식후'),
        ('with', '식사중'),
        ('anytime', '무관'),
    ]

    # Relationships
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='medication_schedules',
        verbose_name="사용자"
    )

    medicine_analysis = models.ForeignKey(
        'medicine_analyzer.MedicineAnalysis',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='schedules',
        help_text="Link to image-analyzed medicine (if available)"
    )

    # Medicine Details
    medicine_name = models.CharField(
        max_length=200,
        verbose_name="약품명"
    )

    dosage = models.CharField(
        max_length=100,
        default="1정",
        verbose_name="복용량"
    )

    # Schedule Details
    time_period = models.CharField(
        max_length=20,
        choices=TIME_PERIOD_CHOICES,
        verbose_name="복용시간"
    )

    scheduled_time = models.TimeField(
        null=True,
        blank=True,
        help_text="Specific time (e.g., 08:00), optional",
        verbose_name="정확한 시간"
    )

    meal_timing = models.CharField(
        max_length=20,
        choices=MEAL_TIMING_CHOICES,
        default='after',
        verbose_name="식사 관계"
    )

    # Metadata
    is_active = models.BooleanField(
        default=True,
        verbose_name="활성 상태"
    )

    notes = models.TextField(
        blank=True,
        verbose_name="메모"
    )

    created_at = models.DateTimeField(
        default=timezone.now,
        verbose_name="생성일시"
    )

    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="수정일시"
    )

    class Meta:
        verbose_name = "복약 일정"
        verbose_name_plural = "복약 일정들"
        ordering = ['time_period', 'scheduled_time']
        indexes = [
            models.Index(fields=['user', 'is_active']),
            models.Index(fields=['time_period']),
        ]

    def __str__(self):
        return f"{self.user.username} - {self.medicine_name} ({self.get_time_period_display()})"
```

### 2. MedicationLog Model

**Purpose**: Track actual medication intake events.

```python
class MedicationLog(models.Model):
    """
    Records when a user actually takes their medication.
    """
    CONFIRMATION_METHOD_CHOICES = [
        ('voice', '음성 확인'),
        ('manual', '수동 입력'),
        ('auto', '자동 기록'),
    ]

    # Relationships
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='medication_logs',
        verbose_name="사용자"
    )

    schedule = models.ForeignKey(
        MedicationSchedule,
        on_delete=models.CASCADE,
        related_name='logs',
        verbose_name="일정"
    )

    # Log Details
    taken_at = models.DateTimeField(
        default=timezone.now,
        verbose_name="복용시각"
    )

    confirmation_method = models.CharField(
        max_length=20,
        choices=CONFIRMATION_METHOD_CHOICES,
        default='voice',
        verbose_name="확인방법"
    )

    # Optional: Link to voice interaction
    voice_interaction = models.ForeignKey(
        'VoiceInteraction',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='medication_logs',
        verbose_name="음성 상호작용"
    )

    notes = models.TextField(
        blank=True,
        verbose_name="메모"
    )

    class Meta:
        verbose_name = "복약 기록"
        verbose_name_plural = "복약 기록들"
        ordering = ['-taken_at']
        indexes = [
            models.Index(fields=['user', '-taken_at']),
            models.Index(fields=['schedule', '-taken_at']),
        ]

    def __str__(self):
        return f"{self.schedule.medicine_name} - {self.taken_at.strftime('%Y-%m-%d %H:%M')}"
```

### 3. VoiceInteraction Model

**Purpose**: Log all voice commands for debugging and improvement.

```python
class VoiceInteraction(models.Model):
    """
    Logs all voice interactions for debugging and analytics.
    """
    # Relationships
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='voice_interactions',
        verbose_name="사용자"
    )

    # STT Output
    transcript = models.TextField(
        verbose_name="음성인식 결과"
    )

    stt_confidence = models.FloatField(
        null=True,
        blank=True,
        help_text="STT confidence score (0.0-1.0)",
        verbose_name="STT 신뢰도"
    )

    # NLU Output
    intent = models.CharField(
        max_length=50,
        verbose_name="의도"
    )

    entities = models.JSONField(
        default=dict,
        verbose_name="엔티티"
    )

    nlu_confidence = models.FloatField(
        null=True,
        blank=True,
        help_text="NLU confidence score (0.0-1.0)",
        verbose_name="NLU 신뢰도"
    )

    # Response
    response_text = models.TextField(
        verbose_name="응답 텍스트"
    )

    # Optional: Store audio files
    audio_file = models.FileField(
        upload_to='voice_interactions/%Y/%m/%d/',
        null=True,
        blank=True,
        help_text="Original audio recording",
        verbose_name="오디오 파일"
    )

    # Performance Metrics
    processing_time_ms = models.IntegerField(
        null=True,
        blank=True,
        help_text="Total processing time in milliseconds",
        verbose_name="처리시간(ms)"
    )

    # Success Tracking
    success = models.BooleanField(
        default=True,
        verbose_name="성공 여부"
    )

    error_message = models.TextField(
        blank=True,
        verbose_name="오류 메시지"
    )

    # Metadata
    created_at = models.DateTimeField(
        default=timezone.now,
        verbose_name="생성일시"
    )

    class Meta:
        verbose_name = "음성 상호작용"
        verbose_name_plural = "음성 상호작용들"
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', '-created_at']),
            models.Index(fields=['intent']),
            models.Index(fields=['success']),
        ]

    def __str__(self):
        return f"{self.user.username} - {self.intent} - {self.created_at.strftime('%Y-%m-%d %H:%M:%S')}"
```

### 4. ConversationContext Model

**Purpose**: Maintain conversation state across turns.

```python
class ConversationContext(models.Model):
    """
    Stores conversation context for multi-turn interactions.
    Automatically expires after TTL.
    """
    # Relationships
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='conversation_context',
        verbose_name="사용자"
    )

    # Context Data
    last_intent = models.CharField(
        max_length=50,
        blank=True,
        verbose_name="마지막 의도"
    )

    last_entities = models.JSONField(
        default=dict,
        verbose_name="마지막 엔티티"
    )

    last_medicine_id = models.IntegerField(
        null=True,
        blank=True,
        help_text="Last mentioned medicine schedule ID",
        verbose_name="마지막 약 ID"
    )

    last_time_period = models.CharField(
        max_length=20,
        blank=True,
        help_text="Last mentioned time period (morning, lunch, etc.)",
        verbose_name="마지막 시간대"
    )

    # Session Management
    last_interaction_at = models.DateTimeField(
        default=timezone.now,
        verbose_name="마지막 상호작용"
    )

    expires_at = models.DateTimeField(
        verbose_name="만료시각"
    )

    class Meta:
        verbose_name = "대화 컨텍스트"
        verbose_name_plural = "대화 컨텍스트들"

    def save(self, *args, **kwargs):
        # Auto-set expiration (30 minutes from now)
        if not self.expires_at:
            from datetime import timedelta
            self.expires_at = timezone.now() + timedelta(minutes=30)
        super().save(*args, **kwargs)

    def is_expired(self):
        return timezone.now() > self.expires_at

    def refresh(self):
        """Extend expiration time"""
        from datetime import timedelta
        self.last_interaction_at = timezone.now()
        self.expires_at = timezone.now() + timedelta(minutes=30)
        self.save()

    def __str__(self):
        return f"{self.user.username} - Context"
```

### 5. ReminderSettings Model

**Purpose**: Store medication reminder preferences.

```python
class ReminderSettings(models.Model):
    """
    Configures medication reminders for a schedule.
    """
    # Relationships
    schedule = models.OneToOneField(
        MedicationSchedule,
        on_delete=models.CASCADE,
        related_name='reminder',
        verbose_name="일정"
    )

    # Reminder Configuration
    enabled = models.BooleanField(
        default=True,
        verbose_name="알림 활성화"
    )

    reminder_time = models.TimeField(
        help_text="When to trigger reminder (e.g., 08:00 for morning)",
        verbose_name="알림 시각"
    )

    snooze_duration_minutes = models.IntegerField(
        default=10,
        help_text="Snooze duration in minutes",
        verbose_name="다시 알림 간격(분)"
    )

    max_snooze_count = models.IntegerField(
        default=3,
        help_text="Maximum number of snoozes before giving up",
        verbose_name="최대 다시 알림 횟수"
    )

    # Voice Settings
    voice_reminder_enabled = models.BooleanField(
        default=True,
        help_text="Use voice reminder (TTS)",
        verbose_name="음성 알림 사용"
    )

    reminder_message = models.CharField(
        max_length=200,
        default="약 드실 시간입니다",
        verbose_name="알림 메시지"
    )

    class Meta:
        verbose_name = "알림 설정"
        verbose_name_plural = "알림 설정들"

    def __str__(self):
        return f"Reminder for {self.schedule}"
```

### Database Migrations

**Create migrations**:
```bash
python manage.py makemigrations voice_assistant
python manage.py migrate
```

---

## API Design

### REST API Endpoints

Base URL: `/api/voice/`

#### 1. Medication Schedule Endpoints

##### 1.1 List Schedules
```
GET /api/voice/schedules/

Query Parameters:
  - time_period (optional): Filter by time (morning, lunch, evening, bedtime)
  - is_active (optional): Filter active schedules (default: true)

Response:
{
  "status": "success",
  "count": 3,
  "schedules": [
    {
      "id": 1,
      "medicine_name": "타이레놀 500mg",
      "dosage": "1정",
      "time_period": "morning",
      "scheduled_time": "08:00:00",
      "meal_timing": "after",
      "is_active": true
    },
    ...
  ]
}
```

##### 1.2 Get Schedule by Time Period
```
GET /api/voice/schedules/by-time/{time_period}/

Path Parameters:
  - time_period: morning, lunch, evening, bedtime

Response:
{
  "status": "success",
  "schedule": {
    "id": 1,
    "medicine_name": "타이레놀 500mg",
    "dosage": "1정",
    "time_period": "morning",
    "meal_timing": "after"
  }
}

Error Response (404):
{
  "status": "error",
  "message": "아침 복용 일정이 없습니다"
}
```

##### 1.3 Create Schedule
```
POST /api/voice/schedules/

Request Body:
{
  "medicine_name": "타이레놀 500mg",
  "dosage": "1정",
  "time_period": "morning",
  "scheduled_time": "08:00",
  "meal_timing": "after"
}

Response (201):
{
  "status": "success",
  "schedule": {
    "id": 42,
    "medicine_name": "타이레놀 500mg",
    ...
  },
  "message": "약 일정이 등록되었습니다"
}
```

#### 2. Medication Log Endpoints

##### 2.1 Log Medication Intake
```
POST /api/voice/logs/

Request Body:
{
  "schedule_id": 1,
  "taken_at": "2025-10-01T08:30:00Z",  // Optional, defaults to now
  "confirmation_method": "voice"
}

Response (201):
{
  "status": "success",
  "log": {
    "id": 100,
    "schedule": {
      "id": 1,
      "medicine_name": "타이레놀 500mg"
    },
    "taken_at": "2025-10-01T08:30:00Z"
  },
  "message": "타이레놀 500mg 복용이 기록되었습니다"
}
```

##### 2.2 Get Medication Status
```
GET /api/voice/logs/status/

Query Parameters:
  - date (optional): YYYY-MM-DD format, defaults to today
  - time_period (optional): Filter by time

Response:
{
  "status": "success",
  "date": "2025-10-01",
  "logs": [
    {
      "time_period": "morning",
      "schedule": {
        "id": 1,
        "medicine_name": "타이레놀 500mg"
      },
      "taken": true,
      "taken_at": "2025-10-01T08:30:00Z"
    },
    {
      "time_period": "lunch",
      "schedule": {
        "id": 2,
        "medicine_name": "비타민 C"
      },
      "taken": false,
      "scheduled_time": "12:00:00"
    }
  ],
  "summary": "오늘 아침약은 드셨고, 점심약과 저녁약은 아직 안 드셨습니다"
}
```

#### 3. Medication Information Endpoints

##### 3.1 Get Medicine Info
```
GET /api/voice/medicines/{schedule_id}/

Response:
{
  "status": "success",
  "medicine": {
    "id": 1,
    "medicine_name": "타이레놀 500mg",
    "dosage": "1정",
    "time_period": "morning",
    "meal_timing": "after",
    "notes": "두통이나 발열시 복용",
    "analysis": {
      "image_url": "/media/medicine_images/...",
      "analysis_result": {...}
    }
  }
}
```

#### 4. Voice Interaction Endpoints

##### 4.1 Log Voice Interaction
```
POST /api/voice/interactions/

Request Body:
{
  "transcript": "아침약 줘",
  "stt_confidence": 0.95,
  "intent": "TAKE_MEDICINE",
  "entities": {
    "time_period": "morning"
  },
  "nlu_confidence": 0.92,
  "response_text": "아침약 타이레놀 500mg 1정을 준비했습니다",
  "processing_time_ms": 2450,
  "success": true
}

Response (201):
{
  "status": "success",
  "interaction_id": 500
}
```

#### 5. Context Management Endpoints

##### 5.1 Get Conversation Context
```
GET /api/voice/context/

Response:
{
  "status": "success",
  "context": {
    "last_intent": "TAKE_MEDICINE",
    "last_entities": {
      "time_period": "morning"
    },
    "last_medicine_id": 1,
    "last_interaction_at": "2025-10-01T08:30:00Z",
    "expires_at": "2025-10-01T09:00:00Z"
  }
}
```

##### 5.2 Update Context
```
PUT /api/voice/context/

Request Body:
{
  "last_intent": "MEDICINE_INFO",
  "last_entities": {
    "medicine_id": 1
  },
  "last_medicine_id": 1
}

Response:
{
  "status": "success",
  "message": "컨텍스트가 업데이트되었습니다"
}
```

##### 5.3 Clear Context
```
DELETE /api/voice/context/

Response:
{
  "status": "success",
  "message": "컨텍스트가 초기화되었습니다"
}
```

### Django REST Framework Implementation

**Install DRF**:
```bash
pip install djangorestframework
```

**Update settings.py**:
```python
INSTALLED_APPS = [
    ...
    'rest_framework',
    'voice_assistant',
]

REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',  # Or AllowAny for MVP
    ],
    'DEFAULT_RENDERER_CLASSES': [
        'rest_framework.renderers.JSONRenderer',
    ],
}
```

**Serializers example** (`voice_assistant/serializers.py`):
```python
from rest_framework import serializers
from .models import MedicationSchedule, MedicationLog, VoiceInteraction

class MedicationScheduleSerializer(serializers.ModelSerializer):
    class Meta:
        model = MedicationSchedule
        fields = [
            'id', 'medicine_name', 'dosage', 'time_period',
            'scheduled_time', 'meal_timing', 'is_active', 'notes'
        ]

class MedicationLogSerializer(serializers.ModelSerializer):
    schedule = MedicationScheduleSerializer(read_only=True)
    schedule_id = serializers.IntegerField(write_only=True)

    class Meta:
        model = MedicationLog
        fields = [
            'id', 'schedule', 'schedule_id', 'taken_at',
            'confirmation_method', 'notes'
        ]

class VoiceInteractionSerializer(serializers.ModelSerializer):
    class Meta:
        model = VoiceInteraction
        fields = [
            'id', 'transcript', 'stt_confidence', 'intent',
            'entities', 'nlu_confidence', 'response_text',
            'processing_time_ms', 'success', 'error_message'
        ]
```

---

## NLU Intent & Entity Schema

### Intent Definitions

#### 1. TAKE_MEDICINE
**Description**: User requests medication for a specific time period.

**Korean Variations**:
- "아침약 줘"
- "점심 약 먹어야 해"
- "저녁 약 복용해야지"
- "약 먹을 시간이야"

**Entities**:
- `time_period` (required): morning | lunch | evening | bedtime
- `meal_timing` (optional): before | after | with | anytime

**Action**:
1. Get schedule for time_period
2. Create medication log
3. Return medicine details

**Response Template**:
```
"{time_period_kr}약 {medicine_name} {dosage}을 준비했습니다"
```

#### 2. MEDICINE_STATUS
**Description**: User checks medication intake status.

**Korean Variations**:
- "오늘 약 먹었어?"
- "아침약 드셨나요?"
- "복용 기록 알려줘"
- "언제 약 먹었지?"

**Entities**:
- `date` (optional): today | yesterday | tomorrow | YYYY-MM-DD
- `time_period` (optional): morning | lunch | evening | bedtime

**Action**:
1. Query logs for date and/or time_period
2. Generate status summary

**Response Template**:
```
"{date_kr} {time_period_kr}약은 {status}. {details}"
// Example: "오늘 아침약은 드셨고, 점심약은 아직 안 드셨습니다"
```

#### 3. MEDICINE_INFO
**Description**: User requests information about a medicine.

**Korean Variations**:
- "이 약 정보 알려줘"
- "약 효능이 뭐야?"
- "복용법 알려줘"
- "부작용 있어?"

**Entities**:
- `medicine_id` (optional): Resolved from context or explicit name
- `medicine_name` (optional): Explicit medicine name

**Action**:
1. Get medicine details from schedule
2. Include image analysis data if available

**Response Template**:
```
"{medicine_name}은 {notes}. {meal_timing_kr} {dosage} 복용하시면 됩니다"
```

#### 4. ADD_MEDICINE
**Description**: User wants to add new medication to schedule.

**Korean Variations**:
- "새 약 추가해줘"
- "약 등록할게"
- "처방약 넣어줘"

**Entities**:
- `medicine_name` (optional): Extracted from speech or asked in follow-up
- `time_period` (optional): When to take
- `meal_timing` (optional): Before/after meal

**Action**:
1. Start multi-turn dialogue to collect required info
2. Create new schedule entry

**Response Template**:
```
"어떤 약을 추가하시겠어요? 약 이름을 말씀해주세요"
```

#### 5. SET_REMINDER
**Description**: User configures medication reminder.

**Korean Variations**:
- "아침 8시에 알림 설정해줘"
- "저녁약 알림 켜줘"
- "리마인더 설정"

**Entities**:
- `time_period` (required): morning | lunch | evening | bedtime
- `reminder_time` (optional): HH:MM format
- `action` (optional): enable | disable

**Action**:
1. Create or update reminder settings
2. Confirm configuration

**Response Template**:
```
"{time_period_kr} {reminder_time}에 알림이 설정되었습니다"
```

#### 6. UNKNOWN
**Description**: Fallback for unclear or out-of-scope commands.

**Action**:
1. Log as unknown intent
2. Ask for clarification

**Response Template**:
```
"죄송합니다. 무엇을 도와드릴까요? 약 복용, 기록 확인, 약 정보 등을 말씀해주세요"
```

### OpenAI Function Calling Schema

**Implementation** (`nlu_service.py`):
```python
import openai
from typing import Dict, Any

class OpenAINLUService:
    def __init__(self, api_key: str):
        self.client = openai.OpenAI(api_key=api_key)

    async def extract_intent(
        self,
        transcript: str,
        context: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        Extract intent and entities using OpenAI function calling.
        """

        # Build context-aware system message
        system_message = self._build_system_message(context)

        # Define functions (intents)
        functions = [
            {
                "name": "take_medicine",
                "description": "사용자가 약을 복용하거나 약을 요청하는 경우",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "time_period": {
                            "type": "string",
                            "enum": ["morning", "lunch", "evening", "bedtime"],
                            "description": "복용 시간대 (아침, 점심, 저녁, 자기전)"
                        },
                        "meal_timing": {
                            "type": "string",
                            "enum": ["before", "after", "with", "anytime"],
                            "description": "식사 관계 (식전, 식후, 식사중, 무관)"
                        }
                    },
                    "required": ["time_period"]
                }
            },
            {
                "name": "medicine_status",
                "description": "사용자가 복용 기록이나 상태를 확인하는 경우",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "date": {
                            "type": "string",
                            "description": "날짜 (today, yesterday, tomorrow, or YYYY-MM-DD)"
                        },
                        "time_period": {
                            "type": "string",
                            "enum": ["morning", "lunch", "evening", "bedtime"],
                            "description": "특정 시간대 (선택사항)"
                        }
                    }
                }
            },
            {
                "name": "medicine_info",
                "description": "사용자가 약 정보를 요청하는 경우",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "medicine_name": {
                            "type": "string",
                            "description": "약 이름 (명시된 경우)"
                        }
                    }
                }
            },
            {
                "name": "add_medicine",
                "description": "사용자가 새 약을 추가하려는 경우",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "medicine_name": {
                            "type": "string",
                            "description": "약 이름"
                        },
                        "time_period": {
                            "type": "string",
                            "enum": ["morning", "lunch", "evening", "bedtime"]
                        }
                    }
                }
            },
            {
                "name": "set_reminder",
                "description": "사용자가 알림을 설정하려는 경우",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "time_period": {
                            "type": "string",
                            "enum": ["morning", "lunch", "evening", "bedtime"]
                        },
                        "reminder_time": {
                            "type": "string",
                            "pattern": "^([0-1][0-9]|2[0-3]):[0-5][0-9]$",
                            "description": "알림 시각 (HH:MM)"
                        },
                        "action": {
                            "type": "string",
                            "enum": ["enable", "disable"]
                        }
                    },
                    "required": ["time_period"]
                }
            }
        ]

        # Call OpenAI API
        response = self.client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": system_message},
                {"role": "user", "content": transcript}
            ],
            functions=functions,
            function_call="auto",
            temperature=0.1
        )

        message = response.choices[0].message

        # Parse response
        if message.function_call:
            intent = message.function_call.name
            entities = json.loads(message.function_call.arguments)
            confidence = 0.9  # High confidence when function is called
        else:
            # No function matched - unknown intent
            intent = "unknown"
            entities = {}
            confidence = 0.5

        return {
            "intent": intent.upper(),
            "entities": entities,
            "confidence": confidence,
            "raw_response": message.content
        }

    def _build_system_message(self, context: Dict[str, Any] = None) -> str:
        """Build context-aware system message"""
        base_message = """당신은 한국어 약물 관리 음성 비서입니다.
사용자의 음성 명령을 분석하여 의도와 엔티티를 추출하세요.

지원하는 기능:
- 약 복용 요청 (take_medicine)
- 복용 기록 확인 (medicine_status)
- 약 정보 조회 (medicine_info)
- 새 약 추가 (add_medicine)
- 알림 설정 (set_reminder)
"""

        if context:
            context_info = f"\n현재 대화 컨텍스트:\n"
            if context.get('last_medicine_id'):
                context_info += f"- 마지막 언급된 약: ID {context['last_medicine_id']}\n"
            if context.get('last_time_period'):
                context_info += f"- 마지막 시간대: {context['last_time_period']}\n"
            base_message += context_info

        return base_message
```

### Entity Normalization

**Korean to English Mapping**:
```python
TIME_PERIOD_MAP = {
    "아침": "morning",
    "점심": "lunch",
    "저녁": "evening",
    "자기전": "bedtime",
    "밤": "bedtime",
    # Variations
    "아침에": "morning",
    "점심때": "lunch",
    "저녁에": "evening",
}

MEAL_TIMING_MAP = {
    "식전": "before",
    "식후": "after",
    "식사중": "with",
    "무관": "anytime",
    # Variations
    "밥먹기전": "before",
    "밥먹고": "after",
}

DATE_MAP = {
    "오늘": "today",
    "어제": "yesterday",
    "내일": "tomorrow",
    "그제": "day_before_yesterday",
}
```

---

## Error Handling Strategy

### 1. STT Failures

**Scenarios**:
- Network timeout
- Naver API rate limit
- Poor audio quality (low confidence)

**Strategy**:
```python
async def transcribe_with_retry(audio_data: bytes, max_retries=2):
    """
    Retry STT with exponential backoff
    """
    for attempt in range(max_retries):
        try:
            result = await stt_service.transcribe_audio(audio_data)

            # Check confidence
            if result['confidence'] < 0.6:
                return {
                    "success": False,
                    "error": "LOW_CONFIDENCE",
                    "tts_message": "죄송합니다. 정확히 듣지 못했습니다. 다시 말씀해주시겠어요?"
                }

            return {
                "success": True,
                "transcript": result['text'],
                "confidence": result['confidence']
            }

        except NetworkError as e:
            if attempt < max_retries - 1:
                await asyncio.sleep(2 ** attempt)  # Exponential backoff
            else:
                return {
                    "success": False,
                    "error": "NETWORK_ERROR",
                    "tts_message": "네트워크 오류가 발생했습니다. 잠시 후 다시 시도해주세요"
                }
```

### 2. NLU Low Confidence

**Threshold**: confidence < 0.7

**Strategy**: Clarification dialogue
```python
async def handle_low_confidence_nlu(nlu_result, transcript):
    """
    Ask clarifying questions for low confidence NLU
    """
    if nlu_result['confidence'] < 0.7:
        intent = nlu_result['intent']

        if intent == "TAKE_MEDICINE":
            # Confirm time period
            time_period = nlu_result['entities'].get('time_period')
            time_period_kr = TIME_PERIOD_MAP_REVERSE[time_period]

            return {
                "action": "CLARIFY",
                "tts_message": f"{time_period_kr}약을 드시려는 건가요?",
                "expected_response": "yes_no",
                "context": nlu_result
            }

        elif intent == "UNKNOWN":
            return {
                "action": "CLARIFY",
                "tts_message": "무엇을 도와드릴까요? 약 복용, 기록 확인, 또는 약 정보를 말씀해주세요",
                "expected_response": "command"
            }

    return None  # Proceed with normal flow
```

### 3. Network Failures

**Strategy**: Queue commands for retry
```python
class CommandQueue:
    """
    Queue failed commands for retry when network is restored
    """
    def __init__(self):
        self.queue = []

    def enqueue(self, command_data):
        self.queue.append({
            "timestamp": datetime.now(),
            "command": command_data
        })

    async def retry_all(self):
        """Retry all queued commands"""
        for item in self.queue:
            try:
                await process_command(item['command'])
                self.queue.remove(item)
            except NetworkError:
                break  # Network still down, stop retrying
```

### 4. Ambiguous Commands

**Scenario**: User says "약 정보 알려줘" without specifying which medicine.

**Strategy**: Context resolution or clarification
```python
async def resolve_ambiguous_medicine(entities, context):
    """
    Resolve medicine reference using context
    """
    medicine_id = entities.get('medicine_id')
    medicine_name = entities.get('medicine_name')

    # Try context first
    if not medicine_id and not medicine_name:
        if context and context.get('last_medicine_id'):
            # Use context
            if (datetime.now() - context['last_interaction_at']).seconds < 1800:
                return context['last_medicine_id']

        # No context - ask user
        return {
            "action": "CLARIFY",
            "tts_message": "어떤 약의 정보를 알려드릤까요?"
        }

    return medicine_id or medicine_name
```

### 5. API Rate Limits

**Strategy**: Exponential backoff and user notification
```python
class RateLimiter:
    """
    Handle API rate limits with exponential backoff
    """
    def __init__(self):
        self.retry_delays = [1, 2, 4, 8, 16]  # seconds

    async def call_with_backoff(self, api_func, *args, **kwargs):
        for delay in self.retry_delays:
            try:
                return await api_func(*args, **kwargs)
            except RateLimitError:
                await asyncio.sleep(delay)

        # All retries failed
        raise RateLimitExceeded("API rate limit exceeded. Please try again later.")
```

### 6. Voice Service Crash Recovery

**Strategy**: Persistent state management
```python
class StateManager:
    """
    Persist critical state to disk for crash recovery
    """
    def __init__(self, state_file="voice_service_state.json"):
        self.state_file = state_file

    def save_state(self, state_data):
        with open(self.state_file, 'w') as f:
            json.dump(state_data, f)

    def restore_state(self):
        if os.path.exists(self.state_file):
            with open(self.state_file, 'r') as f:
                return json.load(f)
        return None
```

---

## Performance Optimization

### 1. Audio Buffering Strategy

**Circular Buffer** for efficient memory usage:
```python
import numpy as np
from collections import deque

class CircularAudioBuffer:
    """
    Rolling 5-second audio buffer for wake word context capture
    """
    def __init__(self, sample_rate=16000, buffer_duration_sec=5):
        self.sample_rate = sample_rate
        self.buffer_size = sample_rate * buffer_duration_sec
        self.buffer = deque(maxlen=self.buffer_size)

    def append(self, audio_chunk):
        """Add audio chunk to buffer"""
        self.buffer.extend(audio_chunk)

    def get_buffer(self):
        """Get entire buffer as numpy array"""
        return np.array(self.buffer, dtype=np.int16)

    def get_last_n_seconds(self, seconds):
        """Get last N seconds of audio"""
        samples = self.sample_rate * seconds
        return np.array(list(self.buffer)[-samples:], dtype=np.int16)
```

### 2. TTS Response Caching

**Cache common responses** to avoid repeated API calls:
```python
import hashlib
from functools import lru_cache

class TTSCache:
    """
    Cache TTS audio for common phrases
    """
    def __init__(self, cache_dir="tts_cache"):
        self.cache_dir = cache_dir
        os.makedirs(cache_dir, exist_ok=True)

    def get_cache_key(self, text, speaker):
        """Generate cache key from text and speaker"""
        content = f"{text}:{speaker}"
        return hashlib.md5(content.encode()).hexdigest()

    def get(self, text, speaker):
        """Get cached TTS audio"""
        key = self.get_cache_key(text, speaker)
        cache_path = os.path.join(self.cache_dir, f"{key}.mp3")

        if os.path.exists(cache_path):
            with open(cache_path, 'rb') as f:
                return f.read()
        return None

    def set(self, text, speaker, audio_data):
        """Cache TTS audio"""
        key = self.get_cache_key(text, speaker)
        cache_path = os.path.join(self.cache_dir, f"{key}.mp3")

        with open(cache_path, 'wb') as f:
            f.write(audio_data)

# Pre-cache common responses
COMMON_RESPONSES = [
    "네, 알겠습니다",
    "약 복용 기록되었습니다",
    "죄송합니다. 다시 말씀해주시겠어요?",
    "무엇을 도와드릴까요?",
]
```

### 3. Async API Calls

**Parallel processing** for STT and NLU:
```python
async def process_voice_command(audio_data, context):
    """
    Process voice command with parallel API calls where possible
    """
    # Step 1: STT (must complete first)
    stt_result = await stt_service.transcribe_audio(audio_data)

    if not stt_result['success']:
        return handle_stt_error(stt_result)

    transcript = stt_result['transcript']

    # Step 2 & 3: Parallel NLU and context fetch
    nlu_task = asyncio.create_task(
        nlu_service.extract_intent(transcript, context)
    )
    context_task = asyncio.create_task(
        django_client.get_context()
    )

    nlu_result, fresh_context = await asyncio.gather(nlu_task, context_task)

    # Step 4: Django API call based on intent
    api_result = await process_intent(nlu_result, fresh_context)

    # Step 5: TTS (final step)
    tts_audio = await tts_service.synthesize_speech(api_result['message'])

    return tts_audio
```

### 4. Connection Pooling

**Reuse HTTP connections**:
```python
import aiohttp

class APIClient:
    """
    HTTP client with connection pooling
    """
    def __init__(self):
        self.session = None

    async def __aenter__(self):
        connector = aiohttp.TCPConnector(
            limit=10,  # Max 10 connections
            ttl_dns_cache=300  # 5-minute DNS cache
        )
        timeout = aiohttp.ClientTimeout(total=10)
        self.session = aiohttp.ClientSession(
            connector=connector,
            timeout=timeout
        )
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.session.close()

    async def post(self, url, **kwargs):
        async with self.session.post(url, **kwargs) as response:
            return await response.json()
```

### 5. Latency Budget Monitoring

**Track performance** in real-time:
```python
import time
from dataclasses import dataclass

@dataclass
class LatencyMetrics:
    wake_word_ms: float
    audio_capture_ms: float
    stt_ms: float
    nlu_ms: float
    api_ms: float
    tts_ms: float
    total_ms: float

    def __str__(self):
        return f"""
Latency Breakdown:
  Wake Word:     {self.wake_word_ms:>6.0f} ms
  Audio Capture: {self.audio_capture_ms:>6.0f} ms
  STT:           {self.stt_ms:>6.0f} ms
  NLU:           {self.nlu_ms:>6.0f} ms
  API:           {self.api_ms:>6.0f} ms
  TTS:           {self.tts_ms:>6.0f} ms
  ─────────────────────────────
  TOTAL:         {self.total_ms:>6.0f} ms
  Target:        < 3000 ms
"""

class PerformanceTracker:
    """Track latency for each pipeline stage"""

    def __init__(self):
        self.metrics = {}

    def start_timer(self, stage):
        self.metrics[stage] = time.time()

    def end_timer(self, stage):
        if stage in self.metrics:
            elapsed = (time.time() - self.metrics[stage]) * 1000
            return elapsed
        return 0

    def get_metrics(self):
        return LatencyMetrics(
            wake_word_ms=self.metrics.get('wake_word', 0),
            audio_capture_ms=self.metrics.get('audio_capture', 0),
            stt_ms=self.metrics.get('stt', 0),
            nlu_ms=self.metrics.get('nlu', 0),
            api_ms=self.metrics.get('api', 0),
            tts_ms=self.metrics.get('tts', 0),
            total_ms=self.metrics.get('total', 0)
        )
```

### 6. Resource Usage Optimization

**Sleep mode** when inactive:
```python
class PowerManager:
    """
    Manage system resources based on activity
    """
    IDLE_THRESHOLD_MINUTES = 10

    def __init__(self):
        self.last_activity = time.time()
        self.sleep_mode = False

    def record_activity(self):
        self.last_activity = time.time()
        if self.sleep_mode:
            self.wake_up()

    def check_idle(self):
        idle_minutes = (time.time() - self.last_activity) / 60
        if idle_minutes > self.IDLE_THRESHOLD_MINUTES and not self.sleep_mode:
            self.enter_sleep_mode()

    def enter_sleep_mode(self):
        """Reduce CPU usage when idle"""
        print("Entering sleep mode (reduced wake word sensitivity)")
        self.sleep_mode = True
        # Reduce wake word check frequency from 32ms to 100ms

    def wake_up(self):
        """Resume normal operation"""
        print("Waking up (full wake word sensitivity)")
        self.sleep_mode = False
```

---

## Deployment Architecture

### Development Setup (MVP)

**Architecture**: Django Management Command

```
┌─────────────────────────────────────────┐
│   Terminal 1: Django Development       │
│   python manage.py runserver           │
└─────────────────────────────────────────┘

┌─────────────────────────────────────────┐
│   Terminal 2: Voice Service            │
│   python manage.py run_voice_service   │
└─────────────────────────────────────────┘
```

**Pros**:
- Simple to develop and debug
- Single codebase
- Easy Django integration

**Cons**:
- No auto-restart on crash
- Manual process management
- Not production-ready

**Setup**:
```bash
# Install dependencies
pip install pyaudio pvporcupine requests aiohttp

# Run Django server
python manage.py runserver

# Run voice service (in another terminal)
python manage.py run_voice_service
```

### Production Deployment (Recommended)

**Architecture**: Systemd Service (Linux) or Windows Service

```
┌──────────────────────────────────────────────────┐
│              Load Balancer (Nginx)               │
│                                                  │
│    ┌─────────────────────────────────────────┐  │
│    │   Django Application (Gunicorn/uWSGI)   │  │
│    │   Port 8000                              │  │
│    │   - REST API endpoints                   │  │
│    │   - Database access                      │  │
│    └─────────────────────────────────────────┘  │
│                                                  │
│    ┌─────────────────────────────────────────┐  │
│    │   Voice Service (Systemd/Windows Svc)   │  │
│    │   - Always running                       │  │
│    │   - Auto-restart on crash                │  │
│    │   - Logging to syslog/Event Log          │  │
│    │   - Calls Django API via HTTP            │  │
│    └─────────────────────────────────────────┘  │
└──────────────────────────────────────────────────┘
```

#### Systemd Service (Linux)

**File**: `/etc/systemd/system/carepill-voice.service`
```ini
[Unit]
Description=CarePill Voice Assistant Service
After=network.target

[Service]
Type=simple
User=carepill
WorkingDirectory=/opt/carepill
ExecStart=/opt/carepill/venv/bin/python manage.py run_voice_service
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal

# Environment variables
Environment="DJANGO_SETTINGS_MODULE=medicine_project.settings"
Environment="OPENAI_API_KEY=your-key-here"
Environment="NAVER_CLIENT_ID=your-id-here"
Environment="NAVER_CLIENT_SECRET=your-secret-here"

[Install]
WantedBy=multi-user.target
```

**Commands**:
```bash
# Enable service
sudo systemctl enable carepill-voice

# Start service
sudo systemctl start carepill-voice

# Check status
sudo systemctl status carepill-voice

# View logs
sudo journalctl -u carepill-voice -f
```

#### Windows Service

**Use NSSM (Non-Sucking Service Manager)**:
```cmd
# Install NSSM
choco install nssm

# Create service
nssm install CarePillVoice "C:\CarePill\venv\Scripts\python.exe" "C:\CarePill\manage.py run_voice_service"

# Set working directory
nssm set CarePillVoice AppDirectory "C:\CarePill"

# Set environment variables
nssm set CarePillVoice AppEnvironmentExtra DJANGO_SETTINGS_MODULE=medicine_project.settings

# Start service
nssm start CarePillVoice
```

### Docker Deployment (Optional)

**docker-compose.yml**:
```yaml
version: '3.8'

services:
  django:
    build: .
    command: gunicorn medicine_project.wsgi:application --bind 0.0.0.0:8000
    volumes:
      - ./:/app
      - static_volume:/app/staticfiles
      - media_volume:/app/media
    ports:
      - "8000:8000"
    env_file:
      - .env
    depends_on:
      - db

  voice_service:
    build: .
    command: python manage.py run_voice_service
    volumes:
      - ./:/app
    devices:
      - /dev/snd:/dev/snd  # Audio device access
    env_file:
      - .env
    depends_on:
      - django
    restart: unless-stopped

  db:
    image: postgres:15
    volumes:
      - postgres_data:/var/lib/postgresql/data
    environment:
      - POSTGRES_DB=carepill
      - POSTGRES_USER=carepill
      - POSTGRES_PASSWORD=secure_password

volumes:
  postgres_data:
  static_volume:
  media_volume:
```

### Environment Configuration

**.env file**:
```env
# Django Settings
SECRET_KEY=your-secret-key-here
DEBUG=False
ALLOWED_HOSTS=localhost,127.0.0.1,yourdomain.com

# Database
DATABASE_URL=postgresql://carepill:password@db:5432/carepill

# API Keys
OPENAI_API_KEY=sk-...
NAVER_CLIENT_ID=your-naver-client-id
NAVER_CLIENT_SECRET=your-naver-client-secret
PORCUPINE_ACCESS_KEY=your-porcupine-key

# Voice Service Settings
VOICE_WAKE_WORD_SENSITIVITY=0.5
VOICE_COMMAND_TIMEOUT_SEC=5
VOICE_TTS_SPEAKER=nara

# Logging
LOG_LEVEL=INFO
```

---

## Implementation Roadmap

### Phase 1: Foundation (Week 1-2)

**Goal**: Set up project structure and basic voice processing.

**Tasks**:
1. Create `voice_assistant` Django app
2. Define data models (MedicationSchedule, MedicationLog, etc.)
3. Run migrations
4. Set up Naver Clova API credentials
5. Test STT API with sample audio
6. Test TTS API with sample text
7. Set up Porcupine wake word (free tier with English wake word for testing)

**Deliverables**:
- Working Django app structure
- Database schema created
- API credentials configured
- Basic STT/TTS working

### Phase 2: Voice Pipeline (Week 3-4)

**Goal**: Build end-to-end voice processing pipeline.

**Tasks**:
1. Implement audio input manager (PyAudio)
2. Integrate Porcupine wake word detector
3. Implement circular audio buffer
4. Build STT service with Naver Clova
5. Build TTS service with Naver Clova
6. Implement audio output manager
7. Create basic command loop (wake word → STT → mock response → TTS)

**Deliverables**:
- Working voice input/output
- Wake word detection functional
- Basic "hello world" voice interaction

### Phase 3: NLU Integration (Week 5)

**Goal**: Add natural language understanding with OpenAI.

**Tasks**:
1. Implement OpenAI NLU service with function calling
2. Define all intent functions (see NLU section)
3. Implement entity extraction
4. Test with various Korean command variations
5. Implement conversation context manager
6. Test context-aware commands

**Deliverables**:
- Intent recognition working
- Entity extraction accurate
- Context maintained across turns

### Phase 4: Django API (Week 6)

**Goal**: Build REST API for medication operations.

**Tasks**:
1. Install Django REST Framework
2. Create serializers for all models
3. Implement API views (schedules, logs, context, etc.)
4. Write API tests
5. Document API endpoints
6. Build Django API client for voice service

**Deliverables**:
- REST API fully functional
- API tests passing
- Voice service can call Django API

### Phase 5: Integration (Week 7)

**Goal**: Connect all components into working system.

**Tasks**:
1. Integrate voice pipeline with Django API
2. Implement error handling (all scenarios)
3. Add retry logic and fallbacks
4. Implement performance tracking
5. Add TTS caching for common responses
6. Test end-to-end scenarios

**Deliverables**:
- Complete voice-to-database flow
- Error handling robust
- Performance meeting <3s target

### Phase 6: Testing & Optimization (Week 8)

**Goal**: Comprehensive testing and performance tuning.

**Tasks**:
1. Unit tests for all services
2. Integration tests for API endpoints
3. Voice interaction tests with real audio
4. Load testing (multiple concurrent requests)
5. Latency optimization
6. Memory profiling and leak detection
7. Create test dataset (Korean commands)

**Deliverables**:
- Test coverage >80%
- All tests passing
- Performance benchmarks documented

### Phase 7: Production Preparation (Week 9-10)

**Goal**: Prepare for deployment.

**Tasks**:
1. Set up systemd service configuration
2. Implement logging (structured logging with JSON)
3. Add monitoring (health checks, metrics)
4. Create deployment documentation
5. Set up PostgreSQL (migrate from SQLite)
6. Configure Gunicorn/uWSGI for Django
7. Set up Nginx reverse proxy
8. SSL certificates (Let's Encrypt)

**Deliverables**:
- Production-ready deployment
- Monitoring dashboard
- Deployment documentation

### Phase 8: Custom Wake Word (Week 11)

**Goal**: Train and deploy custom "케어필" wake word.

**Tasks**:
1. Record 100+ samples of "케어필" (various speakers)
2. Use Porcupine Console to train custom model
3. Download .ppn model file
4. Integrate custom model into voice service
5. Test wake word accuracy (false positive/negative rates)
6. Tune sensitivity parameter

**Deliverables**:
- Custom "케어필" wake word working
- Acceptable accuracy metrics

---

## File Structure & Code Organization

### Complete Project Structure

```
CarePill/
├── manage.py
├── requirements.txt
├── .env
├── .gitignore
├── README.md
│
├── medicine_project/           # Django project settings
│   ├── __init__.py
│   ├── settings.py             # Updated with REST_FRAMEWORK, new apps
│   ├── urls.py                 # Include voice_assistant URLs
│   ├── wsgi.py
│   └── asgi.py
│
├── medicine_analyzer/          # Existing app (image analysis)
│   ├── __init__.py
│   ├── models.py               # MedicineAnalysis model
│   ├── views.py
│   ├── urls.py
│   ├── admin.py
│   └── migrations/
│
├── voice_assistant/            # NEW: Voice interaction app
│   ├── __init__.py
│   ├── models.py               # MedicationSchedule, MedicationLog, etc.
│   ├── admin.py
│   ├── apps.py
│   │
│   ├── api/                    # REST API
│   │   ├── __init__.py
│   │   ├── views.py            # API ViewSets
│   │   ├── serializers.py      # DRF Serializers
│   │   └── urls.py             # API URL routing
│   │
│   ├── services/               # Business logic
│   │   ├── __init__.py
│   │   ├── stt_service.py      # Naver Clova STT
│   │   ├── tts_service.py      # Naver Clova TTS
│   │   ├── nlu_service.py      # OpenAI NLU
│   │   ├── schedule_service.py # Schedule management
│   │   ├── log_service.py      # Medication logging
│   │   └── context_service.py  # Conversation context
│   │
│   ├── voice/                  # Voice processing
│   │   ├── __init__.py
│   │   ├── audio_manager.py    # Audio input/output
│   │   ├── wake_word.py        # Porcupine integration
│   │   ├── audio_buffer.py     # Circular buffer
│   │   ├── pipeline.py         # Main voice pipeline
│   │   └── django_client.py    # Django API client
│   │
│   ├── management/
│   │   └── commands/
│   │       └── run_voice_service.py  # Django command to run voice service
│   │
│   ├── migrations/
│   │   └── 0001_initial.py
│   │
│   ├── tests/
│   │   ├── __init__.py
│   │   ├── test_models.py
│   │   ├── test_api.py
│   │   ├── test_services.py
│   │   └── test_voice_pipeline.py
│   │
│   └── utils/
│       ├── __init__.py
│       ├── constants.py        # TIME_PERIOD_MAP, etc.
│       ├── performance.py      # LatencyMetrics
│       └── errors.py           # Custom exceptions
│
├── static/                     # Static files
│   └── ...
│
├── media/                      # Media files
│   ├── medicine_images/
│   └── voice_interactions/
│
├── templates/                  # Django templates
│   └── ...
│
├── tts_cache/                  # Cached TTS audio
│   └── *.mp3
│
├── voice_models/               # Porcupine models
│   └── carepill_ko_linux.ppn
│
├── logs/                       # Application logs
│   ├── django.log
│   └── voice_service.log
│
└── claudedocs/                 # Documentation
    ├── voice_architecture.md   # This document
    ├── api_documentation.md
    └── deployment_guide.md
```

### Key Files to Create

#### 1. `voice_assistant/management/commands/run_voice_service.py`

```python
from django.core.management.base import BaseCommand
from voice_assistant.voice.pipeline import VoicePipeline
import asyncio

class Command(BaseCommand):
    help = 'Run the voice assistant service'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Starting Voice Assistant Service...'))

        try:
            # Initialize and run voice pipeline
            pipeline = VoicePipeline()
            asyncio.run(pipeline.run())
        except KeyboardInterrupt:
            self.stdout.write(self.style.WARNING('\nShutting down Voice Assistant Service...'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error: {e}'))
```

#### 2. `voice_assistant/voice/pipeline.py`

```python
import asyncio
from .audio_manager import AudioInputManager, AudioOutputManager
from .wake_word import WakeWordDetector
from ..services.stt_service import NaverClovaSTTService
from ..services.nlu_service import OpenAINLUService
from ..services.tts_service import NaverClovaTTSService
from .django_client import DjangoAPIClient

class VoicePipeline:
    """
    Main voice processing pipeline orchestrator
    """
    def __init__(self):
        self.audio_input = AudioInputManager()
        self.audio_output = AudioOutputManager()
        self.wake_word = WakeWordDetector()
        self.stt = NaverClovaSTTService()
        self.nlu = OpenAINLUService()
        self.tts = NaverClovaTTSService()
        self.api = DjangoAPIClient()

        self.running = False

    async def run(self):
        """Main event loop"""
        self.running = True
        print("🎤 Voice Assistant is listening...")
        print("Say '케어필' to wake up")

        try:
            while self.running:
                # Step 1: Wait for wake word
                audio_chunk = self.audio_input.read_chunk()

                if self.wake_word.detect(audio_chunk):
                    print("👂 Wake word detected!")
                    await self.process_command()

        except KeyboardInterrupt:
            self.running = False
            print("\n👋 Goodbye!")

    async def process_command(self):
        """Process voice command after wake word"""
        # Capture command audio
        command_audio = self.audio_input.capture_command(duration_sec=5)

        # STT
        transcript = await self.stt.transcribe(command_audio)
        print(f"📝 Heard: {transcript}")

        # NLU
        nlu_result = await self.nlu.extract_intent(transcript)
        print(f"🧠 Intent: {nlu_result['intent']}")

        # Call Django API
        api_response = await self.api.handle_intent(nlu_result)

        # TTS
        response_audio = await self.tts.synthesize(api_response['message'])

        # Play response
        self.audio_output.play(response_audio)
```

#### 3. `voice_assistant/api/views.py`

```python
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from ..models import MedicationSchedule, MedicationLog
from .serializers import MedicationScheduleSerializer, MedicationLogSerializer

class MedicationScheduleViewSet(viewsets.ModelViewSet):
    queryset = MedicationSchedule.objects.all()
    serializer_class = MedicationScheduleSerializer

    @action(detail=False, methods=['get'])
    def by_time(self, request):
        """Get schedule by time period"""
        time_period = request.query_params.get('time_period')

        try:
            schedule = MedicationSchedule.objects.get(
                time_period=time_period,
                is_active=True
            )
            serializer = self.get_serializer(schedule)
            return Response({
                'status': 'success',
                'schedule': serializer.data
            })
        except MedicationSchedule.DoesNotExist:
            return Response({
                'status': 'error',
                'message': f'{time_period} 복용 일정이 없습니다'
            }, status=status.HTTP_404_NOT_FOUND)

class MedicationLogViewSet(viewsets.ModelViewSet):
    queryset = MedicationLog.objects.all()
    serializer_class = MedicationLogSerializer

    @action(detail=False, methods=['get'])
    def status(self, request):
        """Get medication status for a date"""
        date = request.query_params.get('date', 'today')
        # Implementation here
        pass
```

---

## Conclusion

This architecture provides a comprehensive, scalable foundation for adding voice-first interaction to the CarePill Django application. The design prioritizes:

1. **Separation of Concerns**: Voice processing is isolated from business logic
2. **Performance**: <3 second latency through async processing and caching
3. **Reliability**: Robust error handling and retry mechanisms
4. **Maintainability**: Clean code organization and comprehensive testing
5. **Scalability**: Independent scaling of voice service and Django backend

### Next Steps

1. Review this architecture with stakeholders
2. Set up development environment
3. Begin Phase 1 implementation (Foundation)
4. Iterate based on testing and user feedback

### Contact & Support

For questions or clarifications about this architecture, please refer to:
- Django documentation: https://docs.djangoproject.com/
- Naver Clova API: https://www.ncloud.com/product/aiService/clovaSpeech
- Porcupine: https://picovoice.ai/platform/porcupine/
- OpenAI API: https://platform.openai.com/docs/

---

**Document End**
