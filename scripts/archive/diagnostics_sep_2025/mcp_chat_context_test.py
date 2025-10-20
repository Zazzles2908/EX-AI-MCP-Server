import asyncio, json, os, uuid
from pathlib import Path
from mcp.client.stdio import stdio_client, StdioServerParameters
from mcp.client.session import ClientSession
from mcp.types import TextContent

ROOT = Path(__file__).resolve().parents[2]
WRAPPER = str(ROOT / 'scripts' / 'mcp_server_wrapper.py')
VENV_PY = str(ROOT / '.venv' / 'Scripts' / 'python.exe')
EVID_DIR = ROOT / 'docs' / 'augmentcode_phase2' / 'raw'
EVID_DIR.mkdir(parents=True, exist_ok=True)

async def main():
    env = {**os.environ, 'PYTHONPATH': str(ROOT), 'LOG_LEVEL': os.getenv('LOG_LEVEL', 'ERROR')}
    cont_id = f"ctx-{uuid.uuid4().hex[:8]}"
    rel_path = 'README.md'
    abs_path = str((ROOT / 'README.md').resolve())

    params = StdioServerParameters(
        command=VENV_PY,
        args=['-u', WRAPPER],
        cwd=str(ROOT),
        env=env,
    )

    run = {}
    async with stdio_client(params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()

            # 1) Tool registry
            tools = await session.list_tools()
            run['tools'] = [t.name for t in tools.tools]

            # helper
            async def call(name, args):
                res = await session.call_tool(name, arguments=args)
                texts = [c.text for c in res.content if isinstance(c, TextContent)]
                return texts

            # 2) Chat continuation tests
            # 2a) Negative: user-supplied continuation_id without prior thread should be rejected
            t1 = await call('chat', {'prompt': 'TURN 1 (negative): using a fresh continuation_id should be rejected.', 'model': 'auto', 'continuation_id': cont_id})
            t2 = await call('chat', {'prompt': 'TURN 2 (negative): still rejected.', 'model': 'auto', 'continuation_id': cont_id})
            run['chat_turn_1_negative'] = t1
            run['chat_turn_2_negative'] = t2
            run['continuation_id_negative'] = cont_id

            # 2b) Positive: first call without continuation_id, then accept continuation_offer
            pos1 = await call('chat', {'prompt': 'TURN A: please remember this code: 42', 'model': 'auto'})
            offered = None
            try:
                import json as _json
                for tx in pos1:
                    try:
                        obj = _json.loads(tx)
                        offered = (obj.get('continuation_offer') or {}).get('continuation_id')
                        if offered:
                            break
                    except Exception:
                        continue
            except Exception:
                offered = None
            if offered:
                pos2 = await call('chat', {'prompt': 'TURN B: what code did I just tell you?', 'model': 'auto', 'continuation_id': offered})
            else:
                pos2 = ['no continuation_offer']
            run['chat_turn_1_positive'] = pos1
            run['chat_turn_2_positive'] = pos2
            run['continuation_id_positive'] = offered

            # 3) Path validation with Chat: relative vs absolute
            rel = await call('chat', {'prompt': 'No op; just validating file param handling.', 'model': 'auto', 'files': [rel_path]})
            abx = await call('chat', {'prompt': 'No op; just validating file param handling.', 'model': 'auto', 'files': [abs_path]})
            run['chat_files_relative'] = rel
            run['chat_files_absolute'] = abx

            # 4) Kimi upload: invalid relative path to force error
            try:
                up_err = await call('kimi_upload_and_extract', {'files': ['does_not_exist.md'], 'purpose': 'file-extract'})
            except Exception as e:
                up_err = [f'EXC::{type(e).__name__}: {e}']
            run['kimi_upload_invalid_rel'] = up_err

    out = {
        'timestamp': __import__('datetime').datetime.utcnow().isoformat() + 'Z',
        'results': run,
    }
    out_path = EVID_DIR / f'mcp_chat_context_{cont_id}.json'
    out_path.write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding='utf-8')
    print(str(out_path))

if __name__ == '__main__':
    asyncio.run(main())

