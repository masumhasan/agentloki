import asyncio
import logging
import os
from dotenv import load_dotenv

load_dotenv()

# Enable verbose logging for httpx and mem0
logging.basicConfig(level=logging.DEBUG)
logging.getLogger('httpx').setLevel(logging.DEBUG)
logging.getLogger('mem0').setLevel(logging.DEBUG)

from mem0 import AsyncMemoryClient

async def main():
    client = AsyncMemoryClient()
    user_id = os.environ.get('DEBUG_USER_ID', 'Masum')
    print(f"Calling mem0.get_all(user_id={user_id!r})")
    try:
        results = await client.get_all(user_id=user_id)
        print("SUCCESS - results:")
        print(results)
    except Exception as e:
        print("EXCEPTION while calling mem0.get_all:")
        print(repr(e))
        # httpx.HTTPStatusError often exposes a `.response` attribute
        resp = getattr(e, 'response', None)
        if resp is not None:
            try:
                print("HTTP status:", resp.status_code)
                # resp.text is safe for httpx.Response
                print("HTTP body:", resp.text)
            except Exception as read_err:
                print("Failed to read response body:", read_err)
        else:
            print("No response attribute on exception; check network/config")

if __name__ == '__main__':
    asyncio.run(main())
