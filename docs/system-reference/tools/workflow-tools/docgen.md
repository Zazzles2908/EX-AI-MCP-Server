

**Version:** 1.1  
**Last Updated:** 2025-10-03  
**Category:** Workflow Tool (Multi-Step Investigation)  
**Related:** [analyze.md](analyze.md), [debug.md](debug.md)

---


---

### docgen_EXAI-WS

**Purpose:** Comprehensive documentation generation with complexity analysis

**Description:**
The `docgen` tool creates thorough documentation by analyzing code structure, understanding function complexity, and documenting gotchas and unexpected behaviors. This workflow tool guides the AI client through systematic investigation of code functionality before generating comprehensive documentation.

**Use Cases:**
- Comprehensive documentation generation for undocumented code
- Code documentation analysis and quality assessment
- Complexity assessment with Big O notation
- Documentation modernization and style updates
- API documentation with call flow information
- Gotchas and unexpected behavior documentation

**Key Features:**
- **Systematic file-by-file approach** - Complete documentation with progress tracking
- **Modern documentation styles** - Enforces /// for Objective-C/Swift, /** */ for Java/JavaScript
- **Complexity analysis** - Big O notation for algorithms and performance characteristics
- **Call flow documentation** - Dependencies and method relationships
- **Counter-based completion** - Prevents stopping until all files are documented
- **Large file handling** - Systematic portion-by-portion documentation
- **Final verification scan** - Mandatory check to ensure no functions are missed
- **Bug tracking** - Surfaces code issues without altering logic
- **Configuration parameters** - Control complexity analysis, call flow, inline comments

**Key Parameters:**

*Workflow Parameters:*
- `step` (required): Current step description - discovery (step 1) or documentation (step 2+)
- `step_number` (required): Current step number in documentation sequence
- `total_steps` (required): Dynamically calculated as 1 + total_files_to_document
- `next_step_required` (required): Whether another step is needed
- `findings` (required): Discoveries about code structure and documentation needs
- `relevant_files` (optional): Files being actively documented in current step
- `num_files_documented` (required): Counter tracking completed files (starts at 0)
- `total_files_to_document` (required): Total count of files needing documentation

*Configuration Parameters (required fields):*
- `document_complexity` (required): Include Big O complexity analysis (default: true)
- `document_flow` (required): Include call flow and dependency information (default: true)
- `update_existing` (required): Update existing documentation when incorrect/incomplete (default: true)
- `comments_on_complex_logic` (required): Add inline comments for complex algorithmic steps (default: true)

**Critical Counters:**
- `num_files_documented`: Increment by 1 ONLY when file is 100% documented
- `total_files_to_document`: Set in step 1 after discovering all files
- **Cannot set `next_step_required=false` unless `num_files_documented == total_files_to_document`**

**Workflow:**
1. **Step 1 (Discovery)**: Discover ALL files needing documentation and report exact count
2. **Step 2+ (Documentation)**: Document files one-by-one with complete coverage validation
3. **Throughout**: Track progress with counters and enforce modern documentation styles
4. **Completion**: Only when all files are documented (counters match)
5. **Documentation Generation**: Complete documentation with style consistency

**Usage Examples:**

*Class Documentation:*
```
"Generate comprehensive documentation for the PaymentProcessor class including complexity analysis"
```

*Module Documentation:*
```
"Document all functions in the authentication module with call flow information"
```

*API Documentation:*
```
"Create API documentation for the REST endpoints with complexity and flow analysis"
```

**Best Practices:**
- Let the tool discover all files first (step 1)
- Document one file at a time for thoroughness
- Include complexity analysis for algorithms
- Document call flows for better understanding
- Update existing docs when incorrect
- Add inline comments for complex logic

**When to Use:**
- Use `docgen` for: Generating comprehensive documentation with complexity analysis
- Use `codereview` for: Finding bugs and improving code quality
- Use `analyze` for: Understanding code structure
- Use `refactor` for: Improving code organization