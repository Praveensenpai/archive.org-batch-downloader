import asyncio
from selectolax.parser import HTMLParser
import aiohttp
import aiofiles
import os
from rich import print

DOWNLOAD_LOCATIONS = "Downloads"


async def downloader(path: str, url: str) -> None:
    if not os.path.exists(path):
        os.makedirs(path, exist_ok=True)
        print(f"Created directory {path}")
    print(f"Downloading {url}")
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            file = url.split("/")[-1].replace("%20", " ")
            file = f"{path}/{file}"
            async with aiofiles.open(file, mode="wb") as f:
                await f.write(await response.content.read())
                print(f"Downloaded {file}")


async def get_parser(url: str) -> HTMLParser:
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            html = await response.text()
    return HTMLParser(html)


async def archive_downloader(path: str, url: str) -> None:
    # Have some problem need to fix this later
    print(f"Requesting url={url}")
    try:
        parser = await get_parser(url)
        links = parser.css("tbody tr td a")[1:]
        tasks = []
        for link in links:
            link_href = link.attributes["href"]
            link_url = f"{url}/{link_href}"
            if link_href[-4] == ".":
                tasks.append(asyncio.create_task(downloader(path, link_url)))
            else:
                path = f"{DOWNLOAD_LOCATIONS}/{link.text()}"
                tasks.append(asyncio.create_task(archive_downloader(path, link_url)))
        await asyncio.gather(*tasks)
    except Exception as e:
        print(e)
        print(url)


async def archive_downloader_runner(url: str) -> None:
    url = url.strip().replace("/details/", "/download/")
    await archive_downloader(DOWNLOAD_LOCATIONS, url)


def archive_downlaoder_main_runner(url: str) -> None:
    asyncio.run(archive_downloader_runner(url))
