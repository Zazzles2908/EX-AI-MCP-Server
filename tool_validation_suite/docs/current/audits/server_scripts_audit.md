# Server Scripts Audit Report

**Date:** 2025-10-07

**Total Issues Found:** 172

## 🔴 CRITICAL ISSUES (127)

### Silent Failures

**src\daemon\ws_server.py:131**
- Bare except with pass (silent failure)
- Context: `except Exception:`

**src\daemon\ws_server.py:186**
- Bare except with pass (silent failure)
- Context: `except Exception:`

**src\daemon\ws_server.py:249**
- Bare except with pass (silent failure)
- Context: `except Exception:`

**src\daemon\ws_server.py:358**
- Bare except with pass (silent failure)
- Context: `except Exception:`

**src\daemon\ws_server.py:396**
- Bare except with pass (silent failure)
- Context: `except Exception:`

**src\daemon\ws_server.py:532**
- Bare except with pass (silent failure)
- Context: `except Exception:`

**src\daemon\ws_server.py:550**
- Bare except with pass (silent failure)
- Context: `except Exception:`

**src\daemon\ws_server.py:574**
- Bare except with pass (silent failure)
- Context: `except Exception:`

**src\daemon\ws_server.py:601**
- Bare except with pass (silent failure)
- Context: `except Exception:`

**src\daemon\ws_server.py:614**
- Bare except with pass (silent failure)
- Context: `except Exception:`

**src\daemon\ws_server.py:635**
- Bare except with pass (silent failure)
- Context: `except Exception:`

**src\daemon\ws_server.py:649**
- Bare except with pass (silent failure)
- Context: `except Exception:`

**src\daemon\ws_server.py:689**
- Bare except with pass (silent failure)
- Context: `except Exception:`

**src\daemon\ws_server.py:703**
- Bare except with pass (silent failure)
- Context: `except Exception:`

**src\daemon\ws_server.py:728**
- Bare except with pass (silent failure)
- Context: `except Exception:`

**src\daemon\ws_server.py:742**
- Bare except with pass (silent failure)
- Context: `except Exception:`

**src\daemon\ws_server.py:768**
- Bare except with pass (silent failure)
- Context: `except Exception:`

**src\daemon\ws_server.py:782**
- Bare except with pass (silent failure)
- Context: `except Exception:`

**src\daemon\ws_server.py:788**
- Bare except with pass (silent failure)
- Context: `except Exception:`

**src\daemon\ws_server.py:793**
- Bare except with pass (silent failure)
- Context: `except Exception:`

**src\daemon\ws_server.py:797**
- Bare except with pass (silent failure)
- Context: `except Exception:`

**src\daemon\ws_server.py:843**
- Bare except with pass (silent failure)
- Context: `except Exception:`

**src\daemon\ws_server.py:855**
- Bare except with pass (silent failure)
- Context: `except Exception:`

**src\daemon\ws_server.py:857**
- Bare except with pass (silent failure)
- Context: `except Exception:`

**src\daemon\ws_server.py:866**
- Bare except with pass (silent failure)
- Context: `except Exception:`

**src\daemon\ws_server.py:868**
- Bare except with pass (silent failure)
- Context: `except Exception:`

**src\daemon\ws_server.py:879**
- Bare except with pass (silent failure)
- Context: `except Exception:`

**src\daemon\ws_server.py:881**
- Bare except with pass (silent failure)
- Context: `except Exception:`

**src\daemon\ws_server.py:904**
- Bare except with pass (silent failure)
- Context: `except Exception:`

**src\daemon\ws_server.py:913**
- Bare except with pass (silent failure)
- Context: `except Exception:`

**src\daemon\ws_server.py:928**
- Bare except with pass (silent failure)
- Context: `except Exception:`

**src\daemon\ws_server.py:956**
- Bare except with pass (silent failure)
- Context: `except Exception:`

**src\daemon\ws_server.py:131**
- Broad exception with pass
- Context: `except Exception:`

**src\daemon\ws_server.py:186**
- Broad exception with pass
- Context: `except Exception:`

**src\daemon\ws_server.py:249**
- Broad exception with pass
- Context: `except Exception:`

**src\daemon\ws_server.py:358**
- Broad exception with pass
- Context: `except Exception:`

**src\daemon\ws_server.py:396**
- Broad exception with pass
- Context: `except Exception:`

**src\daemon\ws_server.py:532**
- Broad exception with pass
- Context: `except Exception:`

**src\daemon\ws_server.py:550**
- Broad exception with pass
- Context: `except Exception:`

**src\daemon\ws_server.py:574**
- Broad exception with pass
- Context: `except Exception:`

**src\daemon\ws_server.py:601**
- Broad exception with pass
- Context: `except Exception:`

**src\daemon\ws_server.py:614**
- Broad exception with pass
- Context: `except Exception:`

**src\daemon\ws_server.py:635**
- Broad exception with pass
- Context: `except Exception:`

**src\daemon\ws_server.py:649**
- Broad exception with pass
- Context: `except Exception:`

**src\daemon\ws_server.py:689**
- Broad exception with pass
- Context: `except Exception:`

**src\daemon\ws_server.py:703**
- Broad exception with pass
- Context: `except Exception:`

**src\daemon\ws_server.py:728**
- Broad exception with pass
- Context: `except Exception:`

**src\daemon\ws_server.py:742**
- Broad exception with pass
- Context: `except Exception:`

**src\daemon\ws_server.py:768**
- Broad exception with pass
- Context: `except Exception:`

**src\daemon\ws_server.py:782**
- Broad exception with pass
- Context: `except Exception:`

**src\daemon\ws_server.py:788**
- Broad exception with pass
- Context: `except Exception:`

**src\daemon\ws_server.py:793**
- Broad exception with pass
- Context: `except Exception:`

**src\daemon\ws_server.py:797**
- Broad exception with pass
- Context: `except Exception:`

**src\daemon\ws_server.py:843**
- Broad exception with pass
- Context: `except Exception:`

**src\daemon\ws_server.py:855**
- Broad exception with pass
- Context: `except Exception:`

**src\daemon\ws_server.py:857**
- Broad exception with pass
- Context: `except Exception:`

**src\daemon\ws_server.py:866**
- Broad exception with pass
- Context: `except Exception:`

**src\daemon\ws_server.py:868**
- Broad exception with pass
- Context: `except Exception:`

**src\daemon\ws_server.py:879**
- Broad exception with pass
- Context: `except Exception:`

**src\daemon\ws_server.py:881**
- Broad exception with pass
- Context: `except Exception:`

**src\daemon\ws_server.py:904**
- Broad exception with pass
- Context: `except Exception:`

**src\daemon\ws_server.py:913**
- Broad exception with pass
- Context: `except Exception:`

**src\daemon\ws_server.py:928**
- Broad exception with pass
- Context: `except Exception:`

**src\daemon\ws_server.py:956**
- Broad exception with pass
- Context: `except Exception:`

**src\providers\kimi_chat.py:118**
- Bare except with pass (silent failure)
- Context: `except Exception:`

**src\providers\kimi_chat.py:118**
- Broad exception with pass
- Context: `except Exception:`

**src\providers\openai_compatible.py:505**
- Bare except with pass (silent failure)
- Context: `except Exception:`

**src\providers\openai_compatible.py:523**
- Bare except with pass (silent failure)
- Context: `except Exception:`

**src\providers\openai_compatible.py:568**
- Bare except with pass (silent failure)
- Context: `except Exception:`

**src\providers\openai_compatible.py:588**
- Bare except with pass (silent failure)
- Context: `except Exception:`

**src\providers\openai_compatible.py:648**
- Bare except with pass (silent failure)
- Context: `except Exception:`

**src\providers\openai_compatible.py:654**
- Bare except with pass (silent failure)
- Context: `except Exception:`

**src\providers\openai_compatible.py:661**
- Bare except with pass (silent failure)
- Context: `except Exception:`

**src\providers\openai_compatible.py:903**
- Bare except with pass (silent failure)
- Context: `except Exception:`

**src\providers\openai_compatible.py:505**
- Broad exception with pass
- Context: `except Exception:`

**src\providers\openai_compatible.py:523**
- Broad exception with pass
- Context: `except Exception:`

**src\providers\openai_compatible.py:568**
- Broad exception with pass
- Context: `except Exception:`

**src\providers\openai_compatible.py:588**
- Broad exception with pass
- Context: `except Exception:`

**src\providers\openai_compatible.py:648**
- Broad exception with pass
- Context: `except Exception:`

**src\providers\openai_compatible.py:654**
- Broad exception with pass
- Context: `except Exception:`

**src\providers\openai_compatible.py:661**
- Broad exception with pass
- Context: `except Exception:`

**src\providers\openai_compatible.py:903**
- Broad exception with pass
- Context: `except Exception:`

### Ast Issues

**src\daemon\ws_server.py:131**
- Empty except with pass (silent failure)

**src\daemon\ws_server.py:186**
- Empty except with pass (silent failure)

**src\daemon\ws_server.py:249**
- Empty except with pass (silent failure)

**src\daemon\ws_server.py:358**
- Empty except with pass (silent failure)

**src\daemon\ws_server.py:396**
- Empty except with pass (silent failure)

**src\daemon\ws_server.py:532**
- Empty except with pass (silent failure)

**src\daemon\ws_server.py:550**
- Empty except with pass (silent failure)

**src\daemon\ws_server.py:574**
- Empty except with pass (silent failure)

**src\daemon\ws_server.py:601**
- Empty except with pass (silent failure)

**src\daemon\ws_server.py:614**
- Empty except with pass (silent failure)

**src\daemon\ws_server.py:635**
- Empty except with pass (silent failure)

**src\daemon\ws_server.py:649**
- Empty except with pass (silent failure)

**src\daemon\ws_server.py:689**
- Empty except with pass (silent failure)

**src\daemon\ws_server.py:703**
- Empty except with pass (silent failure)

**src\daemon\ws_server.py:728**
- Empty except with pass (silent failure)

**src\daemon\ws_server.py:742**
- Empty except with pass (silent failure)

**src\daemon\ws_server.py:768**
- Empty except with pass (silent failure)

**src\daemon\ws_server.py:782**
- Empty except with pass (silent failure)

**src\daemon\ws_server.py:788**
- Empty except with pass (silent failure)

**src\daemon\ws_server.py:793**
- Empty except with pass (silent failure)

**src\daemon\ws_server.py:797**
- Empty except with pass (silent failure)

**src\daemon\ws_server.py:843**
- Empty except with pass (silent failure)

**src\daemon\ws_server.py:857**
- Empty except with pass (silent failure)

**src\daemon\ws_server.py:855**
- Empty except with pass (silent failure)

**src\daemon\ws_server.py:868**
- Empty except with pass (silent failure)

**src\daemon\ws_server.py:866**
- Empty except with pass (silent failure)

**src\daemon\ws_server.py:881**
- Empty except with pass (silent failure)

**src\daemon\ws_server.py:879**
- Empty except with pass (silent failure)

**src\daemon\ws_server.py:922**
- Empty except with pass (silent failure)

**src\daemon\ws_server.py:904**
- Empty except with pass (silent failure)

**src\daemon\ws_server.py:913**
- Empty except with pass (silent failure)

**src\daemon\ws_server.py:928**
- Empty except with pass (silent failure)

**src\daemon\ws_server.py:956**
- Empty except with pass (silent failure)

**src\daemon\ws_server.py:975**
- Empty except with pass (silent failure)

**src\providers\kimi_chat.py:118**
- Empty except with pass (silent failure)

**src\providers\glm_chat.py:59**
- Empty except with pass (silent failure)

**src\providers\openai_compatible.py:160**
- Empty except with pass (silent failure)

**src\providers\openai_compatible.py:505**
- Empty except with pass (silent failure)

**src\providers\openai_compatible.py:523**
- Empty except with pass (silent failure)

**src\providers\openai_compatible.py:568**
- Empty except with pass (silent failure)

**src\providers\openai_compatible.py:588**
- Empty except with pass (silent failure)

**src\providers\openai_compatible.py:648**
- Empty except with pass (silent failure)

**src\providers\openai_compatible.py:654**
- Empty except with pass (silent failure)

**src\providers\openai_compatible.py:661**
- Empty except with pass (silent failure)

**src\providers\openai_compatible.py:903**
- Empty except with pass (silent failure)

## Legacy References (2 findings)

### src\daemon\ws_server.py

🟠 **Line 14:** Explicitly marked as deprecated
   - `# Note: Using generic type hint instead of deprecated WebSocketServerProtocol`

🟠 **Line 15:** Explicitly marked as deprecated
   - `# The websockets library deprecated WebSocketServerProtocol in favor of the new asyncio API`

## Silent Failures (88 findings)

### src\daemon\ws_server.py

🔴 **Line 131:** Bare except with pass (silent failure)
   - `except Exception:`

🔴 **Line 131:** Broad exception with pass
   - `except Exception:`

🔴 **Line 186:** Bare except with pass (silent failure)
   - `except Exception:`

🔴 **Line 186:** Broad exception with pass
   - `except Exception:`

🔴 **Line 249:** Bare except with pass (silent failure)
   - `except Exception:`

🔴 **Line 249:** Broad exception with pass
   - `except Exception:`

🟡 **Line 275:** Exception returning None (may hide errors)
   - `except (websockets.exceptions.ConnectionClosedError, ConnectionAbortedError, ConnectionResetError):`

🟡 **Line 277:** Exception returning None (may hide errors)
   - `except asyncio.TimeoutError:`

🔴 **Line 358:** Bare except with pass (silent failure)
   - `except Exception:`

🔴 **Line 358:** Broad exception with pass
   - `except Exception:`

🔴 **Line 396:** Bare except with pass (silent failure)
   - `except Exception:`

🔴 **Line 396:** Broad exception with pass
   - `except Exception:`

🔴 **Line 532:** Bare except with pass (silent failure)
   - `except Exception:`

🔴 **Line 532:** Broad exception with pass
   - `except Exception:`

🔴 **Line 550:** Bare except with pass (silent failure)
   - `except Exception:`

🔴 **Line 550:** Broad exception with pass
   - `except Exception:`

🔴 **Line 574:** Bare except with pass (silent failure)
   - `except Exception:`

🔴 **Line 574:** Broad exception with pass
   - `except Exception:`

🔴 **Line 601:** Bare except with pass (silent failure)
   - `except Exception:`

🔴 **Line 601:** Broad exception with pass
   - `except Exception:`

🔴 **Line 614:** Bare except with pass (silent failure)
   - `except Exception:`

🔴 **Line 614:** Broad exception with pass
   - `except Exception:`

🔴 **Line 635:** Bare except with pass (silent failure)
   - `except Exception:`

🔴 **Line 635:** Broad exception with pass
   - `except Exception:`

🔴 **Line 649:** Bare except with pass (silent failure)
   - `except Exception:`

🔴 **Line 649:** Broad exception with pass
   - `except Exception:`

🔴 **Line 689:** Bare except with pass (silent failure)
   - `except Exception:`

🔴 **Line 689:** Broad exception with pass
   - `except Exception:`

🔴 **Line 703:** Bare except with pass (silent failure)
   - `except Exception:`

🔴 **Line 703:** Broad exception with pass
   - `except Exception:`

🔴 **Line 728:** Bare except with pass (silent failure)
   - `except Exception:`

🔴 **Line 728:** Broad exception with pass
   - `except Exception:`

🔴 **Line 742:** Bare except with pass (silent failure)
   - `except Exception:`

🔴 **Line 742:** Broad exception with pass
   - `except Exception:`

🔴 **Line 768:** Bare except with pass (silent failure)
   - `except Exception:`

🔴 **Line 768:** Broad exception with pass
   - `except Exception:`

🔴 **Line 782:** Bare except with pass (silent failure)
   - `except Exception:`

🔴 **Line 782:** Broad exception with pass
   - `except Exception:`

🔴 **Line 788:** Bare except with pass (silent failure)
   - `except Exception:`

🔴 **Line 788:** Broad exception with pass
   - `except Exception:`

🔴 **Line 793:** Bare except with pass (silent failure)
   - `except Exception:`

🔴 **Line 793:** Broad exception with pass
   - `except Exception:`

🔴 **Line 797:** Bare except with pass (silent failure)
   - `except Exception:`

🔴 **Line 797:** Broad exception with pass
   - `except Exception:`

🔴 **Line 843:** Bare except with pass (silent failure)
   - `except Exception:`

🔴 **Line 843:** Broad exception with pass
   - `except Exception:`

🔴 **Line 855:** Bare except with pass (silent failure)
   - `except Exception:`

🔴 **Line 855:** Broad exception with pass
   - `except Exception:`

🔴 **Line 857:** Bare except with pass (silent failure)
   - `except Exception:`

🔴 **Line 857:** Broad exception with pass
   - `except Exception:`

🔴 **Line 866:** Bare except with pass (silent failure)
   - `except Exception:`

🔴 **Line 866:** Broad exception with pass
   - `except Exception:`

🔴 **Line 868:** Bare except with pass (silent failure)
   - `except Exception:`

🔴 **Line 868:** Broad exception with pass
   - `except Exception:`

🔴 **Line 879:** Bare except with pass (silent failure)
   - `except Exception:`

🔴 **Line 879:** Broad exception with pass
   - `except Exception:`

🔴 **Line 881:** Bare except with pass (silent failure)
   - `except Exception:`

🔴 **Line 881:** Broad exception with pass
   - `except Exception:`

🔴 **Line 904:** Bare except with pass (silent failure)
   - `except Exception:`

🔴 **Line 904:** Broad exception with pass
   - `except Exception:`

🔴 **Line 913:** Bare except with pass (silent failure)
   - `except Exception:`

🔴 **Line 913:** Broad exception with pass
   - `except Exception:`

🔴 **Line 928:** Bare except with pass (silent failure)
   - `except Exception:`

🔴 **Line 928:** Broad exception with pass
   - `except Exception:`

🔴 **Line 956:** Bare except with pass (silent failure)
   - `except Exception:`

🔴 **Line 956:** Broad exception with pass
   - `except Exception:`

🟠 **Line 960:** Exception with continue (may hide errors)
   - `except asyncio.TimeoutError:`

### src\providers\glm_chat.py

🟠 **Line 164:** Exception with continue (may hide errors)
   - `except Exception:`

🟠 **Line 276:** Exception with continue (may hide errors)
   - `except Exception:`

### src\providers\kimi_chat.py

🔴 **Line 118:** Bare except with pass (silent failure)
   - `except Exception:`

🔴 **Line 118:** Broad exception with pass
   - `except Exception:`

### src\providers\openai_compatible.py

🔴 **Line 505:** Bare except with pass (silent failure)
   - `except Exception:`

🔴 **Line 505:** Broad exception with pass
   - `except Exception:`

🔴 **Line 523:** Bare except with pass (silent failure)
   - `except Exception:`

🔴 **Line 523:** Broad exception with pass
   - `except Exception:`

🔴 **Line 568:** Bare except with pass (silent failure)
   - `except Exception:`

🔴 **Line 568:** Broad exception with pass
   - `except Exception:`

🔴 **Line 588:** Bare except with pass (silent failure)
   - `except Exception:`

🔴 **Line 588:** Broad exception with pass
   - `except Exception:`

🟠 **Line 613:** Exception with continue (may hide errors)
   - `except Exception:`

🔴 **Line 648:** Bare except with pass (silent failure)
   - `except Exception:`

🔴 **Line 648:** Broad exception with pass
   - `except Exception:`

🔴 **Line 654:** Bare except with pass (silent failure)
   - `except Exception:`

🔴 **Line 654:** Broad exception with pass
   - `except Exception:`

🔴 **Line 661:** Bare except with pass (silent failure)
   - `except Exception:`

🔴 **Line 661:** Broad exception with pass
   - `except Exception:`

🔴 **Line 903:** Bare except with pass (silent failure)
   - `except Exception:`

🔴 **Line 903:** Broad exception with pass
   - `except Exception:`

## Code Smells (5 findings)

### src\providers\glm_chat.py

🟡 **Line 13:** Long parameter list (>100 chars)
   - `def build_payload(`

🟡 **Line 67:** Long parameter list (>100 chars)
   - `def generate_content(`

### src\providers\kimi_chat.py

🟡 **Line 35:** Long parameter list (>100 chars)
   - `def chat_completions_create(`

### src\providers\openai_compatible.py

🟡 **Line 335:** Long parameter list (>100 chars)
   - `def _generate_with_responses_endpoint(`

🟡 **Line 427:** Long parameter list (>100 chars)
   - `def generate_content(`

## Ast Issues (45 findings)

### src\daemon\ws_server.py

🔴 **Line 131:** Empty except with pass (silent failure)

🔴 **Line 186:** Empty except with pass (silent failure)

🔴 **Line 249:** Empty except with pass (silent failure)

🔴 **Line 358:** Empty except with pass (silent failure)

🔴 **Line 396:** Empty except with pass (silent failure)

🔴 **Line 532:** Empty except with pass (silent failure)

🔴 **Line 550:** Empty except with pass (silent failure)

🔴 **Line 574:** Empty except with pass (silent failure)

🔴 **Line 601:** Empty except with pass (silent failure)

🔴 **Line 614:** Empty except with pass (silent failure)

🔴 **Line 635:** Empty except with pass (silent failure)

🔴 **Line 649:** Empty except with pass (silent failure)

🔴 **Line 689:** Empty except with pass (silent failure)

🔴 **Line 703:** Empty except with pass (silent failure)

🔴 **Line 728:** Empty except with pass (silent failure)

🔴 **Line 742:** Empty except with pass (silent failure)

🔴 **Line 768:** Empty except with pass (silent failure)

🔴 **Line 782:** Empty except with pass (silent failure)

🔴 **Line 788:** Empty except with pass (silent failure)

🔴 **Line 793:** Empty except with pass (silent failure)

🔴 **Line 797:** Empty except with pass (silent failure)

🔴 **Line 843:** Empty except with pass (silent failure)

🔴 **Line 855:** Empty except with pass (silent failure)

🔴 **Line 857:** Empty except with pass (silent failure)

🔴 **Line 866:** Empty except with pass (silent failure)

🔴 **Line 868:** Empty except with pass (silent failure)

🔴 **Line 879:** Empty except with pass (silent failure)

🔴 **Line 881:** Empty except with pass (silent failure)

🔴 **Line 904:** Empty except with pass (silent failure)

🔴 **Line 913:** Empty except with pass (silent failure)

🔴 **Line 922:** Empty except with pass (silent failure)

🔴 **Line 928:** Empty except with pass (silent failure)

🔴 **Line 956:** Empty except with pass (silent failure)

🔴 **Line 975:** Empty except with pass (silent failure)

### src\providers\glm_chat.py

🔴 **Line 59:** Empty except with pass (silent failure)

### src\providers\kimi_chat.py

🔴 **Line 118:** Empty except with pass (silent failure)

### src\providers\openai_compatible.py

🔴 **Line 160:** Empty except with pass (silent failure)

🔴 **Line 505:** Empty except with pass (silent failure)

🔴 **Line 523:** Empty except with pass (silent failure)

🔴 **Line 568:** Empty except with pass (silent failure)

🔴 **Line 588:** Empty except with pass (silent failure)

🔴 **Line 648:** Empty except with pass (silent failure)

🔴 **Line 654:** Empty except with pass (silent failure)

🔴 **Line 661:** Empty except with pass (silent failure)

🔴 **Line 903:** Empty except with pass (silent failure)

## High Complexity (8 findings)

### src\daemon\ws_server.py

🟡 **Line 303:** No message
   - Complexity: 14

### src\providers\glm_chat.py

🟠 **Line 67:** No message
   - Complexity: 81

### src\providers\kimi_chat.py

🟠 **Line 35:** No message
   - Complexity: 51

### src\providers\openai_compatible.py

🟡 **Line 199:** No message
   - Complexity: 13

🟡 **Line 335:** No message
   - Complexity: 11

🟠 **Line 427:** No message
   - Complexity: 91

🟠 **Line 561:** No message
   - Complexity: 52

🟡 **Line 848:** No message
   - Complexity: 12

## Unused Definitions (24 findings)

### src\daemon\ws_server.py

🔵 **Line 0:** No message

### src\providers\glm_chat.py

🔵 **Line 0:** No message

### src\providers\kimi_chat.py

🔵 **Line 0:** No message

### src\providers\openai_compatible.py

🔵 **Line 0:** No message

🔵 **Line 0:** No message

🔵 **Line 0:** No message

🔵 **Line 0:** No message

🔵 **Line 0:** No message

🔵 **Line 0:** No message

🔵 **Line 0:** No message

🔵 **Line 0:** No message

🔵 **Line 0:** No message

🔵 **Line 0:** No message

🔵 **Line 0:** No message

🔵 **Line 0:** No message

🔵 **Line 0:** No message

🔵 **Line 0:** No message

🔵 **Line 0:** No message

🔵 **Line 0:** No message

🔵 **Line 0:** No message

🔵 **Line 0:** No message

🔵 **Line 0:** No message

🔵 **Line 0:** No message

🔵 **Line 0:** No message
