import asyncio
import edge_tts

async def main():
    voices = await edge_tts.list_voices()
    targets = ["ur-", "pa-", "ps-", "hi-", "bn-", "en-pk", "en-in"]
    print("\nAvailable voices in Microsoft Edge TTS:")
    for v in voices:
        short = v["ShortName"]
        for t in targets:
            if short.lower().startswith(t):
                print(f"  - {short} ({v['Gender']}, {v['Locale']})")

if __name__ == "__main__":
    asyncio.run(main())

