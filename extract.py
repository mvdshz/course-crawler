#!/usr/bin/env python3
"""
Skilljar -> NotebookLM extractor (merged version)

Flow:
1) Open browser with persistent profile
2) Prompt user to log in manually
3) Prompt user to paste the starting lesson URL
4) Discover all lesson links from the sidebar
5) Extract text / images / audio from each lesson

Setup:
    pip install playwright
    playwright install firefox
    # yt-dlp must also be installed and available in PATH

Run:
    python extract.py
"""

import asyncio
import os
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from urllib.parse import urlparse

from playwright.async_api import async_playwright

# ── Config ───────────────────────────────────────────────
BASE_OUTPUT_DIR = Path(f"course_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
TEXT_DIR = BASE_OUTPUT_DIR / "course_text"
AUDIO_DIR = BASE_OUTPUT_DIR / "course_audio"
PROFILE_DIR = Path("browser_profile")

STREAM_WAIT = 20
# ─────────────────────────────────────────────────────────

def is_stream_url(url: str) -> bool:
    u = url.lower()
    return (
        ".m3u8" in u
        or "jwplayer.com" in u
        or "jwplatform.com" in u
        or "content.jwplatform" in u
        or ("cdn.jwplayer" in u and (".mp4" in u or ".ts" in u))
    )

def normalize_url_to_path(url: str) -> str:
    """Return only the path part, e.g. https://x.com/a/b -> /a/b."""
    return urlparse(url).path

async def wait_for_manual_login(page):
    print("\n🔐 Log in in the opened browser window.")
    print("   When you are fully logged in and can see the course page, press Enter here.")
    input("   Press Enter to continue... ")

    # small extra wait so the session cookies / DOM settle
    await page.wait_for_timeout(1000)

async def discover_lessons(page, first_lesson_url: str) -> list[str]:
    print("🔍 Scanning sidebar for lessons...")
    await page.goto(first_lesson_url, wait_until="domcontentloaded", timeout=40000)

    # Wait for sidebar links to appear
    try:
        await page.wait_for_selector(
            'a.lesson, .lessons-wrapper a, [class*="curriculum"] a',
            timeout=10000
        )
    except Exception:
        pass

    await asyncio.sleep(1)

    links = await page.evaluate("""(pageUrl) => {
        const base = new URL(pageUrl);
        const seen = new Set();
        const results = [];

        const selectors = [
            'a.lesson[href]',
            '.lessons-wrapper a[href]',
            '[id*="curriculum"] a[href]',
            '[class*="curriculum"] a[href]',
            'nav a[href]',
            'aside a[href]',
        ];

        let anchors = [];
        for (const sel of selectors) {
            const found = Array.from(document.querySelectorAll(sel));
            if (found.length > 0) {
                anchors = found;
                break;
            }
        }

        // For Skilljar-like URLs, course base path is usually /course-name
        const parts = base.pathname.split('/').filter(Boolean);
        const coursePath = parts.length >= 1 ? '/' + parts[0] : '';

        for (const a of anchors) {
            try {
                const url = new URL(a.href, base);

                // Keep same host, same course path, numeric lesson slug at end
                if (
                    url.hostname === base.hostname &&
                    url.pathname.startsWith(coursePath + '/') &&
                    /\\/\\d+$/.test(url.pathname) &&
                    !seen.has(url.href)
                ) {
                    seen.add(url.href);
                    results.push(url.href);
                }
            } catch (e) {}
        }

        return results;
    }""", first_lesson_url)

    return links

async def find_video_url(page) -> tuple[str | None, str]:
    yt_url = await page.evaluate("""() => {
        const selectors = [
            'iframe[src*="youtube.com/embed"]',
            'iframe[src*="youtube-nocookie.com/embed"]',
            'iframe[src*="youtu.be"]',
        ];
        for (const sel of selectors) {
            const el = document.querySelector(sel);
            if (el && el.src) return el.src;
        }
        return null;
    }""")
    if yt_url:
        return yt_url, "youtube"
    return None, "none"

async def extract_lesson(page, context, url: str, idx: int, total: int):
    print(f"\n[{idx:02d}/{total}] {url}")
    stream_url = None

    def on_request(req):
        nonlocal stream_url
        if not stream_url and is_stream_url(req.url):
            stream_url = req.url

    page.on("request", on_request)

    try:
        await page.goto(url, wait_until="domcontentloaded", timeout=40000)
        await asyncio.sleep(2)

        # ── Text ─────────────────────────────────────────
        text = await page.evaluate("""() => {
            const targets = [
                'article',
                'main',
                '[class*="lesson"]',
                '[class*="content"]',
                '[class*="module"]',
                'body'
            ];
            for (const sel of targets) {
                const el = document.querySelector(sel);
                if (el && el.innerText && el.innerText.trim().length > 200) {
                    return el.innerText.trim();
                }
            }
            return document.body.innerText.trim();
        }""")

        if text and len(text) > 100:
            txt_path = TEXT_DIR / f"lesson_{idx:02d}.txt"
            txt_path.write_text(f"Source: {url}\n\n{text}", encoding="utf-8")
            print(f"  ✓ text   → {txt_path}")

        # ── Video ────────────────────────────────────────
        video_url, source_type = await find_video_url(page)

        if source_type == "youtube":
            print("  ✓ YouTube embed detected")
        else:
            for selector in [".jw-display-icon-container", ".jw-icon-playback", ".jwplayer", "video"]:
                try:
                    await page.click(selector, timeout=2000)
                    break
                except Exception:
                    continue

            for _ in range(STREAM_WAIT * 2):
                if stream_url:
                    break
                await asyncio.sleep(0.5)

            if stream_url:
                video_url = stream_url
                print("  ✓ JW Player stream detected")

        # ── Audio download ───────────────────────────────
        if video_url:
            out_tmpl = str(AUDIO_DIR / f"lesson_{idx:02d}.%(ext)s")
            result = subprocess.run(
                [
                    sys.executable, "-m", "yt_dlp",
                    "-x", "--audio-format", "mp3", "--audio-quality", "0",
                    "--quiet", "--no-warnings", "-o", out_tmpl, video_url
                ],
                capture_output=True,
                text=True,
                timeout=600,
            )
            if result.returncode == 0:
                print(f"  ✓ audio  → {AUDIO_DIR}/lesson_{idx:02d}.mp3")
            else:
                print(f"  ✗ yt-dlp error: {result.stderr.strip()[:120]}")
        else:
            print("  ⚠ audio   no video found (text-only lesson?)")

    except Exception as e:
        print(f"  ✗ error: {e}")
    finally:
        try:
            page.remove_listener("request", on_request)
        except Exception:
            pass

    await asyncio.sleep(1)

async def main():
    for d in [TEXT_DIR, AUDIO_DIR, PROFILE_DIR]:
        d.mkdir(parents=True, exist_ok=True)

    print("🌐 Opening browser...\n")

    async with async_playwright() as p:
        context = await p.firefox.launch_persistent_context(
            PROFILE_DIR,
            headless=False,
            viewport={"width": 1280, "height": 800},
        )
        page = context.pages[0] if context.pages else await context.new_page()

        await wait_for_manual_login(page)

        first_url = input(
            "\nPaste the starting lesson URL here:\n"
            "Example: https://anthropic.skilljar.com/claude-101/383389\n> "
        ).strip()

        if not first_url:
            print("No URL provided. Exiting.")
            await context.close()
            return

        urls = await discover_lessons(page, first_url)

        if not urls:
            print("\n⚠ No lessons found. Make sure the URL looks like:")
            print("   https://anthropic.skilljar.com/{course-name}/{number}")
            await context.close()
            return

        print(f"\n📋 Found {len(urls)} lesson(s):")
        for i, u in enumerate(urls, 1):
            print(f"   {i:02d}. {u}")

        print("\nPress Enter to start extraction, or Ctrl+C to cancel...")
        input()

        for i, url in enumerate(urls, 1):
            await extract_lesson(page, context, url, i, len(urls))

        await context.close()

    print(f"\n{'─' * 55}")
    print("✅ Done!")
    print(f"   {TEXT_DIR}/   → text files")
    print(f"   {AUDIO_DIR}/  → mp3 files")

if __name__ == "__main__":
    asyncio.run(main())
