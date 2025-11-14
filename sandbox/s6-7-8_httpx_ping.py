# Basic httpx usage: GET + JSON parsing + 4xx/5xx handling + timeout handling

import httpx


def ping_coingecko() -> None:
    """Demonstration of the 3 httpx skills:
    6) GET + JSON
    7) Handling 4xx/5xx errors safely
    8) Handling timeouts explicitly
    """

    # 1) CoinGecko ping endpoint (this should always return a small, fast JSON)
    url = 'https://api.coingecko.com/api/v3/ping'

    try:
        # 2) Make the GET request
        #    The timeout=5.0 means: if the server does not respond within 5 seconds,
        #    httpx will raise a TimeoutException.
        response = httpx.get(url, timeout=5.0)

    # --- SKILL 8: Timeout handling -----------------------------------------
    except httpx.TimeoutException:
        # This block executes ONLY when the request takes longer than timeout=5.0
        print('[ERROR] Request to CoinGecko timed out.')
        return

    # --- SKILL 7: Network/connection errors --------------------------------
    except httpx.RequestError as exc:
        # This captures ANY network-level issue:
        # - DNS errors
        # - connection refused
        # - no internet
        # - SSL issues
        # Note: TimeoutException is a subclass of RequestError, which is why we
        #       catch TimeoutException first (to handle it separately).
        print(f'[ERROR] Problem connecting with {exc.request.url!r}')
        return

    # --- If we reach this point, the server responded ------------------------
    print('Status code:', response.status_code)

    # --- SKILL 6: Correct handling of a 200 OK response ---------------------
    if response.status_code == 200:
        print('Ping successful!')

        try:
            # Attempt to parse the response as JSON.
            # Even with a 200 status, the response might not be valid JSON,
            # so we wrap it in a try/except.
            data = response.json()
            print('Response data:', data)

        except ValueError:
            # This triggers if .json() fails because the response is not valid JSON.
            print('[ERROR] Failed to parse JSON response.')
            print('Raw response text (first 200 chars):')
            print(response.text[:200])
            return

    # --- SKILL 7: Handling non-200 responses (4xx and 5xx) ------------------
    else:
        # For any status code that is not 200, we DO NOT attempt .json(),
        # because error responses often return HTML or plain text.
        print('[WARNING] Ping failed with status code:', response.status_code)
        print('Response text (first 200 chars):')
        print(response.text[:200])


# Execute the function only when running this script directly
if __name__ == '__main__':
    ping_coingecko()


"""
Expected healthy output:

Status code: 200
Ping successful!
Response data: {'gecko_says': '(V3) To the Moon!'}

"""
