import re
import datetime
from lupa import LuaRuntime
from Filedir import file_directory


# ----------------------------------------------------------------------------------------------------------------------

def format_currency(price):
    gold = price // 10000
    silver = (price % 10000) // 100
    copper = price % 100

    return f"{gold}g {silver}s {copper}c"


def GetData():
    global item_pricings_list
    with open(file_directory, "r") as file:
        lua_code = file.read()

    # Define the pattern for extracting item pricings
    pattern = r"\[\"(.+?)\"\]\s*=\s*(\d+)"

    # Find all matches of the pattern in the Lua code
    matches = re.findall(pattern, lua_code)

    # Filter out the unwanted entries
    trash_data = ["_5000000 = 10000", "_50000 = 500", "_200000 = 1000", "_1000000 = 2500", "_10000 = 200", "_500 = 5",
                  "STARTING_DISCOUNT = 5", "_2000 = 100", "isRecents = 1", "__dbversion = 2", "firstSeen = 1685732428",
                  "stacksize = 1", "numstacks = 0"]

    # Create a list of item pricings as tuples, excluding the trash entries
    item_pricings_list = [(item_name, int(price)) for item_name, price in matches if
                          f"{item_name} = {price}" not in trash_data]

    return item_pricings_list


# Print the item pricings
def SearchPrice(searched_name):
    item_pricings_list = GetData()
    for item_name, price in item_pricings_list:
        if item_name.lower() == str(searched_name).lower():
            # formatted_price = format_currency(price)
            # print(f"Pricing for {searched_name}: {price}")
            return price
    else:
        print(f"No pricing found for {searched_name}")


# Getting Date of last Scan
def getlastupdate():
    # Getting Timestamp from File
    with open(file_directory, "r") as lua_file:
        lua_code = lua_file.read()

    lua = LuaRuntime(unpack_returned_tuples=True)
    lua.execute(lua_code)

    timestamp = lua.globals().AUCTIONATOR_LAST_SCAN_TIME

    # Formatting Timestamp to readable Format
    unformatted_time = datetime.datetime.fromtimestamp(timestamp)
    formatted_time = unformatted_time.strftime("%d.%m.%y %H:%M")
    return formatted_time

# ----------------------------------------------------------------------------------------------------------------------
