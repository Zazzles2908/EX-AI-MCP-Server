try:
    __import__('tools.smart_file_query')
    print('SUCCESS: smart_file_query fixed')
except Exception as e:
    print(f'FAIL: {e}')
    import traceback
    traceback.print_exc()