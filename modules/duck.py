from telethon import events
import aiohttp
from bs4 import BeautifulSoup
from .utils import restricted_to_owner

async def search_duckduckgo(query):
    url = f"https://html.duckduckgo.com/html/?q={query}"
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            if response.status == 200:
                soup = BeautifulSoup(await response.text(), 'html.parser')
                results = []
                for result in soup.find_all('div', class_='result__body'):
                    title = result.find('a', class_='result__a').text
                    link = result.find('a', class_='result__a')['href']
                    snippet = result.find('a', class_='result__snippet').text
                    results.append({
                        'title': title,
                        'link': link,
                        'snippet': snippet
                    })
                return results[:5]  # Mengembalikan 5 hasil teratas
            else:
                return None

def load(client):
    @client.on(events.NewMessage(pattern=r'\.ddg (.+)'))
    @restricted_to_owner
    async def duckduckgo_search(event):
        query = event.pattern_match.group(1)
        await event.edit(f"🔍 Mencari '{query}' di DuckDuckGo...")
        
        results = await search_duckduckgo(query)
        if results:
            response = f"🦆 Hasil pencarian DuckDuckGo untuk '{query}':\n\n"
            for i, result in enumerate(results, 1):
                response += f"{i}. **{result['title']}**\n"
                response += f"   {result['snippet']}\n"
                response += f"   🔗 {result['link']}\n\n"
            await event.edit(response)
        else:
            await event.edit("❌ Maaf, tidak dapat menemukan hasil atau terjadi kesalahan saat pencarian.")

def add_commands(add_command):
    add_command('.ddg <query>', '🦆 Melakukan pencarian di DuckDuckGo')