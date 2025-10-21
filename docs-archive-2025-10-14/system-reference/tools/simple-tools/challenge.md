# challenge_EXAI-WS

**Version:** 1.1  
**Last Updated:** 2025-10-03  
**Category:** Simple Tool (Critical Analysis)  
**Related:** [chat.md](chat.md), [thinkdeep.md](thinkdeep.md), [consensus.md](consensus.md)

---

## Purpose

Critical analysis and truth-seeking to prevent reflexive agreement

---

## Use Cases

- Preventing reflexive agreement when users challenge responses
- Critical evaluation of statements and assumptions
- Truth verification and fact-checking
- Assumption challenging and validation
- Reasoning validation and logical analysis

---

## Key Features

- **Automatic invocation** when user questions or disagrees
- **Critical thinking** instead of automatic agreement
- **Truth-seeking** through reasoned analysis
- **Assumption validation** and challenge
- **Logical reasoning** evaluation

---

## Key Parameters

- `prompt` (required): The user's message or statement to analyze critically

---

## Automatic Invocation

The tool is automatically triggered when the user:
- Questions or disagrees with previous statements ("But I don't think...")
- Challenges assumptions ("You're assuming...")
- Expresses confusion ("I'm confused why...")
- Believes an error was made ("That doesn't seem right...")
- Seeks justification ("Why did you...")
- Shows surprise at conclusions ("Wait, why...")

**Common patterns:**
- "But..."
- "Why did you..."
- "I thought..."
- "Shouldn't we..."
- "That seems wrong..."
- "Are you sure..."
- "I'm confused..."

---

## Manual Invocation

Users can explicitly request critical analysis by using the word "challenge" in their message.

---

## Usage Examples

### User Disagreement
```
User: "But I don't think that approach will work because of the performance implications"
```
→ Tool automatically invokes challenge to critically analyze the disagreement

### Questioning Assumptions
```
User: "You're assuming the database can handle that load, but have you considered peak traffic?"
```
→ Tool critically evaluates the assumption

### Seeking Justification
```
User: "Why did you recommend PostgreSQL over MongoDB for this use case?"
```
→ Tool provides reasoned justification instead of reflexive agreement

---

## Best Practices

- **Think critically** - Don't automatically agree when challenged
- **Provide reasoning** - Explain your analysis clearly
- **Acknowledge errors** - If wrong, admit it and correct course
- **Defend when right** - If correct, explain why with evidence
- **Seek truth** - Truth and correctness matter more than agreement

---

## When to Use

- **Automatic:** When user questions, disagrees, or challenges previous statements
- **Manual:** When user explicitly requests critical analysis with "challenge"
- **Use `challenge` for:** Critical evaluation and truth-seeking
- **Use `chat` for:** Collaborative discussions without critical analysis
- **Use `thinkdeep` for:** Deep reasoning without challenging assumptions
- **Use `consensus` for:** Multiple perspectives on decisions

---

## Related Tools

- [chat.md](chat.md) - Collaborative thinking partner
- [thinkdeep.md](thinkdeep.md) - Extended reasoning
- [consensus.md](consensus.md) - Multi-model consensus

