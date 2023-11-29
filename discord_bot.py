import discord
from discord import app_commands
from discord.ext import commands
import asyncio
from main import SearchPrice, format_currency
from secret import bot_token

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="/", intents=intents)
bot_command = bot.tree.command()

shopping_lists = {}  # Dictionary to store shopping lists for each user
shopping_list_message = None
shopping_list_messages = {}  # Dictionary to store shopping lists for each user
shopping_list = {}


@bot.event
async def on_ready():
    print(f"Logged in as {bot.user.name}")
    try:
        synced = await bot.tree.sync()
        print(synced)
        print(f"Synced {len(synced)} command(s)!")
    except Exception as e:
        print(e)


@bot.command("add")
async def add(ctx, multiplier: int = 1, *args):
    global shopping_list
    embed = discord.Embed(title=f"{ctx.author.name}'s Shopping List", description="Here's your Shopping List!")
    user_id = ctx.author.id
    shopping_list = shopping_lists.setdefault(user_id, {})  # Get the shopping list for the user or create a new one
    item_name = " ".join(args)
    # Search for pricing in the database
    price = SearchPrice(item_name)

    if price is None:
        no_price_message = await ctx.send(f"No pricing found for {item_name}")
        await ctx.message.delete()
        await asyncio.sleep(1)
        await no_price_message.delete()
        return

    try:
        multiplier = int(multiplier)
    except ValueError:
        print("Expected Multiplier, default Throwback!")
        multiplier = 1

    # Check if the item is already in the shopping list
    if item_name in shopping_list:
        # Update the quantity by multiplying with the multiplier
        shopping_list[item_name]["quantity"] += int(multiplier)
    else:
        # Add the item to the shopping list with the specified quantity
        shopping_list[item_name] = {
            "quantity": multiplier,
            "price": price
        }

    # Format the shopping list message for the user
    # message = ""
    total_price = 0

    for item_name, item_data in shopping_list.items():
        quantity = item_data["quantity"]
        item_price = item_data["price"]
        total_price += quantity * item_price
        total_item_price = format_currency(quantity * item_price)
        embed.add_field(name=f"{quantity}x {item_name}", value=f" Price: {total_item_price} \n Each: {format_currency(item_price)}", inline=False)
        # message += f"{quantity}x {item_name} = {total_item_price}\n"

    embed.add_field(name="Total Price:", value=format_currency(total_price), inline=False)
    # message += f"Total: {format_currency(total_price)}"

    # Check if the user already has a shopping list message
    if user_id in shopping_list_messages:
        # Edit the existing message with the updated shopping list
        shopping_list_message1 = shopping_list_messages[user_id]
        await shopping_list_message1.edit(content=None, embed=embed)
    else:
        # Send a new message with the shopping list
        shopping_list_message1 = await ctx.send(embed=embed)
        shopping_list_messages[user_id] = shopping_list_message1

    await ctx.message.delete()


@bot.command(name="reset")
async def reset(ctx):
    global shopping_list, shopping_list_message
    user_id = ctx.author.id
    shopping_list = shopping_lists.pop(user_id, None)  # Remove the shopping list for the user

    # Check if the user has a shopping list message
    if user_id in shopping_list_messages:
        # Delete the shopping list message
        shopping_list_message = shopping_list_messages.pop(user_id)

    reset_message = await ctx.send("Shopping List resetted!")
    await ctx.message.delete()

    await asyncio.sleep(1)
    await reset_message.delete()


@bot.command(name="reload")
async def reload(ctx):
    global shopping_list, shopping_list_message  # Declare the variables as global
    reload_message = await ctx.send("Database reloaded!")
    await ctx.message.delete()

    await asyncio.sleep(1)
    await reload_message.delete()

    # Update the shopping list with the latest pricing information
    updated_shopping_list = {}
    total_price = 0

    for item_name, item_data in shopping_list.items():
        quantity = item_data["quantity"]
        price = SearchPrice(item_name)
        if price is None:
            await ctx.send(f"No pricing found for {item_name}. Removing from shopping list.")
            continue

        updated_shopping_list[item_name] = {
            "quantity": quantity,
            "price": price
        }
        total_price += quantity * price

    shopping_list = updated_shopping_list

    # Format the updated shopping list message
    message = ""
    for item_name, item_data in shopping_list.items():
        quantity = item_data["quantity"]
        item_price = item_data["price"]
        total_item_price = format_currency(quantity * item_price)
        message += f"{quantity}x {item_name} = {total_item_price}\n"

    message += f"Total: {format_currency(total_price)}"

    # If the shopping list message exists, edit its content
    if shopping_list_message:
        await shopping_list_message.edit(content=f"Shopping List:\n{message}")
    else:
        # If the shopping list message doesn't exist, send a new message
        shopping_list_message = await ctx.send(f"Shopping List:\n{message}")


@bot.tree.command(name="ping", description="Checks the latency of the Bot!")
@app_commands.describe()
async def pong(interaction: discord.Interaction):
    await interaction.response.send_message(f"This took {round(bot.latency * 1000)}ms!", ephemeral=True)


bot.run(bot_token)
