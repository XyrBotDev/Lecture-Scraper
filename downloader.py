import asyncio
import os
import yt_dlp
from playwright.async_api import async_playwright

async def main():
    target_url = os.environ.get("TARGET_URL")
    print(f"[*] Targeting URL: {target_url}")

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()
        page = await context.new_page()

        stream_url = None

        def handle_request(request):
            nonlocal stream_url
            if ".m3u8" in request.url or "manifest" in request.url:
                if not stream_url:
                    stream_url = request.url
                    print(f"\n[+] Captured Stream URL: {stream_url}\n")

        page.on("request", handle_request)
        
        try:
            await page.goto(target_url, timeout=60000)
            # Thoda wait karo taaki player initialize ho aur stream request fire ho
            await asyncio.sleep(10)
        except Exception as e:
            print(f"[-] Error loading page: {e}")

        await browser.close()

    if stream_url:
        print("[*] Downloading video via yt-dlp...")
        ydl_opts = {
            'outtmpl': 'downloaded_lecture.mp4',
            'format': 'best',
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([stream_url])
        print("[+] Download Finished Successfully!")
    else:
        print("[-] Stream URL not found.")

if __name__ == "__main__":
    asyncio.run(main())
  
