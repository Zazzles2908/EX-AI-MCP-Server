"""Test model_config.py implementation"""

from src.providers.model_config import (
    get_model_token_limits,
    validate_max_tokens,
    get_default_max_tokens,
    get_max_output_tokens
)

print("=" * 80)
print("MODEL TOKEN LIMITS TEST")
print("=" * 80)

models = [
    'moonshot-v1-8k',
    'moonshot-v1-32k',
    'moonshot-v1-128k',
    'kimi-k2-0905-preview',
    'kimi-k2-0711-preview',
    'kimi-k2-turbo-preview',
    'kimi-thinking-preview',
    'glm-4.6',
    'glm-4.5',
    'glm-4.5-flash',
    'glm-4.5-air',
    'glm-4.5-airx',
    'glm-4.5v'
]

for model in models:
    limits = get_model_token_limits(model)
    print(f"\n{model}:")
    print(f"  Max Context: {limits['max_context_tokens']:,} tokens")
    print(f"  Max Output: {limits['max_output_tokens']:,} tokens")
    print(f"  Default Output: {limits['default_output_tokens']:,} tokens")
    print(f"  Provider: {limits['provider']}")

print("\n" + "=" * 80)
print("VALIDATION TESTS")
print("=" * 80)

test_cases = [
    ('moonshot-v1-8k', 10000, "Should cap at 7168"),
    ('moonshot-v1-8k', 4096, "Should accept as-is"),
    ('moonshot-v1-128k', 50000, "Should accept as-is"),
    ('moonshot-v1-128k', 200000, "Should cap at 114688"),
    ('kimi-k2-0905-preview', 250000, "Should cap at 229376 (256K model)"),
    ('kimi-k2-0905-preview', 16384, "Should accept as-is"),
    ('kimi-thinking-preview', 120000, "Should cap at 114688 (128K model)"),
    ('glm-4.6', 190000, "Should cap at 180224 (200K model)"),
    ('glm-4.6', -100, "Should reject negative"),
    ('glm-4.5-flash', None, "Should use default 8192"),
    ('glm-4.5v', None, "Should use default 8192 (vision model)"),
]

for model, requested, description in test_cases:
    validated = validate_max_tokens(model, requested, enforce_limits=True)
    print(f"\n{model}:")
    print(f"  Requested: {requested}")
    print(f"  Validated: {validated}")
    print(f"  Test: {description}")

print("\n" + "=" * 80)
print("HELPER FUNCTIONS TEST")
print("=" * 80)

for model in ['moonshot-v1-8k', 'glm-4.6']:
    default = get_default_max_tokens(model)
    max_out = get_max_output_tokens(model)
    print(f"\n{model}:")
    print(f"  Default: {default:,}")
    print(f"  Max Output: {max_out:,}")

print("\n" + "=" * 80)
print("✅ ALL TESTS COMPLETE")
print("=" * 80)

