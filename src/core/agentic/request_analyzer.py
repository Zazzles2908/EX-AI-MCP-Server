"""
Request Analyzer: Intelligent preprocessing layer for routing decisions.

This module analyzes incoming requests to determine their type and characteristics
without sending large file contents to GLM for routing decisions. It implements
smart token management and cost-aware preprocessing.
"""
from __future__ import annotations

import hashlib
import logging
import re
from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, List, Optional, Set, Tuple
import json

logger = logging.getLogger("request_analyzer")


class RequestType(Enum):
    """Types of requests that can be routed to different providers."""
    FILE_OPERATION = "file_operation"
    WEB_BROWSING = "web_browsing"
    CODE_GENERATION = "code_generation"
    MULTIMODAL = "multimodal"
    LONG_CONTEXT = "long_context"
    GENERAL_CHAT = "general_chat"
    HYBRID = "hybrid"


class ContentComplexity(Enum):
    """Complexity levels for content analysis."""
    SIMPLE = "simple"
    MODERATE = "moderate"
    COMPLEX = "complex"
    VERY_COMPLEX = "very_complex"


@dataclass
class RequestAnalysis:
    """Analysis result for a request."""
    request_type: RequestType
    complexity: ContentComplexity
    estimated_tokens: int
    has_files: bool
    has_images: bool
    has_web_intent: bool
    file_types: Set[str]
    content_summary: str
    routing_confidence: float
    metadata: Dict[str, Any]

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for logging and routing."""
        return {
            "request_type": self.request_type.value,
            "complexity": self.complexity.value,
            "estimated_tokens": self.estimated_tokens,
            "has_files": self.has_files,
            "has_images": self.has_images,
            "has_web_intent": self.has_web_intent,
            "file_types": list(self.file_types),
            "content_summary": self.content_summary,
            "routing_confidence": self.routing_confidence,
            "metadata": self.metadata
        }


class RequestAnalyzer:
    """
    Intelligent request analyzer that preprocesses requests for optimal routing.
    
    Key features:
    - Token-aware analysis without sending large content to GLM
    - File type and content detection
    - Web browsing intent recognition
    - Smart content summarization for routing decisions
    - Cost-aware preprocessing
    """

    # File operation keywords
    FILE_KEYWORDS = {
        "read", "write", "create", "delete", "modify", "edit", "save", "load",
        "file", "document", "text", "csv", "json", "xml", "yaml", "config",
        "extract", "parse", "analyze file", "process file", "upload", "download"
    }

    # Web browsing keywords
    WEB_KEYWORDS = {
        "search", "browse", "website", "url", "link", "internet", "web",
        "google", "find online", "lookup", "research", "scrape", "crawl",
        "fetch", "retrieve", "online", "http", "https", "www"
    }

    # Code generation keywords
    CODE_KEYWORDS = {
        "code", "program", "script", "function", "class", "method", "algorithm",
        "implement", "develop", "build", "create app", "write code", "debug",
        "refactor", "optimize", "test", "unit test", "api", "framework"
    }

    # File extensions that indicate file operations
    FILE_EXTENSIONS = {
        ".txt", ".md", ".json", ".xml", ".yaml", ".yml", ".csv", ".tsv",
        ".py", ".js", ".ts", ".html", ".css", ".sql", ".sh", ".bat",
        ".pdf", ".doc", ".docx", ".xls", ".xlsx", ".ppt", ".pptx"
    }

    # Image extensions
    IMAGE_EXTENSIONS = {
        ".jpg", ".jpeg", ".png", ".gif", ".bmp", ".svg", ".webp", ".tiff"
    }

    def __init__(self, max_summary_tokens: int = 500):
        """
        Initialize the request analyzer.
        
        Args:
            max_summary_tokens: Maximum tokens to use for content summary
        """
        self.max_summary_tokens = max_summary_tokens
        self._token_estimate_cache: Dict[str, int] = {}

    def analyze_request(self, request: Dict[str, Any]) -> RequestAnalysis:
        """
        Analyze a request to determine its type and characteristics.
        
        Args:
            request: The request dictionary containing messages and metadata
            
        Returns:
            RequestAnalysis object with routing information
        """
        try:
            # Extract messages and content
            messages = request.get("messages", [])
            if not messages:
                return self._create_default_analysis()

            # Analyze content characteristics
            content_info = self._analyze_content(messages)
            
            # Determine request type
            request_type = self._determine_request_type(content_info)
            
            # Assess complexity
            complexity = self._assess_complexity(content_info)
            
            # Create content summary for routing
            content_summary = self._create_content_summary(content_info)
            
            # Calculate routing confidence
            confidence = self._calculate_routing_confidence(content_info, request_type)
            
            analysis = RequestAnalysis(
                request_type=request_type,
                complexity=complexity,
                estimated_tokens=content_info["total_tokens"],
                has_files=content_info["has_files"],
                has_images=content_info["has_images"],
                has_web_intent=content_info["has_web_intent"],
                file_types=content_info["file_types"],
                content_summary=content_summary,
                routing_confidence=confidence,
                metadata={
                    "message_count": len(messages),
                    "avg_message_length": content_info["avg_message_length"],
                    "keyword_matches": content_info["keyword_matches"],
                    "has_attachments": content_info.get("has_attachments", False)
                }
            )
            
            logger.debug(f"Request analysis completed: {analysis.to_dict()}")
            return analysis
            
        except Exception as e:
            logger.error(f"Error analyzing request: {e}")
            return self._create_default_analysis()

    def _analyze_content(self, messages: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze message content for routing characteristics."""
        total_chars = 0
        total_tokens = 0
        has_files = False
        has_images = False
        has_web_intent = False
        file_types: Set[str] = set()
        keyword_matches: Dict[str, int] = {
            "file": 0, "web": 0, "code": 0
        }
        all_text = ""
        
        for message in messages:
            if not isinstance(message, dict):
                continue
                
            content = message.get("content", "")
            if isinstance(content, str):
                all_text += content + " "
                total_chars += len(content)
                total_tokens += self._estimate_tokens(content)
                
                # Check for file-related content
                if self._has_file_indicators(content):
                    has_files = True
                    file_types.update(self._extract_file_types(content))
                
                # Check for web-related content
                if self._has_web_indicators(content):
                    has_web_intent = True
                
                # Count keyword matches
                content_lower = content.lower()
                for keyword in self.FILE_KEYWORDS:
                    if keyword in content_lower:
                        keyword_matches["file"] += 1
                        
                for keyword in self.WEB_KEYWORDS:
                    if keyword in content_lower:
                        keyword_matches["web"] += 1
                        
                for keyword in self.CODE_KEYWORDS:
                    if keyword in content_lower:
                        keyword_matches["code"] += 1
            
            # Check for images in message
            if "images" in message or any(key.startswith("image") for key in message.keys()):
                has_images = True
            
            # Check for attachments
            if "attachments" in message or "files" in message:
                has_files = True

        return {
            "total_chars": total_chars,
            "total_tokens": total_tokens,
            "has_files": has_files,
            "has_images": has_images,
            "has_web_intent": has_web_intent,
            "file_types": file_types,
            "keyword_matches": keyword_matches,
            "all_text": all_text,
            "avg_message_length": total_chars / len(messages) if messages else 0,
            "has_attachments": has_files or has_images
        }

    def _determine_request_type(self, content_info: Dict[str, Any]) -> RequestType:
        """Determine the primary request type based on content analysis."""
        keyword_matches = content_info["keyword_matches"]
        
        # Check for multimodal content
        if content_info["has_images"]:
            return RequestType.MULTIMODAL
        
        # Check for long context
        if content_info["total_tokens"] > 32000:
            return RequestType.LONG_CONTEXT
        
        # Check for hybrid requirements
        if (keyword_matches["file"] > 0 and keyword_matches["web"] > 0) or \
           (content_info["has_files"] and content_info["has_web_intent"]):
            return RequestType.HYBRID
        
        # Check for file operations
        if content_info["has_files"] or keyword_matches["file"] > keyword_matches["web"]:
            return RequestType.FILE_OPERATION
        
        # Check for web browsing
        if content_info["has_web_intent"] or keyword_matches["web"] > 0:
            return RequestType.WEB_BROWSING
        
        # Check for code generation
        if keyword_matches["code"] > 2:
            return RequestType.CODE_GENERATION
        
        return RequestType.GENERAL_CHAT

    def _assess_complexity(self, content_info: Dict[str, Any]) -> ContentComplexity:
        """Assess the complexity of the request."""
        tokens = content_info["total_tokens"]
        keyword_total = sum(content_info["keyword_matches"].values())
        file_types_count = len(content_info["file_types"])
        
        complexity_score = 0
        
        # Token-based complexity
        if tokens > 50000:
            complexity_score += 3
        elif tokens > 20000:
            complexity_score += 2
        elif tokens > 5000:
            complexity_score += 1
        
        # Keyword density complexity
        if keyword_total > 10:
            complexity_score += 2
        elif keyword_total > 5:
            complexity_score += 1
        
        # File type diversity
        if file_types_count > 3:
            complexity_score += 2
        elif file_types_count > 1:
            complexity_score += 1
        
        # Multimodal complexity
        if content_info["has_images"]:
            complexity_score += 1
        
        # Map score to complexity level
        if complexity_score >= 6:
            return ContentComplexity.VERY_COMPLEX
        elif complexity_score >= 4:
            return ContentComplexity.COMPLEX
        elif complexity_score >= 2:
            return ContentComplexity.MODERATE
        else:
            return ContentComplexity.SIMPLE

    def _create_content_summary(self, content_info: Dict[str, Any]) -> str:
        """Create a concise summary for routing decisions."""
        all_text = content_info["all_text"]
        
        # If content is short enough, return as-is
        if len(all_text) <= self.max_summary_tokens * 4:  # Rough char to token ratio
            return all_text.strip()
        
        # Create hash-based summary for large content
        content_hash = hashlib.md5(all_text.encode()).hexdigest()[:8]
        
        # Extract key phrases and first/last portions
        words = all_text.split()
        if len(words) > 100:
            summary_words = words[:50] + ["..."] + words[-50:]
            summary = " ".join(summary_words)
        else:
            summary = all_text
        
        return f"[HASH:{content_hash}] {summary.strip()}"

    def _calculate_routing_confidence(self, content_info: Dict[str, Any], 
                                    request_type: RequestType) -> float:
        """Calculate confidence score for routing decision."""
        confidence = 0.5  # Base confidence
        
        keyword_matches = content_info["keyword_matches"]
        
        # Boost confidence based on clear indicators
        if request_type == RequestType.FILE_OPERATION and content_info["has_files"]:
            confidence += 0.3
        elif request_type == RequestType.WEB_BROWSING and content_info["has_web_intent"]:
            confidence += 0.3
        elif request_type == RequestType.MULTIMODAL and content_info["has_images"]:
            confidence += 0.4
        elif request_type == RequestType.LONG_CONTEXT and content_info["total_tokens"] > 50000:
            confidence += 0.4
        
        # Boost based on keyword density
        max_keywords = max(keyword_matches.values()) if keyword_matches.values() else 0
        if max_keywords > 5:
            confidence += 0.2
        elif max_keywords > 2:
            confidence += 0.1
        
        return min(confidence, 1.0)

    def _has_file_indicators(self, content: str) -> bool:
        """Check if content has file operation indicators."""
        content_lower = content.lower()
        
        # Check for file extensions
        for ext in self.FILE_EXTENSIONS:
            if ext in content_lower:
                return True
        
        # Check for file keywords
        for keyword in self.FILE_KEYWORDS:
            if keyword in content_lower:
                return True
        
        return False

    def _has_web_indicators(self, content: str) -> bool:
        """Check if content has web browsing indicators."""
        content_lower = content.lower()
        
        # Check for URLs
        if re.search(r'https?://|www\.', content_lower):
            return True
        
        # Check for web keywords
        for keyword in self.WEB_KEYWORDS:
            if keyword in content_lower:
                return True
        
        return False

    def _extract_file_types(self, content: str) -> Set[str]:
        """Extract file types mentioned in content."""
        file_types = set()
        content_lower = content.lower()
        
        for ext in self.FILE_EXTENSIONS | self.IMAGE_EXTENSIONS:
            if ext in content_lower:
                file_types.add(ext)
        
        return file_types

    def _estimate_tokens(self, text: str) -> int:
        """Estimate token count for text."""
        # Use cache for repeated content
        text_hash = hashlib.md5(text.encode()).hexdigest()
        if text_hash in self._token_estimate_cache:
            return self._token_estimate_cache[text_hash]
        
        # Simple estimation: ~4 characters per token
        estimated = len(text) // 4
        
        # Cache the result
        if len(self._token_estimate_cache) < 1000:  # Prevent memory bloat
            self._token_estimate_cache[text_hash] = estimated
        
        return estimated

    def _create_default_analysis(self) -> RequestAnalysis:
        """Create a default analysis for error cases."""
        return RequestAnalysis(
            request_type=RequestType.GENERAL_CHAT,
            complexity=ContentComplexity.SIMPLE,
            estimated_tokens=0,
            has_files=False,
            has_images=False,
            has_web_intent=False,
            file_types=set(),
            content_summary="",
            routing_confidence=0.1,
            metadata={}
        )
