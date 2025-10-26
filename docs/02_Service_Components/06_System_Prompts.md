# System Prompts Management

## Purpose & Responsibility

This component manages AI system prompts through templates, versioning, and variable substitution, enabling consistent and reusable prompt engineering across the platform.

## Template Structure

### Prompt Template Schema

```typescript
// types/prompt.ts
export interface PromptTemplate {
  id: string;
  name: string;
  description: string;
  category: string;
  template: string;
  variables: PromptVariable[];
  version: string;
  compatibleModels: string[];
  tags: string[];
  createdAt: Date;
  updatedAt: Date;
}

export interface PromptVariable {
  name: string;
  type: 'string' | 'number' | 'boolean' | 'array';
  description: string;
  required: boolean;
  defaultValue?: any;
}
```

### YAML Template Format

```yaml
# templates/chat-assistant.yaml
id: chat-assistant
name: General Chat Assistant
description: A versatile chat assistant for general conversations
category: chat
version: 1.0.0
compatibleModels:
  - kimi-k2-0905-preview
  - glm-4.6
  - gpt-4
tags:
  - chat
  - general
template: |
  You are a helpful AI assistant named {{assistant_name}}.
  
  Your personality: {{personality}}
  
  Instructions:
  - Be helpful and concise
  - If you don't know something, say so
  - Do not make up information
  
  User question: {{question}}

variables:
  - name: assistant_name
    type: string
    description: Name of the assistant
    required: false
    defaultValue: "EXAI Assistant"
  
  - name: personality
    type: string
    description: Personality traits
    required: false
    defaultValue: "friendly and professional"
  
  - name: question
    type: string
    description: User's question
    required: true
```

## Prompt Service

### Template Management

```python
# services/prompt_service.py
import yaml
from typing import Dict, List, Optional
from pathlib import Path

class PromptService:
    def __init__(self, templates_dir: str = "templates"):
        self.templates_dir = Path(templates_dir)
        self.templates: Dict[str, PromptTemplate] = {}
        self.load_templates()
    
    def load_templates(self):
        """Load all YAML templates from templates directory"""
        for yaml_file in self.templates_dir.glob("*.yaml"):
            with open(yaml_file, 'r') as f:
                data = yaml.safe_load(f)
                template = PromptTemplate(**data)
                self.templates[template.id] = template
    
    def get_template(self, template_id: str) -> Optional[PromptTemplate]:
        """Get template by ID"""
        return self.templates.get(template_id)
    
    def list_templates(
        self, 
        category: Optional[str] = None,
        model: Optional[str] = None
    ) -> List[PromptTemplate]:
        """List templates with optional filtering"""
        templates = list(self.templates.values())
        
        if category:
            templates = [t for t in templates if t.category == category]
        
        if model:
            templates = [t for t in templates if model in t.compatibleModels]
        
        return templates
    
    def render_template(
        self, 
        template_id: str, 
        variables: Dict[str, any]
    ) -> str:
        """Render template with variables"""
        template = self.get_template(template_id)
        if not template:
            raise ValueError(f"Template {template_id} not found")
        
        # Validate variables
        self.validate_variables(template, variables)
        
        # Apply defaults
        final_vars = self.apply_defaults(template, variables)
        
        # Render template
        return self.substitute_variables(template.template, final_vars)
    
    def validate_variables(
        self, 
        template: PromptTemplate, 
        variables: Dict[str, any]
    ):
        """Validate provided variables against template requirements"""
        for var in template.variables:
            if var.required and var.name not in variables:
                raise ValueError(f"Required variable '{var.name}' is missing")
            
            if var.name in variables:
                provided_type = type(variables[var.name]).__name__
                if provided_type != var.type:
                    raise TypeError(
                        f"Variable '{var.name}' should be {var.type}, "
                        f"got {provided_type}"
                    )
    
    def apply_defaults(
        self, 
        template: PromptTemplate, 
        variables: Dict[str, any]
    ) -> Dict[str, any]:
        """Apply default values for missing optional variables"""
        final_vars = variables.copy()
        
        for var in template.variables:
            if var.name not in final_vars and var.defaultValue is not None:
                final_vars[var.name] = var.defaultValue
        
        return final_vars
    
    def substitute_variables(
        self, 
        template: str, 
        variables: Dict[str, any]
    ) -> str:
        """Substitute {{variable}} placeholders with values"""
        import re
        
        def replace(match):
            var_name = match.group(1)
            if var_name in variables:
                return str(variables[var_name])
            return match.group(0)
        
        return re.sub(r'\{\{(\w+)\}\}', replace, template)
```

## Built-in Templates

### Code Review Template

```yaml
# templates/code-review.yaml
id: code-review
name: Code Review Assistant
description: Reviews code for quality, bugs, and best practices
category: code
version: 1.0.0
compatibleModels:
  - kimi-k2-0905-preview
  - glm-4.6
tags:
  - code
  - review
template: |
  You are an expert code reviewer specializing in {{language}}.
  
  Review the following code:
  
  ```{{language}}
  {{code}}
  ```
  
  Focus on:
  - Code quality and readability
  - Potential bugs or errors
  - Performance issues
  - Security vulnerabilities
  - Best practices for {{language}}
  
  Provide specific, actionable feedback.

variables:
  - name: language
    type: string
    description: Programming language
    required: true
  
  - name: code
    type: string
    description: Code to review
    required: true
```

### Debug Assistant Template

```yaml
# templates/debug-assistant.yaml
id: debug-assistant
name: Debug Assistant
description: Helps debug code issues
category: debug
version: 1.0.0
compatibleModels:
  - kimi-k2-0905-preview
  - glm-4.6
tags:
  - debug
  - troubleshooting
template: |
  You are a debugging expert for {{language}}.
  
  Problem: {{problem_description}}
  
  Code:
  ```{{language}}
  {{code}}
  ```
  
  {{#if error_message}}
  Error message:
  ```
  {{error_message}}
  ```
  {{/if}}
  
  Analyze the code and error, then:
  1. Identify the root cause
  2. Explain why it's happening
  3. Provide a fix with explanation
  4. Suggest how to prevent similar issues

variables:
  - name: language
    type: string
    description: Programming language
    required: true
  
  - name: problem_description
    type: string
    description: Description of the problem
    required: true
  
  - name: code
    type: string
    description: Code with the issue
    required: true
  
  - name: error_message
    type: string
    description: Error message if available
    required: false
```

## Usage Examples

### Using Prompt Service

```python
# Example usage
from services.prompt_service import PromptService

# Initialize service
prompt_service = PromptService(templates_dir="templates")

# List all templates
all_templates = prompt_service.list_templates()

# Get specific template
template = prompt_service.get_template("chat-assistant")

# Render template with variables
rendered = prompt_service.render_template(
    template_id="chat-assistant",
    variables={
        "assistant_name": "CodeHelper",
        "personality": "technical and precise",
        "question": "How do I optimize this SQL query?"
    }
)

print(rendered)
```

### API Integration

```python
# routes/prompts.py
from fastapi import APIRouter, HTTPException
from services.prompt_service import PromptService

router = APIRouter()
prompt_service = PromptService()

@router.get("/templates")
async def list_templates(category: str = None, model: str = None):
    templates = prompt_service.list_templates(category=category, model=model)
    return {"templates": templates}

@router.post("/render")
async def render_template(template_id: str, variables: dict):
    try:
        rendered = prompt_service.render_template(template_id, variables)
        return {"prompt": rendered}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except TypeError as e:
        raise HTTPException(status_code=400, detail=str(e))
```

## Configuration

### Template Directory Structure

```
templates/
├── chat/
│   ├── general-assistant.yaml
│   └── technical-support.yaml
├── code/
│   ├── code-review.yaml
│   ├── code-generation.yaml
│   └── refactoring.yaml
├── debug/
│   └── debug-assistant.yaml
└── analysis/
    ├── data-analysis.yaml
    └── text-analysis.yaml
```

## Best Practices

1. **Version Control**: Always version templates for backward compatibility
2. **Variable Validation**: Strictly validate all variables before rendering
3. **Model Compatibility**: Clearly specify compatible models
4. **Security**: Sanitize user inputs to prevent injection attacks
5. **Documentation**: Document each variable's purpose and format

## Integration Points

- **Chat Interface**: Uses templates for system prompts
- **API Layer**: Exposes template management endpoints
- **Provider Layer**: Sends rendered prompts to AI models
- **Supabase**: Stores template usage analytics

