# Caching

**Version:** 1.1  
**Last Updated:** 2025-10-03  
**Related:** [../04-features-and-capabilities.md](../04-features-and-capabilities.md), [../providers/kimi.md](../providers/kimi.md)

---

## Overview

Prompt caching and advanced caching strategies for improved performance and cost reduction. Both GLM and Kimi providers support caching with different implementations.

---

## Provider Support

### GLM Provider - Prompt Caching

**Features:**
- Automatic prompt caching
- Reduced costs for repeated prompts
- Faster response times

**Configuration:**
```env
GLM_ENABLE_CACHING=true
```

### Kimi Provider - Advanced Caching

**Features:**
- Automatic prompt caching
- Up to 90% cost reduction for repeated prompts
- Significantly faster response times
- No configuration required

**Benefits:**
- Ideal for iterative workflows
- Reduced costs for repeated queries
- Faster response times for cached content

---

## Caching Strategies

### Automatic Caching
- Both providers cache prompts automatically
- No manual configuration required
- Transparent to the user

### Cache Invalidation
- Caches expire after a certain period
- New prompts invalidate old caches
- Provider-managed cache lifecycle

---

## Best Practices

- Use consistent prompts for better caching
- Leverage caching for iterative workflows
- Monitor cache hit rates for optimization
- Use Kimi for maximum caching benefits

---

## Related Documentation

- [../04-features-and-capabilities.md](../04-features-and-capabilities.md) - Features overview
- [../providers/glm.md](../providers/glm.md) - GLM caching details
- [../providers/kimi.md](../providers/kimi.md) - Kimi caching details

