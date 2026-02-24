# DeepSafe AI System Prompts Reference

This document catalogs all AI/LLM system prompts used across DeepSafe's detection systems.

---

## Social Engineering Analysis Prompt

**Used by:** `GPT4Analyzer` (OpenAI API), `OllamaAnalyzer` (local Ollama)
**Source:** `src/services/detection/social_engineering/prompts.py`

### System Prompt

```
You are a security analyst specializing in detecting social engineering attacks in business communications. Your role is to analyze conversation transcripts and identify potential threats.

Analyze the provided conversation for:
1. Social engineering tactics (urgency, authority, reciprocity, scarcity, social proof)
2. Business Email Compromise (BEC) indicators
3. Fraudulent intent (payment redirect, credential theft, data exfiltration)
4. Manipulation techniques (emotional manipulation, pressure tactics)
5. Impersonation attempts

Respond with a JSON object containing:
{
    "is_suspicious": boolean,
    "confidence": number (0-100),
    "intent_classification": string (legitimate|suspicious|malicious|unknown),
    "manipulation_tactics": [list of identified tactics],
    "risk_assessment": string (low|medium|high|critical),
    "reasoning": string (explanation of analysis),
    "recommendations": [list of recommended actions]
}

Be thorough but avoid false positives. Consider business context and normal communication patterns.
```

### User Prompt Template

Built by `build_analysis_prompt()` in `prompts.py`:

```
Analyze the following conversation for social engineering indicators:

Meeting Context:
- Title: {meeting_context['title']}
- Scheduled: {meeting_context['scheduled']}
- Organizer: {meeting_context['organizer']}

Participant Information:
- {name}: {info}

Conversation Transcript:
```
{transcript}
```

Provide your analysis in JSON format.
```

### Expected JSON Response Schema

| Field | Type | Values | Description |
|-------|------|--------|-------------|
| `is_suspicious` | boolean | `true`/`false` | Whether the conversation contains social engineering indicators |
| `confidence` | number | 0-100 | Confidence score of the assessment |
| `intent_classification` | string | `legitimate`, `suspicious`, `malicious`, `unknown` | Classification of the conversation intent |
| `manipulation_tactics` | string[] | e.g., `["urgency", "authority"]` | List of detected manipulation tactics |
| `risk_assessment` | string | `low`, `medium`, `high`, `critical` | Overall risk level |
| `reasoning` | string | Free text | Explanation of the analysis decision |
| `recommendations` | string[] | Free text list | Suggested actions to take |

---

## Model Configuration

### GPT-4 (API Mode)

- **Model:** `gpt-4-turbo-preview` (configurable via `OPENAI_MODEL`)
- **Temperature:** `0.3` (lower for consistent analysis)
- **Max Tokens:** `1000`
- **Response Format:** JSON object

### Ollama (Local Mode)

- **Model:** `phi3:mini` (configurable via `DETECTION_OLLAMA_MODEL`)
- **Endpoint:** `http://localhost:11434/api/chat`
- **Format:** JSON
- **Stream:** `false`

---

## Detection Models (Non-Prompt-Based)

These models use ML inference rather than prompts:

### Wav2Vec2 (Audio Deepfake Detection)
- **Model:** `facebook/wav2vec2-base` (configurable via `DETECTION_AUDIO_MODEL`)
- **Task:** Binary classification (real vs. synthetic speech)
- **Fallback:** Statistical feature analysis (zero-crossing rate, energy variance)

### EfficientNet-B4 (Video Deepfake Detection)
- **Model:** `google/efficientnet-b4` (configurable via `DETECTION_VIDEO_MODEL`)
- **Task:** Image classification used for anomaly scoring
- **Fallback:** Pixel-based analysis (channel correlation, noise patterns, edge density)

### Whisper (Audio Transcription)
- **Model:** `small` (configurable via `DETECTION_WHISPER_MODEL_SIZE`)
- **Library:** `faster-whisper`
- **Task:** Speech-to-text transcription
- **Compute:** INT8 on CPU, FP16 on GPU

---

## Manipulation Tactics Dictionary

Used by `GPT4Analyzer.get_manipulation_tactic_description()`:

| Tactic | Description |
|--------|-------------|
| `urgency` | Creating artificial time pressure to force quick decisions |
| `authority` | Claiming or implying authority to compel compliance |
| `reciprocity` | Creating false sense of obligation |
| `scarcity` | Implying limited availability or time |
| `social_proof` | Claiming others have already complied |
| `liking` | Building false rapport or trust |
| `commitment` | Using prior commitments to manipulate |
| `fear` | Using fear or threats to compel action |
| `greed` | Appealing to desire for gain |
| `helpfulness` | Exploiting desire to be helpful |
