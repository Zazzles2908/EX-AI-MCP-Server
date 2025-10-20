"""
History detection and stripping utilities for conversation management.

This module provides multi-layer detection of embedded conversation history
and utilities to strip it from messages to prevent recursive embedding.
"""

import re
from enum import Enum
from typing import List, Tuple, Optional
import logging

logger = logging.getLogger(__name__)


class DetectionMode(Enum):
    """Detection mode for history markers."""
    CONSERVATIVE = "conservative"  # Only clear, unambiguous markers
    AGGRESSIVE = "aggressive"      # Include potential markers with higher false positives


class HistoryDetector:
    """
    Multi-layer history detection with configurable sensitivity.
    
    Supports both conservative (high confidence) and aggressive (broader)
    detection modes. Uses compiled regex patterns for performance.
    """
    
    def __init__(self, mode: DetectionMode = DetectionMode.CONSERVATIVE):
        """
        Initialize history detector.
        
        Args:
            mode: Detection mode (CONSERVATIVE or AGGRESSIVE)
        """
        self.mode = mode
        self._compile_patterns()
    
    def _compile_patterns(self):
        """Compile regex patterns for history detection."""
        # Conservative patterns - high confidence markers
        self.conservative_patterns = [
            re.compile(r'===\s*CONVERSATION\s+HISTORY\s*===', re.IGNORECASE),
            re.compile(r'===\s*PREVIOUS\s+MESSAGES\s*===', re.IGNORECASE),
            re.compile(r'===\s*CONTEXT\s*===', re.IGNORECASE),
            re.compile(r'---+\s*HISTORY\s*---+', re.IGNORECASE),
            re.compile(r'\[HISTORY\s+START\]', re.IGNORECASE),
            re.compile(r'<history>', re.IGNORECASE),
            re.compile(r'===\s*CHAT\s+HISTORY\s*===', re.IGNORECASE),
        ]

        # Aggressive patterns - broader but may have false positives
        self.aggressive_patterns = [
            re.compile(r'===\s*PREVIOUS\s+CONVERSATION\s*===', re.IGNORECASE),
            re.compile(r'---+\s*PREVIOUS\s*---+', re.IGNORECASE),
            re.compile(r'\[HISTORY\s+BEGINS\]', re.IGNORECASE),
            re.compile(r'<conversation_history>', re.IGNORECASE),
            re.compile(r'===\s*EARLIER\s+MESSAGES\s*===', re.IGNORECASE),
            re.compile(r'Context:\s*\n', re.IGNORECASE),
            re.compile(r'Previous conversation:', re.IGNORECASE),
            re.compile(r'Earlier messages:', re.IGNORECASE),
        ]

        # End marker patterns
        self.end_patterns = [
            re.compile(r'===\s*END\s*===', re.IGNORECASE),
            re.compile(r'---+\s*END\s*---+', re.IGNORECASE),
            re.compile(r'\[HISTORY\s+END\]', re.IGNORECASE),
            re.compile(r'\[END\s+HISTORY\]', re.IGNORECASE),
            re.compile(r'</history>', re.IGNORECASE),
            re.compile(r'</conversation_history>', re.IGNORECASE),
        ]
    
    def detect_history_markers(self, text: str) -> List[Tuple[int, int]]:
        """
        Detect history markers in text.
        
        Args:
            text: Text to search for history markers
            
        Returns:
            List of (start_pos, end_pos) tuples for each marker found
        """
        if not text:
            return []
        
        patterns = self.conservative_patterns.copy()
        if self.mode == DetectionMode.AGGRESSIVE:
            patterns.extend(self.aggressive_patterns)
        
        markers = []
        for pattern in patterns:
            for match in pattern.finditer(text):
                markers.append((match.start(), match.end()))
        
        # Sort by position and remove duplicates
        markers = sorted(set(markers), key=lambda x: x[0])
        
        if markers:
            logger.debug(f"Detected {len(markers)} history markers in text")
        
        return markers
    
    def extract_history_sections(self, text: str) -> List[Tuple[int, int]]:
        """
        Extract complete history sections between markers.

        Args:
            text: Text to extract history sections from

        Returns:
            List of (start_pos, end_pos) tuples for each history section
        """
        markers = self.detect_history_markers(text)
        if not markers:
            return []

        sections = []
        # Look for matching end markers
        for i, (start, marker_end) in enumerate(markers):
            # Find the end of this section by looking for end markers
            section_end = None

            # Search for end markers after this start marker
            for end_pattern in self.end_patterns:
                match = end_pattern.search(text, marker_end)
                if match:
                    # Found an end marker
                    end_pos = match.end()
                    # Include the newline after the end marker if present
                    if end_pos < len(text) and text[end_pos] == '\n':
                        end_pos += 1

                    # Use this end marker if it's before any other end marker we found
                    if section_end is None or end_pos < section_end:
                        section_end = end_pos

            # If no end marker found, look for the next start marker
            if section_end is None:
                if i + 1 < len(markers):
                    section_end = markers[i+1][0]
                else:
                    # No end marker and no next start marker - skip this section
                    # to avoid removing content after the marker
                    continue

            sections.append((start, section_end))

        if sections:
            logger.debug(f"Extracted {len(sections)} history sections from text")

        return sections
    
    def strip_history(self, text: str, preserve_user_content: bool = True) -> str:
        """
        Strip embedded history from text.
        
        Args:
            text: Text to strip history from
            preserve_user_content: If True, preserve content after last history section
            
        Returns:
            Text with history sections removed
        """
        if not text:
            return text
        
        sections = self.extract_history_sections(text)
        if not sections:
            return text
        
        # Extract content outside history sections
        clean_parts = []
        last_end = 0
        
        for start, end in sections:
            # Add content before this history section
            if start > last_end:
                clean_parts.append(text[last_end:start])
            last_end = end
        
        # Add content after last history section
        if preserve_user_content and last_end < len(text):
            clean_parts.append(text[last_end:])
        
        clean_text = ''.join(clean_parts).strip()
        
        if clean_text != text:
            logger.info(
                f"Stripped history from text: "
                f"{len(text)} chars -> {len(clean_text)} chars "
                f"({len(sections)} sections removed)"
            )
        
        return clean_text
    
    def has_embedded_history(self, text: str) -> bool:
        """
        Check if text contains embedded history markers.
        
        Args:
            text: Text to check
            
        Returns:
            True if history markers are detected, False otherwise
        """
        markers = self.detect_history_markers(text)
        return len(markers) > 0


def strip_embedded_history(content: str, mode: DetectionMode = DetectionMode.CONSERVATIVE,
                           preserve_user_content: bool = True) -> str:
    """
    Convenience function to strip embedded history from content.
    
    This is the main entry point for history stripping. It creates a detector
    and strips history in one call.
    
    Args:
        content: Content to strip history from
        mode: Detection mode (CONSERVATIVE or AGGRESSIVE)
        preserve_user_content: If True, preserve content after last history section
        
    Returns:
        Content with history stripped
    """
    if not content:
        return content
    
    detector = HistoryDetector(mode)
    return detector.strip_history(content, preserve_user_content)


def detect_and_log_history(content: str, context: str = "") -> bool:
    """
    Detect history and log details for debugging.
    
    Args:
        content: Content to check for history
        context: Context string for logging (e.g., "user message", "assistant response")
        
    Returns:
        True if history was detected, False otherwise
    """
    if not content:
        return False
    
    detector = HistoryDetector(DetectionMode.AGGRESSIVE)
    markers = detector.detect_history_markers(content)
    
    if markers:
        logger.warning(
            f"Detected embedded history in {context}: "
            f"{len(markers)} markers found at positions {markers}"
        )
        return True
    
    return False


def strip_history_recursive(content: str, max_iterations: int = 5) -> str:
    """
    Recursively strip history until no markers remain.
    
    This handles cases where history is nested multiple levels deep.
    
    Args:
        content: Content to strip history from
        max_iterations: Maximum number of stripping iterations
        
    Returns:
        Content with all nested history stripped
    """
    if not content:
        return content
    
    detector = HistoryDetector(DetectionMode.AGGRESSIVE)
    
    for iteration in range(max_iterations):
        if not detector.has_embedded_history(content):
            if iteration > 0:
                logger.info(f"Stripped nested history in {iteration} iterations")
            return content
        
        content = detector.strip_history(content)
    
    # If we hit max iterations, log a warning
    if detector.has_embedded_history(content):
        logger.warning(
            f"History markers still present after {max_iterations} iterations. "
            f"Content may have deeply nested or malformed history."
        )
    
    return content


# Global detector instances for reuse
_conservative_detector = HistoryDetector(DetectionMode.CONSERVATIVE)
_aggressive_detector = HistoryDetector(DetectionMode.AGGRESSIVE)


def quick_strip(content: str, aggressive: bool = False) -> str:
    """
    Quick history stripping using global detector instances.
    
    Args:
        content: Content to strip history from
        aggressive: If True, use aggressive detection mode
        
    Returns:
        Content with history stripped
    """
    detector = _aggressive_detector if aggressive else _conservative_detector
    return detector.strip_history(content)

