# secaudit_EXAI-WS

**Version:** 1.1  
**Last Updated:** 2025-10-03  
**Category:** Workflow Tool (Multi-Step Investigation)  
**Related:** [analyze.md](analyze.md), [debug.md](debug.md)

---



**Purpose:** Comprehensive security audit with OWASP-based assessment

**Description:**
The `secaudit` tool provides comprehensive security auditing capabilities with systematic OWASP Top 10 assessment, compliance framework evaluation, and threat modeling. This workflow tool guides the AI client through methodical security investigation with forced pauses to ensure thorough vulnerability assessment.

**IMPORTANT**: AI models may not identify all security vulnerabilities. Always perform additional manual security reviews, penetration testing, and verification.

**Use Cases:**
- Comprehensive security assessment with OWASP Top 10 coverage
- Compliance evaluation (SOC2, PCI DSS, HIPAA, GDPR, FedRAMP)
- Vulnerability identification and threat modeling
- Security architecture review and attack surface mapping
- Authentication and authorization assessment
- Input validation and data security review

**Key Features:**
- **OWASP Top 10 (2021) systematic assessment** with specific vulnerability identification
- **Multi-compliance framework support**: SOC2, PCI DSS, HIPAA, GDPR, FedRAMP
- **Threat-level aware analysis**: Critical, high, medium, low threat classifications
- **Technology-specific security patterns**: Web apps, APIs, mobile, cloud, enterprise systems
- **Risk-based prioritization**: Business impact and exploitability assessment
- **Audit focus customization**: Comprehensive, authentication, data protection, infrastructure
- **Image support**: Security analysis from architecture diagrams, network topology
- **Multi-file security analysis**: Cross-component vulnerability identification
- **Compliance gap analysis**: Specific framework requirements with remediation guidance
- **Attack surface mapping**: Entry points, data flows, privilege boundaries
- **Security control effectiveness**: Evaluation of existing security measures

**Key Parameters:**

*Workflow Investigation Parameters:*
- `step` (required): Current security investigation step description
- `step_number` (required): Current step number in audit sequence
- `total_steps` (required): Estimated total investigation steps (typically 4-6)
- `next_step_required` (required): Whether another investigation step is needed
- `findings` (required): Security discoveries and evidence collected
- `files_checked` (optional): All files examined during security investigation
- `relevant_files` (required in step 1): Files directly relevant to security audit (absolute paths)
- `relevant_context` (optional): Methods/functions/classes with security implications
- `issues_found` (optional): Security issues with severity levels
- `confidence` (optional): Confidence level in audit completeness
- `images` (optional): Visual references (architecture diagrams, network topology)

*Initial Configuration:*
- `model` (optional): Model to use (default: auto)
- `audit_focus` (optional): owasp|compliance|infrastructure|dependencies|comprehensive (default: comprehensive)
- `threat_level` (optional): low|medium|high|critical (default: medium)
- `security_scope` (optional): Application context (web app, mobile app, API, enterprise system)
- `compliance_requirements` (optional): List of applicable frameworks (SOC2, PCI DSS, HIPAA, GDPR, ISO 27001)
- `severity_filter` (optional): critical|high|medium|low|all (default: all)
- `thinking_mode` (optional): Thinking depth (default: medium)
- `use_websearch` (optional): Enable web search (default: true)
- `use_assistant_model` (optional): Use expert analysis phase (default: true)

**Workflow:**
1. **Step 1**: Security scope analysis - identify application type, tech stack, attack surface
2. **Step 2**: Authentication & authorization assessment
3. **Step 3**: Input validation & data security review
4. **Step 4**: OWASP Top 10 (2021) systematic review
5. **Step 5**: Dependencies & infrastructure security
6. **Step 6**: Compliance & risk assessment
7. **Expert Analysis**: Comprehensive security assessment summary

**Usage Examples:**

*E-Commerce Security Audit:*
```
"Perform a secaudit on this e-commerce web application focusing on payment processing security and PCI DSS compliance"
```

*Authentication System Audit:*
```
"Conduct a comprehensive security audit of the authentication system, threat level high, focus on HIPAA compliance"
```

*API Security Assessment:*
```
"Security audit of REST API focusing on OWASP Top 10 and authentication vulnerabilities"
```

**Best Practices:**
- Define security scope and application context clearly
- Specify compliance requirements upfront
- Use appropriate threat level for risk prioritization
- Include architecture diagrams for better context
- Focus on specific audit areas for targeted assessment

**When to Use:**
- Use `secaudit` for: Comprehensive security assessment and vulnerability identification
- Use `codereview` for: General code quality with some security considerations
- Use `analyze` for: Understanding code structure without security focus