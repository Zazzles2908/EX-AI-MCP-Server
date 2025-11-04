"""
Think Deep Workflow Tool

This module implements a deep thinking workflow that performs expert analysis
on problems with configurable confidence-based logic.

CRITICAL FIX: Confidence-based skipping logic has been fixed to ensure expert_analysis()
is ALWAYS called regardless of confidence level to prevent empty responses.
"""

import logging
from typing import Dict, List, Optional, Any
from enum import Enum

logger = logging.getLogger(__name__)


class ConfidenceLevel(Enum):
    """Confidence levels for analysis"""
    CERTAIN = "certain"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    UNCERTAIN = "uncertain"


class WorkflowStep:
    """Base class for workflow steps"""
    
    def __init__(self, step_id: str, description: str):
        self.step_id = step_id
        self.description = description
        
    def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the workflow step"""
        raise NotImplementedError
        
    def expert_analysis(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Perform expert analysis - should always be called"""
        logger.info(f"Performing expert analysis for step {self.step_id}")
        return {
            "analysis": f"Expert analysis completed for {self.step_id}",
            "recommendations": "Based on deep analysis",
            "confidence": "expert-level"
        }
    
    def should_skip_expert_analysis(self, context: Dict[str, Any]) -> bool:
        """
        CRITICAL FIX: Always return False to ensure expert_analysis() is ALWAYS called.
        
        Previous implementation had a design flaw where this function would return True
        when confidence was 'certain', causing empty responses by skipping the expert
        analysis step.
        
        FIXED: Now always returns False to prevent this issue.
        """
        # Always return False - never skip expert analysis regardless of confidence
        return False
        
        # REMOVED BUGGY LOGIC:
        # confidence = context.get('confidence', ConfidenceLevel.MEDIUM.value)
        # if confidence == ConfidenceLevel.CERTAIN.value:
        #     return True  # This was causing empty responses!
        
    def process_step(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Process a workflow step with confidence-aware logic"""
        logger.info(f"Processing step: {self.description}")
        
        # FIXED: Always call expert analysis regardless of confidence level
        if not self.should_skip_expert_analysis(context):
            expert_result = self.expert_analysis(context)
            context['expert_analysis'] = expert_result
            logger.info("Expert analysis completed successfully")
        else:
            logger.warning("Expert analysis was skipped - this should not happen with the fix!")
            
        # Continue with step-specific processing
        step_result = self.execute(context)
        context.update(step_result)
        
        return context


class ThinkDeepWorkflow:
    """Main workflow orchestrator for think-deep processing"""
    
    def __init__(self):
        self.steps: List[WorkflowStep] = []
        self.context: Dict[str, Any] = {}
        
    def add_step(self, step: WorkflowStep):
        """Add a workflow step"""
        self.steps.append(step)
        
    def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the complete workflow"""
        logger.info("Starting Think Deep workflow execution")
        
        # Initialize context with input data
        self.context = input_data.copy()
        self.context['workflow_start'] = True
        self.context['steps_completed'] = []
        
        try:
            # Process each step with guaranteed expert analysis
            for step in self.steps:
                logger.info(f"Executing step: {step.step_id}")
                
                # Ensure confidence is set for each step
                if 'confidence' not in self.context:
                    self.context['confidence'] = ConfidenceLevel.MEDIUM.value
                    
                # Process step with expert analysis (FIXED: will always call expert_analysis)
                result_context = step.process_step(self.context)
                self.context.update(result_context)
                
                # Track completed steps
                self.context['steps_completed'].append(step.step_id)
                
                logger.info(f"Completed step: {step.step_id}")
                
            # Finalize workflow
            self.context['workflow_complete'] = True
            self.context['final_result'] = {
                "status": "success",
                "message": "Think Deep workflow completed with expert analysis",
                "steps_executed": len(self.steps),
                "expert_analysis_included": True  # Guaranteed by the fix
            }
            
            logger.info("Think Deep workflow completed successfully")
            return self.context
            
        except Exception as e:
            logger.error(f"Workflow execution failed: {str(e)}")
            self.context['workflow_error'] = str(e)
            self.context['workflow_complete'] = False
            return self.context


class ProblemAnalysisStep(WorkflowStep):
    """Step for analyzing the core problem"""
    
    def __init__(self):
        super().__init__("problem_analysis", "Analyze the core problem")
        
    def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute problem analysis"""
        return {
            "problem_analysis": {
                "complexity": "analyzed",
                "requirements": "identified",
                "approach": "structured"
            }
        }


class SolutionDesignStep(WorkflowStep):
    """Step for designing the solution"""
    
    def __init__(self):
        super().__init__("solution_design", "Design the solution approach")
        
    def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute solution design"""
        return {
            "solution_design": {
                "methodology": "designed",
                "components": "specified",
                "implementation": "planned"
            }
        }


class ValidationStep(WorkflowStep):
    """Step for validating the approach"""
    
    def __init__(self):
        super().__init__("validation", "Validate the approach")
        
    def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute validation"""
        return {
            "validation": {
                "approach": "validated",
                "risks": "assessed",
                "mitigation": "planned"
            }
        }


def create_think_deep_workflow() -> ThinkDeepWorkflow:
    """Create and configure a think-deep workflow"""
    workflow = ThinkDeepWorkflow()
    
    # Add workflow steps
    workflow.add_step(ProblemAnalysisStep())
    workflow.add_step(SolutionDesignStep())
    workflow.add_step(ValidationStep())
    
    return workflow


def run_think_deep_analysis(input_data: Dict[str, Any], 
                          confidence: str = "medium") -> Dict[str, Any]:
    """
    Run a complete think-deep analysis with the fixed confidence logic.
    
    Args:
        input_data: Input data for analysis
        confidence: Confidence level (will not affect expert analysis due to fix)
        
    Returns:
        Analysis results with guaranteed expert analysis
    """
    # Ensure confidence is set
    input_data['confidence'] = confidence
    
    # Create and run workflow
    workflow = create_think_deep_workflow()
    result = workflow.execute(input_data)
    
    return result


if __name__ == "__main__":
    # Example usage with confidence = "certain" - this would have caused empty responses before the fix
    test_data = {
        "problem": "test_problem",
        "requirements": "test_requirements"
    }
    
    # This will now work correctly with expert analysis always included
    result = run_think_deep_analysis(test_data, confidence="certain")
    print(f"Result: {result}")