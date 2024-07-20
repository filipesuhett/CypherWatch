import aiohttp
import discord
from discord.ext import commands
import asyncio

async def get_mmr_by_match_id(match_id, puuid, region, api_key):
    url = f"https://api.henrikdev.xyz/valorant/v1/by-puuid/mmr-history/{region}/{puuid}"
    params = {'api_key': api_key}
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params, timeout=10) as response:
                if response.status == 200:
                    data = await response.json()
                    for record in data["data"]:
                        if record["match_id"] == match_id:
                            return record
                else:
                    print(f'Error fetching MMR data: {response.status}')
    except asyncio.TimeoutError:
        print('Request timed out')
    return None

async def embed_matches(match_data_list, ctx):
    # Create an embed with a title and color
    embed = discord.Embed(
        title="**Resume Last 5 Matches**",
        color=0x1abc9c  # A nice teal color
    )

    # Add details for each match
    for i, match_data in enumerate(match_data_list):
        if i > 0:
            embed.add_field(name="\u200b", value="---", inline=False)  # Adds a horizontal line for separation

        embed.add_field(
            name=f"**Match Details: {match_data['map_name']}**",
            value=(
                f"**🕹️ Mode:** {match_data['mode']}\n\n"
                f"**🎯 Performance:**\n"
                f"**Kills:** {match_data['kills']}\n"
                f"**Assists:** {match_data['assists']}\n"
                f"**Deaths:** {match_data['deaths']}\n\n"
                f"**📈 Rank Change:**\n"
                f"**Tier:** {match_data['tier_patched']}\n"
                f"**MMR Change:** {match_data['mmr_change']}\n"
                f"**Ranking in Tier:** {match_data['ranking_in_tier']}"
            ),
            inline=False
        )

    # Add a footer for additional context or branding
    embed.set_footer(text="Cypher Watch | Data from Valorant API")

    # Send the embed based on the context type
    if isinstance(ctx, commands.Context):
        await ctx.send(embed=embed)
    elif isinstance(ctx, discord.Interaction):
        await ctx.response.send_message(embed=embed)
    elif isinstance(ctx, discord.commands.context.ApplicationContext):
        await ctx.respond(embed=embed)
    else:
        print("ctx is not a valid commands.Context, discord.Interaction, or ApplicationContext object")

async def find_player_data(puuid, region, api_key, ctx):
    url = f'https://api.henrikdev.xyz/valorant/v3/by-puuid/matches/{region}/{puuid}'
    params = {'api_key': api_key}
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params, timeout=10) as response:
                if response.status == 200:
                    response_data = await response.json()
                else:
                    print(f'Error fetching player data: {response.status}')
                    return
    except asyncio.TimeoutError:
        print('Request timed out')
        return
    
    match_data_list = []

    for match in response_data.get("data", []):
        metadata = match.get("metadata", {})
        map_name = metadata.get("map", "Unknown")
        match_id = metadata.get("matchid", "Unknown")
        mode = metadata.get("mode", "Unknown")

        for player in match.get("players", {}).get("all_players", []):
            if player.get("puuid") == puuid:
                player_stats = player.get("stats", {})
                kills = player_stats.get("kills", 0)
                assists = player_stats.get("assists", 0)
                deaths = player_stats.get("deaths", 0)
                
                mmr_data = await get_mmr_by_match_id(match_id, puuid, region, api_key)
                
                if mmr_data:
                    mmr_change = mmr_data.get("mmr_change_to_last_game", "N/A")
                    tier_patched = mmr_data.get("currenttierpatched", "N/A")
                    ranking_in_tier = mmr_data.get("ranking_in_tier", "N/A")
                    
                    if isinstance(mmr_change, (int, float)):
                        mmr_change = f"+{mmr_change}" if mmr_change > 0 else str(mmr_change)
                else:
                    mmr_change = "N/A"
                    tier_patched = "N/A"
                    ranking_in_tier = "N/A"
                
                match_data = {
                    "map_name": map_name,
                    "match_id": match_id,
                    "mode": mode,
                    "kills": kills,
                    "assists": assists,
                    "deaths": deaths,
                    "tier_patched": tier_patched,
                    "ranking_in_tier": ranking_in_tier,
                    "mmr_change": mmr_change
                }

                match_data_list.append(match_data)

    if match_data_list:
        await embed_matches(match_data_list, ctx)
    else:
        await ctx.send("No match data found.")
