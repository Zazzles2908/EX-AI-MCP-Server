"""
SecAudit Workflow Configuration

Field descriptions and configuration constants for the SecAudit workflow tool.
"""

# Tool-specific field descriptions for security audit workflow
SECAUDIT_WORKFLOW_FIELD_DESCRIPTIONS = {
    "step": (
        "Describe what you're currently investigating for security audit by thinking deeply about security "
        "implications, threat vectors, and protection mechanisms. In step 1, clearly state your security "
        "audit plan and begin forming a systematic approach after identifying the application type, "
        "technology stack, and relevant security requirements. You must begin by passing the file path "
        "for the initial code you are about to audit in relevant_files. CRITICAL: Follow the OWASP Top 10 "
        "systematic checklist, examine authentication/authorization mechanisms, analyze input validation "
        "and data handling, assess dependency vulnerabilities, and evaluate infrastructure security. "
        "Consider not only obvious vulnerabilities but also subtle security gaps, configuration issues, "
        "design flaws, and compliance requirements. Map out the attack surface, understand the threat "
        "landscape, and identify areas requiring deeper security analysis. In all later steps, continue "
        "exploring with precision: trace security dependencies, verify security assumptions, and adapt "
        "your understanding as you uncover security evidence."
    ),
    "step_number": (
        "The index of the current step in the security audit sequence, beginning at 1. Each step should "
        "build upon or revise the previous one."
    ),
    "total_steps": (
        "Your current estimate for how many steps will be needed to complete the security audit. "
        "Adjust and increase as new security findings emerge."
    ),
    "next_step_required": (
        "Set to true if you plan to continue the investigation with another step. False means you believe "
        "the security audit analysis is complete and ALL threats have been uncovered, ready for expert validation."
    ),
    "findings": (
        "Summarize everything discovered in this step about security aspects of the code being audited. "
        "Include analysis of security vulnerabilities, authentication/authorization issues, input validation "
        "gaps, encryption weaknesses, configuration problems, and compliance concerns. Be specific and avoid "
        "vague language—document what you now know about the security posture and how it affects your "
        "assessment. IMPORTANT: Document both positive security findings (proper implementations, good "
        "security practices) and concerns (vulnerabilities, security gaps, compliance issues). In later "
        "steps, confirm or update past findings with additional evidence."
    ),
    "files_checked": (
        "List all files (as absolute paths, do not clip or shrink file names) examined during the security "
        "audit investigation so far. Include even files ruled out or found to be unrelated, as this tracks "
        "your exploration path."
    ),
    "relevant_files": (
        "For when this is the first step, please pass absolute file paths of relevant code to audit (do not clip "
        "file paths). When used for the final step, this contains a subset of files_checked (as full absolute paths) "
        "that contain code directly relevant to the security audit or contain significant security issues, patterns, "
        "or examples worth highlighting. Only list those that are directly tied to important security findings, "
        "vulnerabilities, authentication issues, or security architectural decisions. This could include "
        "authentication modules, input validation files, configuration files, or files with notable security patterns."
    ),
    "relevant_context": (
        "List methods, functions, classes, or modules that are central to the security audit findings, in the "
        "format 'ClassName.methodName', 'functionName', or 'module.ClassName'. Prioritize those that contain "
        "security vulnerabilities, demonstrate security patterns, show authentication/authorization logic, or "
        "represent key security architectural decisions."
    ),
    "issues_found": (
        "List of security issues identified during the investigation. Each issue should be a dictionary with "
        "'severity' (critical, high, medium, low) and 'description' fields. Include security vulnerabilities, "
        "authentication bypasses, authorization flaws, injection vulnerabilities, cryptographic weaknesses, "
        "configuration issues, compliance gaps, etc."
    ),
    "confidence": (
        "Indicate your current confidence in the security audit assessment. Use: 'exploring' (starting analysis), "
        "'low' (early investigation), 'medium' (some evidence gathered), 'high' (strong evidence), "
        "'very_high' (very strong evidence), 'almost_certain' (nearly complete audit), 'certain' "
        "(100% confidence - security audit is thoroughly complete and all significant security issues are identified with no need for external model validation). "
        "Do NOT use 'certain' unless the security audit is comprehensively complete, use 'very_high' or 'almost_certain' instead if not 100% sure. "
        "Using 'certain' means you have complete confidence locally and prevents external model validation."
    ),
    "backtrack_from_step": (
        "If an earlier finding or assessment needs to be revised or discarded, specify the step number from which "
        "to start over. Use this to acknowledge investigative dead ends and correct the course."
    ),
    "images": (
        "Optional list of absolute paths to architecture diagrams, security models, threat models, or visual "
        "references that help with security audit context. Only include if they materially assist understanding "
        "or assessment of security posture."
    ),
    "security_scope": (
        "Define the security scope and application context (web app, mobile app, API, enterprise system, "
        "cloud service). Include technology stack, user types, data sensitivity, and threat landscape. "
        "This helps focus the security assessment appropriately."
    ),
    "threat_level": (
        "Assess the threat level based on application context: 'low' (internal tools, low-risk data), "
        "'medium' (customer-facing, business data), 'high' (financial, healthcare, regulated industry), "
        "'critical' (payment processing, sensitive personal data). This guides prioritization."
    ),
    "compliance_requirements": (
        "List applicable compliance frameworks and security standards (SOC2, PCI DSS, HIPAA, GDPR, "
        "ISO 27001, NIST). Include industry-specific requirements that affect security controls."
    ),
    "audit_focus": "Primary security focus areas for this audit (owasp, compliance, infrastructure, dependencies)",
    "severity_filter": "Minimum severity level to report on the security issues found",
}


__all__ = ["SECAUDIT_WORKFLOW_FIELD_DESCRIPTIONS"]

