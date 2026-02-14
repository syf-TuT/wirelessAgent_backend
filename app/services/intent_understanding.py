"""
IntentUnderstandingService - Handles LLM-based intent classification
"""

import re
from typing import Dict, Any, List, Optional, Tuple
from app.models.enums import SliceType, IntentType
from app.core.config import get_cached_settings


class IntentUnderstandingService:
    """
    Service for understanding user requests and classifying intent to appropriate network slices.
    
    Supports both knowledge-base and pure LLM-based intent classification.
    """
    
    def __init__(self, use_knowledge_base: bool = False, knowledge_base_content: Optional[str] = None):
        """
        Initialize IntentUnderstandingService.
        
        Args:
            use_knowledge_base: Whether to use knowledge base for classification
            knowledge_base_content: Content of knowledge base file (if using KB)
        """
        self.use_knowledge_base = use_knowledge_base
        self.knowledge_base_content = knowledge_base_content
        self.llm = None
        self._initialize_llm()
    
    def _initialize_llm(self):
        """Initialize LLM client using configuration"""
        try:
            from langchain_openai import ChatOpenAI
            settings = get_cached_settings()
            
            self.llm = ChatOpenAI(
                api_key=settings.llm_api_key,
                base_url=settings.llm_base_url,
                model=settings.llm_model,
                temperature=settings.llm_temperature,
            )
        except Exception as e:
            # If LLM initialization fails, fall back to heuristic
            print(f"Warning: LLM initialization failed: {e}. Using heuristic classification.")
            self.llm = None
    
    def classify_intent(self, request: str) -> Tuple[IntentType, SliceType, List[str]]:
        """
        Classify user request into an intent type and determine appropriate slice.
        
        Args:
            request: User's natural language request
            
        Returns:
            Tuple of (intent_type, slice_type, reasoning_list)
        """
        # Clean request
        request_lower = request.lower().strip()
        
        # Try knowledge-base classification if enabled
        if self.use_knowledge_base and self.knowledge_base_content:
            intent, slice_type, reasoning = self._classify_with_kb(request_lower)
            if intent != IntentType.UNKNOWN:
                return intent, slice_type, reasoning
        
        # Fall back to LLM or heuristic classification
        if self.llm:
            intent, slice_type, reasoning = self._classify_with_llm(request)
        else:
            intent, slice_type, reasoning = self._classify_with_heuristics(request_lower)
        
        return intent, slice_type, reasoning
    
    def _classify_with_kb(self, request_lower: str) -> Tuple[IntentType, SliceType, List[str]]:
        """
        Classify using knowledge base patterns.
        
        Args:
            request_lower: Request text in lowercase
            
        Returns:
            Tuple of (intent_type, slice_type, reasoning)
        """
        reasoning = []
        
        if not self.knowledge_base_content:
            return IntentType.UNKNOWN, SliceType.EMBB, ["No knowledge base loaded"]
        
        # Search for patterns in knowledge base
        kb_lower = self.knowledge_base_content.lower()
        
        # Count keyword matches for each slice type
        embb_matches = 0
        urllc_matches = 0
        mmtc_matches = 0
        
        # Define slice-specific keywords
        embb_keywords = [
            "video", "stream", "download", "upload", "ar", "vr", "high bandwidth",
            "multimedia", "4k", "hd", "entertainment", "cloud gaming", "virtual reality"
        ]
        
        urllc_keywords = [
            "control", "real-time", "latency", "instant", "robotic", "autonomous",
            "surgery", "critical", "reliable", "fast", "immediate", "low latency"
        ]
        
        mmtc_keywords = [
            "sensor", "iot", "monitoring", "tracking", "meter", "device",
            "massive", "connectivity", "asset", "low bandwidth", "infrequent"
        ]
        
        # Count matches
        for keyword in embb_keywords:
            if keyword in request_lower:
                embb_matches += 1
        
        for keyword in urllc_keywords:
            if keyword in request_lower:
                urllc_matches += 1
        
        for keyword in mmtc_keywords:
            if keyword in request_lower:
                mmtc_matches += 1
        
        # Determine dominant slice type
        if embb_matches > urllc_matches and embb_matches > mmtc_matches and embb_matches > 0:
            intent = IntentType.BROADBAND
            slice_type = SliceType.EMBB
            reasoning.append(f"Knowledge base match: eMBB keywords found ({embb_matches} matches)")
        elif urllc_matches > embb_matches and urllc_matches > mmtc_matches and urllc_matches > 0:
            intent = IntentType.LOW_LATENCY
            slice_type = SliceType.URLLC
            reasoning.append(f"Knowledge base match: URLLC keywords found ({urllc_matches} matches)")
        elif mmtc_matches > embb_matches and mmtc_matches > urllc_matches and mmtc_matches > 0:
            intent = IntentType.IOT
            slice_type = SliceType.MMTC
            reasoning.append(f"Knowledge base match: mMTC keywords found ({mmtc_matches} matches)")
        else:
            return IntentType.UNKNOWN, SliceType.EMBB, ["No clear knowledge base match"]
        
        return intent, slice_type, reasoning
    
    def _classify_with_llm(self, request: str) -> Tuple[IntentType, SliceType, List[str]]:
        """
        Classify using LLM analysis.
        
        Args:
            request: User's natural language request
            
        Returns:
            Tuple of (intent_type, slice_type, reasoning)
        """
        reasoning = []
        
        if not self.llm:
            return self._classify_with_heuristics(request.lower())
        
        try:
            from langchain_core.messages import HumanMessage, SystemMessage
            
            system_prompt = """You are a network resource allocation expert. 
Analyze the user's request and classify it into one of these categories:
1. BROADBAND - Requests for video streaming, downloads, AR/VR, high-bandwidth content
2. LOW_LATENCY - Real-time critical control, autonomous systems, low-latency applications
3. IOT - IoT sensors, monitoring, asset tracking, machine-type communications

Respond with ONLY the category name (BROADBAND, LOW_LATENCY, or IOT).
Do not include any other text."""
            
            messages = [
                SystemMessage(content=system_prompt),
                HumanMessage(content=f"User request: {request}")
            ]
            
            response = self.llm.invoke(messages)
            response_text = response.content.strip().upper()
            
            # Parse LLM response
            if "BROADBAND" in response_text:
                intent = IntentType.BROADBAND
                slice_type = SliceType.EMBB
            elif "LOW_LATENCY" in response_text or "CRITICAL" in response_text:
                intent = IntentType.LOW_LATENCY
                slice_type = SliceType.URLLC
            elif "IOT" in response_text or "MONITORING" in response_text:
                intent = IntentType.IOT
                slice_type = SliceType.MMTC
            else:
                # Fallback
                return self._classify_with_heuristics(request.lower())
            
            reasoning.append(f"LLM classification: {intent.value}")
            
            return intent, slice_type, reasoning
        
        except Exception as e:
            reasoning.append(f"LLM classification failed: {str(e)}")
            # Fall back to heuristic
            return self._classify_with_heuristics(request.lower())
    
    def _classify_with_heuristics(self, request_lower: str) -> Tuple[IntentType, SliceType, List[str]]:
        """
        Classify using simple keyword-based heuristics.
        
        Args:
            request_lower: Request text in lowercase
            
        Returns:
            Tuple of (intent_type, slice_type, reasoning)
        """
        reasoning = []
        
        # eMBB keywords
        embb_keywords = {
            "video", "stream", "download", "upload", "ar", "vr",
            "4k", "hd", "multimedia", "movie", "music", "large file",
            "high bandwidth", "internet", "cloud", "gaming", "virtual reality",
            "content", "browse", "web", "social media"
        }
        
        # URLLC keywords
        urllc_keywords = {
            "control", "real-time", "latency", "instant", "robot",
            "autonomous", "surgery", "critical", "reliable", "fast",
            "immediate", "responsive", "low latency", "emergency",
            "drive", "monitor critical", "control system"
        }
        
        # mMTC keywords
        mmtc_keywords = {
            "sensor", "iot", "monitor", "track", "meter", "device",
            "massive", "connect", "asset", "low bandwidth",
            "infrequent", "data collection", "telemetry", "smart city",
            "environmental", "weather"
        }
        
        # Score each category
        embb_score = sum(1 for kw in embb_keywords if kw in request_lower)
        urllc_score = sum(1 for kw in urllc_keywords if kw in request_lower)
        mmtc_score = sum(1 for kw in mmtc_keywords if kw in request_lower)
        
        # Determine dominant category
        max_score = max(embb_score, urllc_score, mmtc_score)
        
        if max_score == 0:
            # No clear match, default to eMBB (most common use case)
            intent = IntentType.BROADBAND
            slice_type = SliceType.EMBB
            reasoning.append("No clear keywords found, defaulting to eMBB (broadband)")
        elif embb_score == max_score and embb_score > 0:
            intent = IntentType.BROADBAND
            slice_type = SliceType.EMBB
            reasoning.append(f"Heuristic match: eMBB ({embb_score} keywords)")
        elif urllc_score == max_score and urllc_score > 0:
            intent = IntentType.LOW_LATENCY
            slice_type = SliceType.URLLC
            reasoning.append(f"Heuristic match: URLLC ({urllc_score} keywords)")
        else:  # mmtc_score == max_score and mmtc_score > 0
            intent = IntentType.IOT
            slice_type = SliceType.MMTC
            reasoning.append(f"Heuristic match: mMTC ({mmtc_score} keywords)")
        
        return intent, slice_type, reasoning
    
    def extract_entity_from_request(self, request: str) -> Dict[str, Any]:
        """
        Extract important entities and keywords from user request.
        
        Args:
            request: User's natural language request
            
        Returns:
            Dictionary with extracted entities
        """
        request_lower = request.lower()
        
        entities = {
            "request_text": request,
            "bandwidth_hints": [],
            "latency_hints": [],
            "reliability_hints": [],
        }
        
        # Bandwidth hints
        if any(kw in request_lower for kw in ["large file", "video", "4k", "hd", "stream"]):
            entities["bandwidth_hints"].append("high_bandwidth_required")
        
        if any(kw in request_lower for kw in ["sensor", "meter", "small data", "infrequent"]):
            entities["bandwidth_hints"].append("low_bandwidth_ok")
        
        # Latency hints
        if any(kw in request_lower for kw in ["real-time", "instant", "critical", "emergency"]):
            entities["latency_hints"].append("low_latency_required")
        
        if any(kw in request_lower for kw in ["download", "file", "background", "batch"]):
            entities["latency_hints"].append("latency_not_critical")
        
        # Reliability hints
        if any(kw in request_lower for kw in ["critical", "reliable", "safe", "surgery", "autonomous"]):
            entities["reliability_hints"].append("high_reliability_required")
        
        return entities
    
    def get_slice_recommendation_reasons(self, request: str) -> Dict[str, List[str]]:
        """
        Provide detailed reasoning for slice recommendation.
        
        Args:
            request: User's natural language request
            
        Returns:
            Dictionary with reasoning for each slice type
        """
        intent, slice_type, reasoning = self.classify_intent(request)
        
        result = {
            "selected_intent": intent.value,
            "selected_slice": slice_type.value,
            "reasoning": reasoning,
            "confidence": self._calculate_confidence(intent, request),
        }
        
        return result
    
    def _calculate_confidence(self, intent: IntentType, request: str) -> float:
        """
        Calculate confidence score for the classification.
        
        Args:
            intent: Classified intent type
            request: Original request text
            
        Returns:
            Confidence score (0.0-1.0)
        """
        # Simple confidence calculation based on request length and clarity
        request_len = len(request.split())
        
        # Base confidence on request specificity
        if request_len < 5:
            base_confidence = 0.5
        elif request_len < 10:
            base_confidence = 0.7
        else:
            base_confidence = 0.85
        
        return min(base_confidence, 1.0)
