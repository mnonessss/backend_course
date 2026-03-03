import argparse
import asyncio
import sys
from urllib.parse import urlparse

import aiohttp


def main():

    parser = argparse.ArgumentParser(description="Parser for hedgedcurl")

    parser.add_argument("urls", nargs="+", help="Список url")

    def positive_int(value):
        try:
            ivalue = int(value)
        except ValueError:
            raise argparse.ArgumentTypeError("Timeout must be integer")
        if ivalue <= 0:
            raise argparse.ArgumentTypeError("Timeout must be > 0")
        return ivalue

    parser.add_argument(
        "--timeout",
        "-t",
        type=positive_int,
        default=15,
        help="Timeout in seconds (must be greater than 0, default = 15 second)"
    )

    def is_valid_url(url):
        parsed = urlparse(url)
        if parsed.scheme not in ("http", "https"):
            return False
        if not parsed.netloc:
            return False
        return True

    args = parser.parse_args()
    valid_urls = []
    invalid_urls = []
    for url in args.urls:
        if is_valid_url(url):
            valid_urls.append(url)
        else:
            invalid_urls.append(url)

    if not valid_urls:
        print("Error: There isn't any valid URLS", file=sys.stderr)
        sys.exit(1)

    if invalid_urls:
        print("Warning: There is some invalid URLS:", file=sys.stderr)
        for url in invalid_urls:
            print(url, file=sys.stderr)

    exit_code = asyncio.run(async_main(valid_urls, args.timeout))
    sys.exit(exit_code)


async def fetch(url, session):
    async with session.get(url) as response:
        version = response.version
        status = response.status
        reason = response.reason
        headers = response.headers
        body = await response.text()
        return version, status, reason, headers, body


async def async_main(valid_urls, timeout):
    timeout_obj = aiohttp.ClientTimeout(total=timeout)
    timeout_happened = False
    async with aiohttp.ClientSession(timeout=timeout_obj) as session:
        tasks = [
            asyncio.create_task(fetch(url, session))
            for url in valid_urls
        ]
        for task in asyncio.as_completed(tasks):
            try:
                res = await task
                version, status, reason, headers, body = res
                s = f"HTTP/{version.major}.{version.minor} {status} {reason}"
                print(s)
                for key, val in headers.items():
                    print(f"{key}: {val}")
                print()
                print(body)
                for t in tasks:
                    if not t.done():
                        t.cancel()
                return 0
            except (
                asyncio.TimeoutError,
                aiohttp.ServerTimeoutError,
            ):
                timeout_happened = True
            except asyncio.CancelledError:
                raise
            except aiohttp.ClientError:
                pass
        if timeout_happened:
            return 228
        return 1


if __name__ == "__main__":
    main()
