try:
    __import__('tools.providers.kimi.kimi_tools_chat')
    print('SUCCESS: Kimi tools chat imported')
except Exception as e:
    print(f'FAIL: Kimi tools chat - {e}')

try:
    __import__('tools.providers.glm.glm_web_search')
    print('SUCCESS: GLM web search imported')
except Exception as e:
    print(f'FAIL: GLM web search - {e}')

try:
    __import__('tools.providers.kimi.kimi_files')
    print('SUCCESS: Kimi files imported')
except Exception as e:
    print(f'FAIL: Kimi files - {e}')