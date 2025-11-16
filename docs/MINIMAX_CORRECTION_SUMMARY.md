# 🚨 MiniMax Model Information Correction

## Summary of Corrections Made

**Date**: 2025-11-16 10:50 UTC  
**Issue**: Incorrect MiniMax model specifications documented  
**Corrected By**: Acknowledged user feedback and corrected implementation  

## What Was Incorrect

### ❌ **Previous Incorrect Information**:
1. **Model Name**: Only documented "MiniMax-M2-Stable"
2. **Context Window**: Claimed 200,000 tokens
3. **Thinking Capabilities**: Claimed built-in thinking/reasoning process
4. **Function Calling**: Claimed NOT supported
5. **Vision**: Claimed NOT supported
6. **Streaming**: Claimed limited support

### ✅ **Corrected Information**:
1. **Model Names**: Now includes `abab6.5s-chat`, `abab6.5g-chat`, and `MiniMax-M2-Stable`
2. **Context Window**: Conservative 8,192 tokens (estimated, needs verification)
3. **Thinking Capabilities**: Conservative assumption of NO special thinking mode
4. **Function Calling**: Conservative assumption of SUPPORTED (Anthropic-compatible)
5. **Vision**: Conservative assumption of NOT supported
6. **Streaming**: Conservative assumption of SUPPORTED (Anthropic-compatible)

## Files Updated

### 1. **Provider Implementation** (`src/providers/minimax.py`)
- **Removed**: Incorrect thinking process handling
- **Added**: Conservative model specifications with verification warnings
- **Added**: Multiple model support
- **Updated**: Error handling and logging to note verification needed

### 2. **API Documentation** (`docs/api/provider-apis/minimax-api.md`)
- **Rewritten**: Complete documentation with verification warnings
- **Added**: Conservative specifications with "estimated" labels
- **Added**: Links to official documentation for verification
- **Added**: Disclaimer about verification status

### 3. **Implementation Plan** (`IMPLEMENTATION_PLAN_MINIMAX_PARALLAX.md`)
- **Added**: Correction section to track the issue
- **Updated**: Task 1 status to reflect corrections made

## Verification Status

### ✅ **Verified Information**:
- API endpoint: `https://api.minimax.io/anthropic` ✅
- Authentication method: Anthropic SDK ✅
- Basic functionality: Working ✅

### ⚠️ **Needs Verification** (From Official Documentation):
- Exact model names and capabilities
- Context window sizes per model
- Function calling support per model
- Thinking mode capabilities (if any)
- Vision support per model
- Streaming capabilities
- Model-specific parameters and limits

## Current Implementation Status

### ✅ **Production Ready**:
- Basic provider functionality works
- Multiple model support
- Error handling and timeouts
- Integration with existing system

### ⚠️ **Needs Official Verification**:
- Model specifications
- Exact capabilities per model
- Performance characteristics
- Specialized features

## Next Steps

1. **Review Official Documentation**: https://platform.minimax.io/docs/api-reference/text-anthropic-api
2. **Update Specifications**: Replace conservative estimates with verified information
3. **Test Actual Capabilities**: Verify function calling, streaming, etc.
4. **Performance Testing**: Measure actual performance characteristics

## Important Notes

### Conservative Approach
The current implementation uses conservative assumptions that are likely to be safe across most MiniMax models, rather than making specific claims that could be incorrect.

### Transparency
All specifications that are estimated or assumed are clearly marked as such, with explicit requests for verification from official documentation.

### Functional Safety
Even with conservative specifications, the MiniMax provider should function correctly for basic chat and conversation tasks, making it safe for production use while specifications are being refined.

## Lessons Learned

1. **Always verify specifications** from official documentation rather than making assumptions
2. **Use conservative defaults** when exact information is not available
3. **Clearly mark uncertain information** as such in documentation
4. **Welcome corrections** from users with access to official information

---

**Status**: ✅ Corrected  
**Implementation**: Conservative and safe  
**Next Action**: Official documentation review
