"""
MongoDB Connection Module

Provides MongoDB client for document storage (transcripts, forensic evidence).
"""

from typing import Any, Dict, List, Optional

from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from pymongo import ASCENDING, DESCENDING

from src.shared.config import get_settings


class MongoDBClient:
    """
    MongoDB client wrapper with common operations.

    Handles connections to MongoDB for storing:
    - Meeting transcripts with risk analysis
    - Forensic evidence (audio/video analysis details)
    """

    def __init__(self, client: AsyncIOMotorClient, database: AsyncIOMotorDatabase):
        self._client = client
        self._db = database

    @property
    def client(self) -> AsyncIOMotorClient:
        """Get the underlying MongoDB client."""
        return self._client

    @property
    def db(self) -> AsyncIOMotorDatabase:
        """Get the database instance."""
        return self._db

    # Collection accessors
    @property
    def transcripts(self):
        """Get the transcripts collection."""
        return self._db.transcripts

    @property
    def forensic_evidence(self):
        """Get the forensic evidence collection."""
        return self._db.forensic_evidence

    @property
    def detection_results(self):
        """Get the detection results collection."""
        return self._db.detection_results

    # Transcript operations
    async def insert_transcript_segment(
        self,
        meeting_id: str,
        participant_id: str,
        text: str,
        timestamp: float,
        risk_indicators: Dict[str, Any],
    ) -> str:
        """
        Insert a transcript segment with risk analysis.

        Returns:
            str: The inserted document ID.
        """
        document = {
            "meeting_id": meeting_id,
            "participant_id": participant_id,
            "text": text,
            "timestamp": timestamp,
            "risk_indicators": risk_indicators,
            "created_at": timestamp,
        }
        result = await self.transcripts.insert_one(document)
        return str(result.inserted_id)

    async def get_meeting_transcript(
        self,
        meeting_id: str,
        limit: Optional[int] = None,
        skip: int = 0,
    ) -> List[Dict[str, Any]]:
        """
        Get transcript segments for a meeting.

        Args:
            meeting_id: The meeting identifier.
            limit: Maximum number of segments to return.
            skip: Number of segments to skip.

        Returns:
            List of transcript segments ordered by timestamp.
        """
        cursor = self.transcripts.find({"meeting_id": meeting_id}).sort(
            "timestamp", ASCENDING
        )

        if skip > 0:
            cursor = cursor.skip(skip)
        if limit:
            cursor = cursor.limit(limit)

        return await cursor.to_list(length=limit or 1000)

    async def get_risky_segments(
        self,
        meeting_id: str,
        min_risk_score: float = 0.5,
    ) -> List[Dict[str, Any]]:
        """
        Get transcript segments with risk score above threshold.
        """
        cursor = self.transcripts.find(
            {
                "meeting_id": meeting_id,
                "risk_indicators.composite_score": {"$gte": min_risk_score},
            }
        ).sort("timestamp", ASCENDING)

        return await cursor.to_list(length=1000)

    # Forensic evidence operations
    async def store_forensic_evidence(
        self,
        meeting_id: str,
        incident_id: str,
        evidence_type: str,
        analysis_results: Dict[str, Any],
        raw_data_reference: Optional[str] = None,
    ) -> str:
        """
        Store forensic evidence for an incident.

        Args:
            meeting_id: The meeting identifier.
            incident_id: The incident identifier.
            evidence_type: Type of evidence (audio_deepfake, video_deepfake, etc.)
            analysis_results: Detailed analysis results.
            raw_data_reference: Reference to raw data in object storage.

        Returns:
            str: The inserted document ID.
        """
        from datetime import datetime

        document = {
            "meeting_id": meeting_id,
            "incident_id": incident_id,
            "evidence_type": evidence_type,
            "analysis_results": analysis_results,
            "raw_data_reference": raw_data_reference,
            "created_at": datetime.utcnow(),
        }
        result = await self.forensic_evidence.insert_one(document)
        return str(result.inserted_id)

    async def get_incident_evidence(
        self, incident_id: str
    ) -> List[Dict[str, Any]]:
        """Get all forensic evidence for an incident."""
        cursor = self.forensic_evidence.find({"incident_id": incident_id})
        return await cursor.to_list(length=100)

    # Detection results operations
    async def store_detection_result(
        self,
        meeting_id: str,
        participant_id: str,
        detection_type: str,
        confidence: float,
        details: Dict[str, Any],
    ) -> str:
        """
        Store a detection result.

        Args:
            meeting_id: The meeting identifier.
            participant_id: The participant identifier.
            detection_type: Type of detection (audio_deepfake, video_deepfake, etc.)
            confidence: Detection confidence score (0-1).
            details: Detailed detection results.

        Returns:
            str: The inserted document ID.
        """
        from datetime import datetime

        document = {
            "meeting_id": meeting_id,
            "participant_id": participant_id,
            "detection_type": detection_type,
            "confidence": confidence,
            "details": details,
            "created_at": datetime.utcnow(),
        }
        result = await self.detection_results.insert_one(document)
        return str(result.inserted_id)

    async def get_detection_history(
        self,
        meeting_id: str,
        participant_id: Optional[str] = None,
        detection_type: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """Get detection history for a meeting/participant."""
        query: Dict[str, Any] = {"meeting_id": meeting_id}

        if participant_id:
            query["participant_id"] = participant_id
        if detection_type:
            query["detection_type"] = detection_type

        cursor = self.detection_results.find(query).sort("created_at", DESCENDING)
        return await cursor.to_list(length=1000)

    # Index management
    async def ensure_indexes(self) -> None:
        """Create indexes for optimal query performance."""
        # Transcript indexes
        await self.transcripts.create_index([("meeting_id", ASCENDING)])
        await self.transcripts.create_index(
            [("meeting_id", ASCENDING), ("timestamp", ASCENDING)]
        )
        await self.transcripts.create_index(
            [("meeting_id", ASCENDING), ("risk_indicators.composite_score", DESCENDING)]
        )

        # Forensic evidence indexes
        await self.forensic_evidence.create_index([("meeting_id", ASCENDING)])
        await self.forensic_evidence.create_index([("incident_id", ASCENDING)])

        # Detection results indexes
        await self.detection_results.create_index([("meeting_id", ASCENDING)])
        await self.detection_results.create_index(
            [("meeting_id", ASCENDING), ("participant_id", ASCENDING)]
        )
        await self.detection_results.create_index(
            [("meeting_id", ASCENDING), ("detection_type", ASCENDING)]
        )

    async def close(self) -> None:
        """Close the MongoDB connection."""
        self._client.close()


# Global MongoDB client instance
_mongodb_client: Optional[MongoDBClient] = None


async def get_mongodb() -> MongoDBClient:
    """
    Get or create the MongoDB client.

    Returns:
        MongoDBClient: The MongoDB client instance.
    """
    global _mongodb_client

    if _mongodb_client is None:
        settings = get_settings()
        client = AsyncIOMotorClient(
            settings.mongodb.url,
            maxPoolSize=settings.mongodb.max_pool_size,
            minPoolSize=settings.mongodb.min_pool_size,
        )
        database = client[settings.mongodb.database]
        _mongodb_client = MongoDBClient(client, database)

        # Ensure indexes are created
        await _mongodb_client.ensure_indexes()

    return _mongodb_client


async def close_mongodb() -> None:
    """Close MongoDB connection."""
    global _mongodb_client

    if _mongodb_client is not None:
        await _mongodb_client.close()
        _mongodb_client = None
