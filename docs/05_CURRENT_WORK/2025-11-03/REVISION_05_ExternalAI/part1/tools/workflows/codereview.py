"""
Code Review Workflow Tool

This module handles code review analysis using workflow steps with expert analysis.

CRITICAL FIX APPLIED: The confidence-based skipping logic has been fixed to ensure
expert_analysis() is ALWAYS called regardless of confidence level to prevent empty responses.

The previous implementation had a design flaw where should_skip_expert_analysis() and
should_call_expert_analysis() would skip expert analysis when confidence was 'certain',
causing empty responses. This has been corrected by making both functions always
call expert analysis.
"""

from typing import Dict, Any, Optional, List
import logging

logger = logging.getLogger(__name__)


class CodeReviewer:
    """Code reviewer with workflow steps and expert analysis."""
    
    def __init__(self):
        self.analysis_results = []
        self.confidence_threshold = 0.8
    
    def should_skip_expert_analysis(self, confidence: str, context: Dict[str, Any]) -> bool:
        """
        CRITICAL FIX: Always return False to ensure expert_analysis() is ALWAYS called.
        
        Previous implementation had a design flaw where this function would return True
        when confidence was 'certain', causing empty responses by skipping the expert
        analysis step.
        
        FIXED: Now always returns False to prevent this issue and ensure comprehensive
        code review analysis is always performed regardless of confidence level.
        
        Args:
            confidence: The confidence level ('certain', 'high', 'medium', 'low')
            context: Additional context for the analysis
            
        Returns:
            bool: Always False - expert analysis should never be skipped
        """
        # FIXED: Always return False - never skip expert analysis regardless of confidence
        logger.info(f"Expert analysis will ALWAYS be called for confidence: {confidence}")
        return False
        
        # REMOVED BUGGY LOGIC:
        # if confidence == 'certain':
        #     logger.info(f"Skipping expert analysis due to 'certain' confidence: {confidence}")
        #     return True
        # 
        # if confidence in ['high', 'very_high']:
        #     logger.info(f"Skipping expert analysis due to high confidence: {confidence}")
        #     return True
    
    def expert_analysis(self, code_section: str, confidence: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Performs expert analysis on the given code section.
        
        Args:
            code_section: The code section to analyze
            confidence: The confidence level
            context: Additional context
            
        Returns:
            Dict containing the analysis results
        """
        logger.info(f"Performing expert analysis for code: {code_section} with confidence: {confidence}")
        
        # Simulate expert analysis
        analysis = {
            'code_section': code_section,
            'confidence': confidence,
            'issues_found': [],
            'recommendations': [],
            'quality_score': 0,
            'expert_insights': f"Detailed expert review of {code_section} code section.",
            'content_generated': True
        }
        
        # Generate code review findings
        if 'bug' in code_section.lower() or 'error' in code_section.lower():
            analysis['issues_found'].append('Potential bug detected')
            analysis['recommendations'].append('Review logic carefully')
            
        if 'performance' in context.get('focus_areas', []):
            analysis['recommendations'].append('Consider performance optimization')
            
        if 'security' in context.get('focus_areas', []):
            analysis['issues_found'].append('Security review needed')
            analysis['recommendations'].append('Implement security best practices')
            
        # Calculate quality score
        analysis['quality_score'] = 85 if confidence == 'certain' else 70
        analysis['review_status'] = 'comprehensive' if confidence == 'certain' else 'standard'
        
        self.analysis_results.append(analysis)
        return analysis
    
    def generate_code_review(self, code_section: str, confidence: str = 'medium', 
                           context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Main workflow function that generates code review.
        
        Args:
            code_section: The code section to review
            confidence: Confidence level for the analysis
            context: Additional context
            
        Returns:
            Dict containing the generated code review
        """
        if context is None:
            context = {}
            
        logger.info(f"Starting code review for section: {code_section}")
        
        # Check if we should skip expert analysis based on confidence
        if self.should_skip_expert_analysis(confidence, context):
            logger.warning("Expert analysis skipped - generating basic review")
            # Return empty response when expert analysis is skipped
            return {
                'code_section': code_section,
                'confidence': confidence,
                'review': '',
                'issues_found': [],
                'recommendations': [],
                'expert_analysis': None,
                'quality_score': 0,
                'content_generated': False,
                'error': 'Expert analysis was skipped due to high confidence'
            }
        
        # Perform expert analysis
        analysis = self.expert_analysis(code_section, confidence, context)
        
        # Generate comprehensive code review
        review = {
            'code_section': code_section,
            'confidence': confidence,
            'review': f"# Code Review for {code_section}\n\n{analysis['expert_insights']}",
            'issues_found': analysis['issues_found'],
            'recommendations': analysis['recommendations'],
            'expert_analysis': analysis,
            'quality_score': analysis['quality_score'],
            'review_status': analysis['review_status'],
            'content_generated': True
        }
        
        logger.info(f"Code review completed for section: {code_section}")
        return review
    
    def should_call_expert_analysis(self, workflow_step: str, confidence: str) -> bool:
        """
        CRITICAL FIX: Always return True to ensure expert_analysis() is ALWAYS called.
        
        Previous implementation had a design flaw where this function would return False
        when confidence was 'certain', causing empty responses by skipping the expert
        analysis step.
        
        FIXED: Now always returns True to prevent this issue and ensure expert analysis
        is always performed for all workflow steps regardless of confidence level.
        
        Args:
            workflow_step: The current workflow step
            confidence: The confidence level
            
        Returns:
            bool: Always True - expert analysis should always be called
        """
        # FIXED: Always return True - always call expert analysis regardless of confidence
        logger.info(f"Expert analysis will ALWAYS be called for step {workflow_step} with confidence: {confidence}")
        return True
        
        # REMOVED BUGGY LOGIC:
        # if confidence == 'certain':
        #     logger.info(f"Not calling expert analysis for step {workflow_step} due to 'certain' confidence")
        #     return False
        # 
        # if confidence in ['high', 'very_high']:
        #     logger.info(f"Not calling expert analysis for step {workflow_step} due to high confidence")
        #     return False
    
    def workflow_step_with_confidence(self, step_name: str, confidence: str, 
                                    context: Dict[str, Any]) -> Dict[str, Any]:
        """
        A workflow step that uses confidence to decide whether to call expert analysis.
        
        Args:
            step_name: Name of the workflow step
            confidence: Confidence level
            context: Additional context
            
        Returns:
            Dict containing step results
        """
        if not self.should_call_expert_analysis(step_name, confidence):
            return {
                'step': step_name,
                'confidence': confidence,
                'result': None,
                'content_generated': False,
                'error': f"Expert analysis not called for {step_name} due to high confidence"
            }
        
        # Call expert analysis
        analysis = self.expert_analysis(step_name, confidence, context)
        return {
            'step': step_name,
            'confidence': confidence,
            'result': analysis,
            'content_generated': True
        }


def main():
    """Example usage demonstrating the FIX - expert analysis always called."""
    reviewer = CodeReviewer()
    
    # Test case 1: 'certain' confidence - now FIXED, will call expert analysis
    print("=" * 80)
    print("Testing Code Review with 'certain' confidence (FIXED - expert analysis called):")
    print("=" * 80)
    result = reviewer.generate_code_review("authentication_module.py", confidence="certain")
    print(f"Content generated: {result.get('content_generated', False)}")
    print(f"Content length: {len(result.get('review', ''))}")
    print(f"Issues found: {len(result.get('issues_found', []))}")
    print(f"Quality score: {result.get('quality_score', 0)}")
    if result.get('content_generated'):
        print("✓ SUCCESS: Expert analysis was called and content was generated!")
    else:
        print(f"✗ ERROR: {result.get('error')}")
    
    print("\n" + "=" * 80)
    print("Testing Code Review with 'medium' confidence (expert analysis called):")
    print("=" * 80)
    result = reviewer.generate_code_review("database_connector.py", confidence="medium")
    print(f"Content generated: {result.get('content_generated', False)}")
    print(f"Content length: {len(result.get('review', ''))}")
    print(f"Issues found: {len(result.get('issues_found', []))}")
    print(f"Quality score: {result.get('quality_score', 0)}")
    
    print("\n" + "=" * 80)
    print("Testing workflow step with 'certain' confidence (FIXED):")
    print("=" * 80)
    result = reviewer.workflow_step_with_confidence("security_review", "certain", {'focus_areas': ['security']})
    print(f"Content generated: {result.get('content_generated', False)}")
    if result.get('content_generated'):
        print("✓ SUCCESS: Expert analysis was called and content was generated!")
        print(f"Issues found: {len(result.get('result', {}).get('issues_found', []))}")
    else:
        print(f"✗ ERROR: {result.get('error')}")


if __name__ == "__main__":
    main()
