import discord
from discord import app_commands
from discord.ext import tasks, commands
from discord.ui import view

import random
import datetime
import json
import math


organizationFile = "./data/Orgs.json"
FactionFile = "./data/Factions.json"
priceFile = "./data/Prices.json"
ExistingUserFile = "./data/ExistingUsers.json"
intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)
tree = app_commands.CommandTree(client)
opRoles = [687105162569187430, 761621207270948874, 1047119025332813925]
DeltaBotChannel = 1046913052089524336 #This is the Bot-Testing guild, general chat

@client.event
async def on_ready():
    print(f'We have logged in as {client.user}')
    await tree.sync()
    print("Ready!")


      
def fileFromGroupType(type:str):
    type = type.lower()
    if type[-1] == "s":
        type = type[0:-1]
    if type == "faction":
        with open(FactionFile, "r") as f:
            groups = json.load(f)
    elif type == "organization":
        with open(organizationFile, "r") as f:
            groups = json.load(f)
    else:
        return None
    return groups

def groupToFile(groups, type:str):
    type = type.lower()
    if type == "faction":
        with open(FactionFile, "w") as f:
            json.dump(groups, f, indent=4)
    elif type == "organization":
        with open(organizationFile, "w") as f:
            json.dump(groups, f, indent=4)
    return groups

def getGroupNames():
    facs = fileFromGroupType("Faction")
    orgs = fileFromGroupType("Organization")
    
    groupNames = []
    
    for fac in facs:
        if facs[fac] != "Available":
            groupNames.append(facs[fac]["name"].lower())
        
    for org in orgs:
        if orgs[org] != "Available":
            groupNames.append(orgs[org]["name"].lower())
        
    return groupNames

def idAndTypeFromName(name:str) -> tuple[(int, str)]|str:
    facs = fileFromGroupType("Faction")
    orgs = fileFromGroupType("Organization")
    
    name = name.lower()
    
    for fac in facs:
        if facs[fac] != "Available" and name == facs[fac]["name"].lower():
            return (fac, "faction")
        
    for org in orgs:
        if orgs[org] != "Available" and name == orgs[org]["name"].lower():
            return (org, "organization")

    return "Not Found"

#assume a person can only lead a single group
def groupFromLeaderID(uid:int) -> tuple[(int, str)]|str:
    
    facs = fileFromGroupType("Faction")
    orgs = fileFromGroupType("Organization")
    
    for fac in facs:
        if facs[fac] != "Available" and uid == facs[fac]["leader"]:
            return (fac, "faction")
        
    for org in orgs:
        if orgs[org] != "Available" and uid == orgs[org]["leader"]:
            return (org, "organization")
    
    
    return "Not found"




def periodCalc():
    facs = fileFromGroupType("Faction")
    orgs = fileFromGroupType("Organization")
    
    for org in orgs:
        if orgs[org] != "Available":
            netIncome = orgs[org]["totalIncome"] - orgs[org]["totalUpkeep"]
            orgs[org]["gold"] = orgs[org]["gold"] + netIncome
        
    for fac in facs:
        if facs[fac] != "Available":
            netIncome = facs[fac]["totalIncome"] - facs[fac]["totalUpkeep"]
            facs[fac]["gold"] = facs[fac]["gold"] + netIncome
        
    groupToFile(facs, "Faction")
    groupToFile(orgs, "Organization")   
        
    return
        
async def riotCalc():
    facs = fileFromGroupType("Faction")
    orgs = fileFromGroupType("Organization")
    
    channel = client.get_channel(DeltaBotChannel)
        
    for org in orgs:
        if orgs[org] != "Available":
            riotChance = orgs[org]["riotChance"]
            dice = random.randint(0,100)
            if dice <= riotChance and orgs[org]["riot"] == False:
                orgs[org]["riot"] = True
                if channel != None:
                    await channel.send("<@"+orgs[org]["leader"]+">, a riot has broken out in your organization!")
            elif dice > riotChance and orgs[org]["riot"] == True:
                orgs[org]["riot"] = False
                if channel != None:
                    await channel.send("<@"+orgs[org]["leader"]+">, a riot has been quelled in your organization")
                    
    for fac in facs:
        if facs[fac] != "Available":
            riotChance = facs[fac]["riotChance"]
            dice = random.randint(0,100)
            if dice <= riotChance and facs[fac]["riot"] == False:
                facs[fac]["riot"] = True
                if channel != None:
                    await channel.send("<@"+facs[fac]["leader"]+">, a riot has broken out in your faction!")
            elif dice > riotChance and facs[fac]["riot"] == True:
                facs[fac]["riot"] = False
                if channel != None:
                    await channel.send("<@"+orgs[fac]["leader"]+">, a riot has been quelled in your faction")
        
    groupToFile(facs, "Faction")
    groupToFile(orgs, "Organization")    
    return

def incomeCalc():
    facs = fileFromGroupType("Faction")
    orgs = fileFromGroupType("Organization")

        
        
    for org in orgs:
        if orgs[org] != "Available":
            tempInc = 0
            tempInc += 50+50*(orgs[org]["upgrade base"])*(1.5*(orgs[org]["upgrade base"]))
            
            tempInc += 200*(orgs[org]["ABfront"])
            
            if (orgs[org]["bribes"]):
                dice = random.randint(0,100)
                if dice <= 80:
                    tempInc += 325*(orgs[org]["BMfront"])
            else:
                dice = random.randint(0,100)
                if dice <= 55:
                    tempInc += 325*(orgs[org]["BMfront"])
                    
            tempInc *= 1 + 0.5*(orgs[org]["money cut"])
            
            if (orgs[org]["production level up"]) > 0:
                tempInc *= 1.2*(orgs[org]["production level up"])
                
            if orgs[org]["riot"]:
                tempInc *= 0
            
            orgs[org]["totalIncome"] = tempInc

        
        
    for fac in facs:
        if facs[fac] != "Available":
            tempInc = 0
            tempInc += 200+200*(facs[fac]["capital"])*(2*(facs[fac]["capital"]))
            
            tempInc += 900*(facs[fac]["farms"])
                    
            tempInc *= 1 + 0.5*(facs[fac]["taxation"])
            
            if (facs[fac]["roads"])>0:
                tempInc *= 1.2*(facs[fac]["roads"])
                
            if facs[fac]["riot"]:
                tempInc *= 0
            
            facs[fac]["totalIncome"] = tempInc
        
    groupToFile(facs, "Faction")
    groupToFile(orgs, "Organization")    
    return

def intrigueIncome():
    facs = fileFromGroupType("Faction")
    orgs = fileFromGroupType("Organization")
    groupNames = getGroupNames()

    
    
    for fac in facs:
        tempInt = 0
        countedGroups = []
        spies = facs[fac]["spy"]
        for group in groupNames:
            id, group_type = idAndTypeFromName(group)
            hasEmbassy = False
            
            if group_type == "faction":
                hasEmbassy = facs[id]["embassy"]
            if group_type == "organization":
                hasEmbassy = orgs[id]["delegacy"]
            
            if spies.count(group) != 0:
                discChance = 0
                spiesForGroup = spies.count(group)
                
                #First, the chance of a gorup discovering the org is spying on them:
                if hasEmbassy:
                    discChance = 15
                discChance += 15+10*(spiesForGroup-1)
                #are the spies discovered?
                dice = random.randint(0,100)
                if dice >= discChance:
                    #spies aren't discovered, Intrigue income is added
                    tempInt += 1*spiesForGroup
                else:
                    #If the spies are discovered, should there be some kind of downside? Should the org lose the spy?
                    dice = random.randint(0,100)
                    if dice < 45:
                        facs[fac]["spy"].remove(group)
            
            if hasEmbassy:
                tempInt += 2
                
                
                
        print(countedGroups)
                
    for org in orgs:
        countedGroups = []
        spies = orgs[org]["spy"]
        for group in groupNames:
            id, group_type = idAndTypeFromName(group)
            hasEmbassy = False
            
            if group_type == "faction":
                hasEmbassy = facs[id]["embassy"]
            if group_type == "organization":
                hasEmbassy = orgs[id]["delegacy"]
            
            if spies.count(group) != 0:
                discChance = 0
                spiesForGroup = spies.count(group)
                
                #First, the chance of a gorup discovering the org is spying on them:
                if hasEmbassy:
                    discChance = 15
                discChance += 15+10*(spiesForGroup-1)
                #are the spies discovered?
                dice = random.randint(0,100)
                if dice >= discChance:
                    #spies aren't discovered, Intrigue income is added
                    tempInt += 1*spiesForGroup
                else:
                    #If the spies are discovered, should there be some kind of downside? Should the org lose the spy?
                    dice = random.randint(0,100)
                    if dice < 45:
                        orgs[org]["spy"].remove(group)
            
            if hasEmbassy:
                tempInt += 2
                        
    groupToFile(facs, "Faction")
    groupToFile(orgs, "Organization")
    return

def upkeepCalc():
    facs = fileFromGroupType("Faction")
    orgs = fileFromGroupType("Organization")
        
        
    for org in orgs:
        if orgs[org] != "Available":
            tempUpk = 0
            
            tempUpk += 100*(orgs[org]["ABfront"])
            
            if (orgs[org]["bribes"]):
                tempUpk += 250*(orgs[org]["BMfront"])
            else:
                tempUpk += 150*(orgs[org]["BMfront"])
            
            if (orgs[org]["production level up"]) > 0:
                tempUpk *= 0.9**(orgs[org]["production level up"])
                
            if (orgs[org]["spy"]):
                tempUpk += 500*len(orgs[org]["spy"])
                
            if orgs[org]["guard"]>0:
                tempUpk += 5*orgs[org]["guard"]
                
            if orgs[org]["ambusher"]>0:
                tempUpk += 10*orgs[org]["ambusher"]
                
            if orgs[org]["custom units"] != None:
                tempUpk += 5*getCustomUnitAmt(orgs[org]["name"])

            if orgs[org]["guardhouse"]>0:
                tempUpk += 1000*orgs[org]["guardhouse"]
                
            if orgs[org]["delegacy"]:
                tempUpk += 1500
                
            if orgs[org]["riot"]:
                tempUpk *= 5
            
            orgs[org]["totalUpkeep"] = tempUpk
        
        
    for fac in facs:
        if facs[fac] != "Available":
            tempUpk = 0
            
            tempUpk += 400*(facs[fac]["farms"])
            
            if (facs[fac]["roads"])>0:
                tempUpk = 300+300*(facs[fac]["roads"])*0.5*(facs[fac]["roads"])
                
            if (facs[fac]["spy"]):
                tempUpk += 500*len(facs[fac]["spy"])
            
            if facs[fac]["militia"]>0:
                tempUpk += 5 * facs[fac]["militia"]
            
            if facs[fac]["militia archer"]>0:
                tempUpk += 10*facs[fac]["militia archer"]
                
            if facs[fac]["custom troops"] != None:
                tempUpk += 5*getCustomUnitAmt(facs[fac]["name"])
            
            if facs[fac]["barracks"]>0:
                tempUpk += 1000*facs[fac]["barracks"]
                
            if facs[fac]["embassy"]:
                tempUpk += 1500
                
            if facs[fac]["riot"]:
                tempUpk *= 5
            
            facs[fac]["totalUpkeep"] = tempUpk
        
    groupToFile(facs, "Faction")
    groupToFile(orgs, "Organization")
    return

def getActiveSabotagePercent(name:str) -> int:
    tempPercent = 0
    
    if idAndTypeFromName(name) != None:
        _, grouptype = idAndTypeFromName(name)
    
    grouptype = grouptype.lower()
    
    
    facs = fileFromGroupType("Faction")
    orgs = fileFromGroupType("Organization")
    
    for fac in facs:
        for mission in facs[str(fac)]["sabotage"]:       
            if mission != None and mission != "Available":
                if facs[fac]["sabotage"][mission]["time left"] == 0:
                    facs[fac]["sabotage"][mission] = "Available"
                    
                if facs[fac]["sabotage"][mission]["time left"] > 0 and facs[fac]["sabotage"][mission]["target name"] == name:
                    tempPercent += facs[fac]["sabotage"][mission]["unrest%"]
                    facs[fac]["sabotage"][mission]["time left"] -= 1
    
    for org in orgs:
        for mission in orgs[org]["sabotage"]:
            if mission != None and mission != "Available":
                if orgs[org]["sabotage"][mission]["time left"] == 0:
                    orgs[org]["sabotage"][mission] = "Available"
                    
                if orgs[org]["sabotage"][mission]["time left"] > 0 and orgs[org]["sabotage"][mission]["target name"] == name:
                    tempPercent += orgs[org]["sabotage"][mission]["unrest%"]
                    orgs[org]["sabotage"][mission]["time left"] -= 1
    
    
    groupToFile(facs, "Faction")
    groupToFile(orgs, "Organization")

    return tempPercent

def riotChanceCalc():
    facs = fileFromGroupType("Faction")
    orgs = fileFromGroupType("Organization")
    
    for fac in facs:
        tempChance = 0
        match facs[fac]["money cut"]:
            case 0:
                break
            case 1:
                tempChance = 20
                break
            case 2:
                tempChance = 45
                break
            case 3:
                tempChance = 65
                break
        
        tempChance += getActiveSabotagePercent(facs[fac]["name"])
        facs[fac]["riotChance"] = tempChance
        
    for org in orgs:
        tempChance = 0
        match orgs[org]["taxation"]:
            case 0:
                break
            case 1:
                tempChance = 20
                break
            case 2:
                tempChance = 45
                break
            case 3:
                tempChance = 65
                break
        
        tempChance += getActiveSabotagePercent(int(org), "Organization")
        orgs[org]["riotChance"] = tempChance
        
    groupToFile(orgs, "Organization")
    groupToFile(facs, "Faction")

    return

def cleanGroups():
    facs = fileFromGroupType("Faction")
    orgs = fileFromGroupType("Organization")
    
    guild = client.get_channel(DeltaBotChannel).guild
    
    for fac in facs:
        for userIndex in range(len(facs[fac]["users"])):
            if guild.get_member(facs[fac]["users"][userIndex]) == None:
                facs[fac]["users"][userIndex] = None
            if all(isinstance(x, None) for x in facs[fac]["users"]):
                facs[fac]["users"] = []
            
        if guild.get_member(facs[fac]["leader"]) == None and facs[fac]["users"] == []:
            RemFac(int(fac))
            
    for org in orgs:
        for userIndex in range(len(orgs[org]["users"])):
            if guild.get_member(orgs[org]["users"][userIndex]) == None:
                orgs[org]["users"][userIndex] == None
            if all(isinstance(x, None) for x in orgs[org]["users"]):
                orgs[org]["users"] = []
                
        if guild.get_member(orgs[org]["leader"]) == None and orgs[org]["users"] == []:
            RemOrg(int(org)) 

    return

def getCustomUnitAmt(name:str) -> int:
    if idAndTypeFromName(name) == None:
        return 0
    id, group_type = idAndTypeFromName(name)
    
    groups = fileFromGroupType(group_type)
    
    tempCost = 0
    
    if group_type == "faction":
        for unit in groups[id]["custom troops"]:
            tempCost += 1
            tempCost += groups[id]["custom troops"][unit]["offense"]-1
            tempCost += groups[id]["custom troops"][unit]["defense"]-1
            tempCost += groups[id]["custom troops"][unit]["loyalty"]-1
            tempCost += groups[id]["custom troops"][unit]["speed"]-1
    else:
        for unit in groups[id]["custom units"]:
            tempCost += 1
            tempCost += groups[id]["custom units"][unit]["offense"]-1
            tempCost += groups[id]["custom units"][unit]["defense"]-1
            tempCost += groups[id]["custom units"][unit]["loyalty"]-1
            tempCost += groups[id]["custom units"][unit]["speed"]-1
    
    return tempCost

async def buyInfrastructure(name:str, ctx:discord.Interaction, item:str) -> bool:
    try:
        id, group_type = idAndTypeFromName(name)
    except:
        return False
        
    item = item.lower()
        
    groups = fileFromGroupType(group_type)
    
    with open(priceFile, "r") as f:
        prices = json.load(f)
    
    channel = client.get_channel(DeltaBotChannel)
    factionOnly = ["road", "capital", "farm"]
    organizationOnly = ["upgrade base", "front", "production level up"]
    
    if ctx.user.id != groups[id]["leader"]:
        await channel.send("You're not the leader of this group")
        return False
    
    if (group_type == "faction" and item in organizationOnly) or (group_type == "organization" and item in factionOnly):
        await channel.send(f"You can only buy {group_type}-specific items for {group_type}")
        return False
    
    match item:
        case "road":
            #first check if the group has too many already
            max = 2 + groups[id]["capital"]
            if groups[id]["roads"] < max:
                #Then calculate the cost and check if the group has enough gold to pay
                cost = (prices["Roads"] + prices["Roads"] * (groups[id]["roads"])) * (1.3 * (groups[id]["roads"]))
                if groups[id]["gold"] >= cost:
                    groups[id]["gold"] -= cost
                    groups[id]["roads"] += 1
                else: 
                    await channel.send("your group does not have enough gold")
                    return False
            else:
                await channel.send("you've reached the maximum number of roads for your current group level") 
                return False
            
        case "capital":
            #first check whether the max has been reached
            max = 5
            if groups[id]["capital"] < max:
                #then calculate cost of the upgrade and check if group has enough gold
                cost = prices["Capital"]*(2.5**groups[id]["capital"])
                if groups[id]["gold"] >= cost:
                    groups[id]["gold"] -= cost
                    groups[id]["capital"] += 1
                    groups[id]["base level"] += 1
                else:
                    await channel.send("your group does not have enough gold")
                    return False
            else: 
                await channel.send("your capital is already at max level")
                return False
        case "farm":
            #check if max has been reached
            max = 2 + groups[id]["capital"]
            if groups[id]["farms"] < max:
                #check if the group has enough gold
                cost = prices["Farms"]
                if groups[id]["gold"] >= cost:
                    groups[id]["gold"] -= cost
                    groups[id]["farms"] += 1
                else:
                    await channel.send("your group does not have enough gold")
                    return False
            else:
                await channel.send("your group has already built the current max of farms")
                return False
        case "upgrade base":
            #check if max has been reached
            max = 5
            if groups[id]["upgrade base"] < max:
                #check if the group has enough gold
                cost = prices["Upgrade Base"]*(2**groups[id]["upgrade base"])
                if groups[id]["gold"] >= cost:
                    groups[id]["gold"] -= cost
                    groups[id]["upgrade base"] += 1
                    groups[id]["base level"] += 1
                else:
                    await channel.send("your group does not have enough gold") 
                    return False
            else:
                await channel.send("your base is already at max level")
                return False
        case "front":
            #check if max has been reached
            max = 1 + groups[id]["upgrade base"]
            if groups[id]["ABfront"] + groups[id]["BMfront"] < max:
                #check if the group has enough gold
                cost = prices["Establish Front"]
                if groups[id]["gold"] >= cost:
                    await channel.send(ctx.user.mention + ", would you like to purchase a black market or above board front?\nBlack market: 'BM'\nAbove board: 'AB'")

                    # This will make sure that the response will only be registered if the following
                    # conditions are met:
                    
                    def check(msg):
                        return msg.author == ctx.user and msg.channel == channel and msg.content.upper() in ["BM", "AB"]

                    msg = await client.wait_for("message", check=check)
                    if msg.content.upper() == "AB":
                        groups[id]["gold"] -= cost
                        groups[id]["ABfront"] += 1
                        
                    elif msg.content.upper() == "BM":
                        groups[id]["gold"] -= cost
                        groups[id]["BMfront"] += 1
                else:
                    await channel.send("your group does not have enough gold")
                    return False
            else:
                await channel.send("your group already has the current maximum number of fronts")
                return False
        case "production level up":
            #check if the max has been reached
            max = 2 + math.floor(0.5*groups[id]["upgrade base"])
            if groups[id]["production level up"] < max:
                #check if there is enough gold
                cost = prices["Production Level Up"]
                if groups[id]["gold"] >= cost:
                    groups[id]["gold"] -= cost
                    groups[id]["production level up"] += 1
                else:
                    await channel.send("your group does not have enough gold")
                    return False
            else:
                await channel.send("your group alread has the current maximum of production upgrades")
                return False
            
    groupToFile(groups, group_type)
    
    return True

#Buy Intrigue needs working on, Espionage needs to be implemented
async def buyIntrigue(name:str, ctx:discord.Interaction, item:str) -> bool:
    try:
        id, group_type = idAndTypeFromName(name)
    except:
        return False
    
    groups = fileFromGroupType(group_type)
    
    with open(priceFile, "r") as f:
        prices = json.load(f)
        
    channel = client.get_channel(DeltaBotChannel)
    
    item = item.lower()
    
    groupNames = getGroupNames()
    
    match item:
        case "spy":
            #there isn't a max, so only price is checked.
            cost = prices["Hire Spy"]
            if groups[id]["gold"] >= cost:

                await channel.send(ctx.user.mention + ", where would you like to send the spy? Name any one group, or if you wish to use the spy to defend your group, write 'defense'")

                # This will make sure that the response will only be registered if the following
                # conditions are met:
                def check(msg):
                    return msg.author == ctx.user and msg.channel == channel and (msg.content.lower() in groupNames or msg.content.lower() == "defense")

                msg = await client.wait_for("message", check=check)
                if msg.content.lower() in groupNames or msg.content.lower() == "defense":
                    groups[id]["spy"].append(msg.content.lower())
                    groups[id]["gold"] -= cost   
                else:
                    await channel.send("That group doesn't exist, spy not bought")
                    return False

            else:
                await channel.send("Your group does not have enough money to hire a spy")
                return False
            
        case "sabotage":
            #There isn't a max, so only price is checked
            channel.send("The price of sabotages are *Variable* so they cannot be bought from the shop, contact a mod to discuss a sabotage and they will give you a price.\nIf this price is acceptable, the mod will remove the discussed amount of gold from the group before rolling to see if the mission was a success.\nIf the mission was a success they will add it to your group's list of successful sabotage missions")
            return False
            
        case "espionage":
            channel.send("Espionage has not yet been developed so it cannot be bought at the current moment, apologies.")
            return False
            
    groupToFile(groups, group_type)
    
    return True

async def buyMilitary(name:str, ctx:discord.Interaction, item:str) -> bool:
    
    try:
        id, group_type = idAndTypeFromName(name)
    except:
        return False
    
    groups = fileFromGroupType(group_type)
    
    with open(priceFile, "r") as f:
        prices = json.load(f)
    
    item = item.lower()
    
    channel = client.get_channel(DeltaBotChannel)
    factionOnly = ["militia", "archer", "custom troop", "barrack"]
    organizationOnly = ["guard", "ambusher", "custom unit", "guardhouse"]
    
    if group_type == "faction":
        totalUnits = groups[id]["militia"] + groups[id]["militia archer"] + getCustomUnitAmt(name)
    elif group_type == "organization":
        totalUnits = groups[id]["guard"] + groups[id]["ambusher"] + getCustomUnitAmt(name)
    
    if ctx.user.id != groups[id]["leader"]:
        await channel.send("You're not the leader of this group")
        return False
    
    if (group_type == "faction" and item in organizationOnly) or (group_type == "organization" and item in factionOnly):
        await channel.send(f"You can only buy {group_type}-specific items for {group_type}")
        return False
    
    match group_type:
        case "faction":
            match item:
                case "militia":
                    #First it's checked if the max is already reached
                    max = 250+250*groups[id]["capital"]+250*groups[id]["barracks"]
                    if totalUnits < max:
                        await channel.send(ctx.user.mention + ", How many units would you like to buy?")

                        # This will make sure that the response will only be registered if the following
                        # conditions are met:
                        
                        def check(msg):
                            return msg.author == ctx.user and msg.channel == channel and msg.content.isdigit()

                        msg = await client.wait_for("message", check=check)
                        if msg.content.isdigit():
                            #first check if the bought amount would bring the number over max
                            if totalUnits+int(msg.content) < max:
                                #Then cost can be calculated and checked
                                cost = prices["Militia"]*int(msg.content)
                                if groups[id]["gold"] >= cost:
                                    groups[id]["militia"] += int(msg.content)
                                    groups[id]["gold"] -= cost
                                else:
                                    await channel.send("Your group doesn't have enough gold!")
                                    return False
                            else:
                                await channel.send("This number of militia would bring your group over the maximum")
                                return False
                        else:
                            await channel.send("Please denote a positive number for the amount of milita you wish to buy")
                            return False
                    else:
                        await channel.send("Your group is already at the current max of milita")
                        return False
                case "archer":
                    #First it's checked if the max is already reached
                    max = 250+250*groups[id]["capital"]+250*groups[id]["barracks"]
                    if totalUnits < max:
                        await channel.send(ctx.user.mention + ", How many units would you like to buy?")

                        # This will make sure that the response will only be registered if the following
                        # conditions are met:
                        
                        def check(msg):
                            return msg.author == ctx.user and msg.channel == channel and msg.content.isdigit()

                        msg = await client.wait_for("message", check=check)
                        if msg.content.isdigit():
                            #first check if the bought amount would bring the number over max
                            if totalUnits+int(msg.content) < max:
                                #Then cost can be calculated and checked
                                cost = prices["Militia Archer"]*int(msg.content)
                                if groups[id]["gold"] >= cost:
                                    groups[id]["militia archer"] += int(msg.content)
                                    groups[id]["gold"] -= cost
                                else:
                                    await channel.send("Your group doesn't have enough gold!")
                                    return False
                            else:
                                await channel.send("This number of archer(s) would bring your group over the maximum")
                                return False
                        else:
                            await channel.send("Please denote a positive number for the amount of archer(s) you wish to buy")
                            return False
                    else:
                        await channel.send("Your group is already at the current max of archer(s)")
                        return False
                case "custom":
                    await channel.send("Custom units have variable cost in both gold and intrigue and thus cannot be bought in the shop.\n Please contact a mod, and they will help you in finding out which kind of custom fighter is right for you")
                    return False
                case "barrack":
                    #First see if the group has the max amount of barracks
                    max = 3
                    if groups[id]["barracks"] < max:
                        #then check the cost of the barracks
                        cost = prices["Barracks"]*(1.5**groups[id]["barracks"])
                        if groups[id]["gold"] >= cost:
                            groups[id]["barracks"] += 1
                            groups[id]["gold"] -= cost
                        else:
                            await channel.send("Your group doesn't have enough gold!")
                            return False
                    else:
                        await channel.send("Your group is already at the current max of barracks")
                        return False
                    
        case "organization":
            match item:
                case "guard":
                    #first it's checked if the max is reached
                    max = 100+100*groups[id]["upgrade base"]+50*groups[id]["guardhouse"]
                    if totalUnits < max:
                        await channel.send(ctx.user.mention + ", How many units would you like to buy?")

                        # This will make sure that the response will only be registered if the following
                        # conditions are met:
                        
                        def check(msg):
                            return msg.author == ctx.user and msg.channel == channel and msg.content.isdigit()

                        msg = await client.wait_for("message", check=check)
                        if msg.content.isdigit():
                            #first check if the bought amount would bring the number over max
                            if totalUnits+int(msg.content) < max:
                                #Then cost can be calculated and checked
                                cost = prices["Guard"]*int(msg.content)
                                if groups[id]["gold"] >= cost:
                                    groups[id]["guard"] += int(msg.content)
                                    groups[id]["gold"] -= cost
                                else:
                                    await channel.send("Your group doesn't have enough gold!")
                                    return False
                            else:
                                await channel.send("This number of guard(s) would bring your group over the maximum")
                                return False
                        else:
                            await channel.send("Please denote a positive number for the amount of guard(s) you wish to buy")
                            return False
                    else:
                        await channel.send("Your group is already at the current max of guard(s)")
                        return False
                case "ambusher":
                    #First it's checked if the max is already reached
                    max = 100+100*groups[id]["upgrade base"]+50*groups[id]["guardhouse"]
                    if totalUnits < max:
                        await channel.send(ctx.user.mention + ", How many units would you like to buy?")

                        # This will make sure that the response will only be registered if the following
                        # conditions are met:
                        
                        def check(msg):
                            return msg.author == ctx.user and msg.channel == channel and msg.content.isdigit()

                        msg = await client.wait_for("message", check=check)
                        if msg.content.isdigit():
                            #first check if the bought amount would bring the number over max
                            if totalUnits+int(msg.content) < max:
                                #Then cost can be calculated and checked
                                cost = prices["Ambusher"]*int(msg.content)
                                if groups[id]["gold"] >= cost:
                                    groups[id]["ambusher"] += int(msg.content)
                                    groups[id]["gold"] -= cost
                                else:
                                    await channel.send("Your group doesn't have enough gold!")
                                    return False
                            else:
                                await channel.send("This number of ambusher(s) would bring your group over the maximum")
                                return False
                        else:
                            await channel.send("Please denote a positive number for the amount of ambusher(s) you wish to buy")
                            return False
                    else:
                        await channel.send("Your group is already at the current max of ambusher(s)")
                        return False
                case "custom":
                    await channel.send("Custom units have variable cost in both gold and intrigue and thus cannot be bought in the shop.\n Please contact a mod, and they will help you in finding out which kind of custom fighter is right for you")
                    return False
                case "guardhouse":
                    #First see if the group has the max amount of barracks
                    max = 3
                    if groups[id]["guardhouse"] < max:
                        #then check the cost of the barracks
                        cost = prices["Guardhouse"]*(1.5**groups[id]["guardhouse"])
                        if groups[id]["gold"] >= cost:
                            groups[id]["guardhouse"] += 1
                            groups[id]["gold"] -= cost
                        else:
                            await channel.send("Your group doesn't have enough gold!")
                            return False
                    else:
                        await channel.send("Your group is already at the current max of guardhouses")
                        return False
    
    groupToFile(groups, group_type)
    return True

#diplomatic maneuvers need to be implemented
async def buyStatecraft(name:str, ctx:discord.Interaction, item:str) -> bool:

    
    try:
        id, group_type = idAndTypeFromName(name)
    except:
        return False
    
    groups = fileFromGroupType(group_type)
    
    with open(priceFile, "r") as f:
        prices = json.load(f)
    
    channel = client.get_channel(DeltaBotChannel)
    
    item = item.lower()
    
    if ctx.user.id != groups[id]["leader"]:
        await channel.send("You're not the leader of this group")
        return False
    
    match item:
        case "delegacy":
            if group_type == "faction":
                await channel.send("A delegacy is an Organization only building")
                return False

            #check max hasn't been reached
            if groups[id]["delegacy"]:
                cost = prices["Embassy"]
                if groups[id]["gold"] >= cost:
                    groups[id]["delegacy"] = True
                    groups[id]["gold"] -= cost
                else:
                    channel.send("Your group doesn't have enough gold")
                    return False
            else:
                channel.send("Your group already has a delegacy")
                return False
        
        case "embassy":
            if group_type == "organization":
                await channel.send("An embassy is a Faction only building")
                return False
            
            if groups[id]["embassy"]:
                cost = prices["Embassy"]
                if groups[id]["gold"] >= cost:
                    groups[id]["embassy"] = True
                    groups[id]["gold"] -= cost
                else:
                    channel.send("Your group doesn't have enough gold")
                    return False
            else:
                channel.send("Your group already has a embassy")
                return False
        
        case "campaign":
            await channel.send("Campaigns have variable cost in both gold and intrigue and thus cannot be bought in the shop.\n Please contact a mod, and they will help you in finding out which kind of campaign is right for you")
            return False
        
        case "diplomacy":
            channel.send("Diplomacy has not yet been developed so it cannot be bought at the current moment, apologies.")
            return False
    
    groupToFile(groups, group_type)
    return True



class MyCog(commands.Cog):
    def __init__(self):
        self.index = 0
        self.timer.start()

    def cog_unload(self):
        self.timer.cancel()

    # 2 weeks = 14 days = 24 * 14 hours = 336 hours total
    @tasks.loop(hours=336)
    async def timer(self):
        cleanGroups()
        await riotChanceCalc()
        await riotCalc()
        incomeCalc()
        upkeepCalc()
        periodCalc()

        

class taxView(discord.ui.View):
    @discord.ui.select( # the decorator that lets you specify the properties of the select menu
        placeholder = "How big should the taxes/money-cut be?", # the placeholder text that will be displayed if nothing is selected
        min_values = 1, # the minimum number of values that must be selected by the users
        max_values = 1, # the maximum number of values that can be selected by the users
        options = [ # the list of options from which users can choose, a required field
            discord.SelectOption(
                label="None",
                description="Pick this if you won't take any money"
            ),
            discord.SelectOption(
                label="Low",
                description="Pick this if you'll take a low amount"
            ),
            discord.SelectOption(
                label="Med",
                description="Pick this if you'll take a medium amount"
            ),
            discord.SelectOption(
                label="High",
                description="Pick this if you'll take a high amount"
            )
        ]
    )
    async def select_callback(self, interaction:discord.Interaction, select): # the function called when the user is done selecting options
        val = select.values[0]
        try:
            id, group_type = groupFromLeaderID(interaction.user.id)
        except:
            await interaction.response.send_message("You're not the leader of any group")
            return
            
        groups = fileFromGroupType(group_type)
        
        match val.lower():
            case "none":
                if group_type == "faction":
                    groups[id]["taxation"] = 0
                else:
                    groups[id]["money cut"] = 0

            case "low":
                if group_type == "faction":
                    groups[id]["taxation"] = 1
                else:
                    groups[id]["money cut"] = 1
            case "med":
                if group_type == "faction":
                    groups[id]["taxation"] = 2
                else:
                    groups[id]["money cut"] = 2
            case "high":
                if group_type == "faction":
                    groups[id]["taxation"] = 3
                else:
                    groups[id]["money cut"] = 3
        
        groupToFile(groups, group_type)
        
        await interaction.response.edit_message(content=f"The taxation/money-cut level has been set to {val}", view=None)
        return

class bribeView(discord.ui.View):
    @discord.ui.select( # the decorator that lets you specify the properties of the select menu
        placeholder = "Do you want to bribe government officials to look away from your black market fronts?", # the placeholder text that will be displayed if nothing is selected
        min_values = 1, # the minimum number of values that must be selected by the users
        max_values = 1, # the maximum number of values that can be selected by the users
        options = [ # the list of options from which users can choose, a required field
            discord.SelectOption(
                label="Yes",
                description="Pick this if you wish to bribe government officials"
            ),
            discord.SelectOption(
                label="No",
                description="Pick this if you don't wish to bribe government officials"
            )
        ]
    )
    async def select_callback(self, interaction:discord.Interaction, select): # the function called when the user is done selecting options
        val = select.values[0]
        try:
            id, group_type = groupFromLeaderID(interaction.user.id)
        except:
            await interaction.response.send_message("You're not the leader of any group")
            return
        
        if group_type != "organization":
            await interaction.response.send_message("You're not the leader of an organization")
            return
            
        groups = fileFromGroupType(group_type)
        
        match val.lower():
            case "yes":
                groups[id]["bribes"] = True


            case "no":
                groups[id]["bribes"] = False
        
        groupToFile(groups, group_type)
        
        await interaction.response.edit_message(content=f"You answered {val} to bribing the officials", view=None)
        return

class joinView(discord.ui.View):
    groupnames = getGroupNames()
    allOptions = []
    for name in groupnames:
        allOptions.append(discord.SelectOption(label=name))
    
    @discord.ui.select( # the decorator that lets you specify the properties of the select menu
        placeholder = "Which group would you like to join?", # the placeholder text that will be displayed if nothing is selected
        min_values = 1, # the minimum number of values that must be selected by the users
        max_values = 1, # the maximum number of values that can be selected by the users
        options = allOptions
    )
    async def select_callback(self, interaction:discord.Interaction, select): # the function called when the user is done selecting options
        val = select.values[0]
        try:
            id, group_type = idAndTypeFromName(val)
        except:
            await interaction.response.send_message("Something went wrong that shouldn't have! Please grab <@"+str(246913471415844864)+"> and get him to look into it")
            return
            
        groups = fileFromGroupType(group_type)

        group = groups[str(id)]
        leader = await interaction.guild.fetch_member(group["leader"])
        author = interaction.user
        authorMen = author.mention
        leaderMen = leader.mention
        
        with open(ExistingUserFile, "r") as f:
            ExistingUsers = json.load(f)
            
        if author.id in ExistingUsers:
            if len(ExistingUsers[str(author.id)]["organizations"]) + len(ExistingUsers[str(author.id)]["factions"]) > 3:
                await interaction.response.send_message("You are already a member of 4 groups")
                return
        
        if leader == author.id:
            await interaction.response.send_message(f"You are the leader of this {group_type}!")
            return

        if len(group["users"]) > 10:
            await interaction.response.send_message(f"This {group_type} is already full!")
            return
        
        await interaction.response.send_message(leaderMen + ", would you allow " + authorMen + " to join your group?\n y, n")

        # This will make sure that the response will only be registered if the following
        # conditions are met:
        def check(msg):
            return msg.author == leader and msg.channel == interaction.channel and msg.content.lower() in ["y", "n"]

        msg = await client.wait_for("message", check=check)
        if msg.content.lower() == "y":
            new_members = group["users"]
            new_members.append(author.id)
            groups[str(id)]["users"] = new_members 
            
            groupToFile(groups, type)
            
            await interaction.channel.send("Congratulations " + authorMen + ", you are now a proud part of " + val)
            
            if type.lower() == "organization":
                ExistingUsers[str(author.id)]["organizations"].append(id)
            elif type.lower() == "faction":   
                ExistingUsers[str(author.id)]["factions"].append(id)
            
            
            with open(ExistingUserFile, "w") as f:
                json.dump(ExistingUsers, f, indent=4)
        else:
            await interaction.channel.send("Sorry, " + authorMen + " you were not allowed to join " + val)

        await interaction.response.edit(content=f"You attempted to join: {val}", view=None)
        return

class showView(discord.ui.View):
    groupnames = getGroupNames()
    allOptions = []
    for name in groupnames:
        allOptions.append(discord.SelectOption(label=name))
    
    @discord.ui.select( # the decorator that lets you specify the properties of the select menu
        placeholder = "Which group would you like take a look at?", # the placeholder text that will be displayed if nothing is selected
        min_values = 1, # the minimum number of values that must be selected by the users
        max_values = 1, # the maximum number of values that can be selected by the users
        options = allOptions
    )
    async def select_callback(self, interaction:discord.Interaction, select): # the function called when the user is done selecting options
        val = select.values[0]
        try:
            id, group_type = idAndTypeFromName(val)
        except:
            await interaction.channel.send("Something went wrong that shouldn't have! Please grab <@"+str(246913471415844864)+"> and get him to look into it")
            return
            
        groups = fileFromGroupType(group_type)

        group = groups[str(id)]
    
        if group != "Available":
            name = group["name"]
            baseLvl = group["base level"]
            gold = group["gold"]
            intrigue = group["intrigue"]
            leader = group["leader"]
            members = group["users"]
            income = group["totalIncome"]
            upkeep = group["totalUpkeep"]
                    
            if group_type == "faction":
                if groups[id]["embassy"]:
                    Emb = " Your faction has an embassy."
                else:
                    Emb = " Your faction doesn't have an embassy."
            if group_type == "organization":
                if groups[id]["delegacy"]:
                    Emb = " Your organization has a delegacy."
                else:
                    Emb = " Your organization doesn't have a delegacy"

            em = discord.Embed(
                title=group_type,
                color=discord.Color(0x00ff00)
            )
            
            userString = ""
            for member in members:
                userString = userString + "<@" + str(member) + ">, "
            
            
            if interaction.user.id in members or interaction.user.id == leader:
                em.add_field(name=f"{name} -- Group Level: {baseLvl}", value=f"Gold: {gold}, Intrigue: {intrigue}, Income: {income}, Upkeep: {upkeep}\nLeader: <@{leader}>\nMembers: {userString}", inline=False)
                if group_type == "faction":
                    troopStr = ""
                    troops = group["custom troops"]
                    spyStr = ""
                    
                    match group["taxation"]:
                        case 0:
                            tax = "none"
                        case 1:
                            tax = "low"
                        case 2:
                            tax = "medium"
                        case 3:
                            tax = "high"
                    
                    for troop in troops:
                        troopStr = troopStr + troop + "With an offense of " + str(troops[troop]["offense"]) + ", a defense of " + str(troops[troop]["defense"]) + ", a loyalty of " + str(troops[troop]["loyalty"]) + ", and a speed of " + str(troops[troop]["speed"]) + "\n"
                        
                    for string in group["spy"]:
                        spyStr = spyStr + string + "\n"
                    
                    em.add_field(name="Buildings", value="There are " + str(group["farms"]) + " farm(s), " + str(group["roads"]) + " road(s), " + str(group["barracks"]) + " barrack(s). The current taxation level is: " + tax + "." + Emb, inline=False)
                    
                    em.add_field(name="troops", value="Your faction has " + str(group["militia"]) + " militia(s), " + str(group["militia archer"]) + " militia archer(s), and the following custom troop(s):\n" + troopStr, inline=False)
                    
                    em.add_field(name="spy-missions and statecraft", value="Your faction has the following spies, each occurence accounts for one spy: " + spyStr, inline=False)
                    
                    
                elif group_type == "organization":
                    troopStr = ""
                    troops = group["custom units"]
                    spyStr = ""
                    
                    match group["money cut"]:
                        case 0:
                            tax = "none"
                        case 1:
                            tax = "low"
                        case 2:
                            tax = "medium"
                        case 3:
                            tax = "high"
                    
                    if group["BMfront"] > 0 and group["bribes"]:
                        bribe = " of which bribes are handed out to stop them from being noticed."
                    elif group["BMfront"] > 0 and not group["bribes"]:
                        bribe = " of which no bribes are being handed out to stop them from being noticed, y'all like to live on the edge huh?"
                    
                    for troop in troops:
                        troopStr = troopStr + troop + " with an offense of " + str(troops[troop]["offense"]) + ", a defense of " + str(troops[troop]["defense"]) + ", a loyalty of " + str(troops[troop]["loyalty"]) + ", and a speed of " + str(troops[troop]["speed"]) + "\n"
                        
                    for string in group["spy"]:
                        spyStr = spyStr + string + ", "
                    
                    em.add_field(name="Buildings", value="There are " + str(group["ABfront"]) + " above-board front(s), " + str(group["BMfront"]) + " Black market front(s)," + bribe + "Your organization also has " + str(group["guardhouse"]) + " guardhouse(s). The current money cut level is: " + tax + "." + Emb, inline=False)
                    
                    em.add_field(name="troops", value="Your faction has " + str(group["guard"]) + " guard(s), " + str(group["ambusher"]) + " ambusher(s), and the following custom unit(s):\n" + troopStr, inline=False)
                    
                    em.add_field(name="spy-missions and statecraft", value="Your faction has the following spies, each occurence accounts for one spy at the named group: " + spyStr, inline=False)
                    
                await interaction.response.send_message(embed=em, ephemeral=True)
            else:
                em.add_field(name=f"{name} -- Group Level: {baseLvl}", value=f"Gold: {gold}, Income: {income}, Upkeep: {upkeep}\nLeader: <@{leader}>\nMembers: {userString}", inline=False)
                await interaction.channel.send(embed=em)
            
        else:
            await interaction.channel.send("Please denote a single existing and accepted group")

    
        await interaction.response.edit_message(content=f"You've chosen to show {val}", view=None)
        return

class catView(discord.ui.View):
    @discord.ui.select( # the decorator that lets you specify the properties of the select menu
        placeholder = "What category would you like to check out?", # the placeholder text that will be displayed if nothing is selected
        min_values = 1, # the minimum number of values that must be selected by the users
        max_values = 1, # the maximum number of values that can be selected by the users
        options = [ # the list of options from which users can choose, a required field
            discord.SelectOption(
                label="All"
            ),
            discord.SelectOption(
                label="Infrastructure"
            ),
            discord.SelectOption(
                label="Military"
            ),
            discord.SelectOption(
                label="Faction Infrastructure"
            ),
            discord.SelectOption(
                label="Faction Military"
            ),
            discord.SelectOption(
                label="Organization Infrastructure"
            ),
            discord.SelectOption(
                label="Organization Military"
            ),
            discord.SelectOption(
                label="Intrigue"
            ),
            discord.SelectOption(
                label="Statecraft"
            )
        ]
    )
    async def select_callback(self, interaction:discord.Interaction, select): # the function called when the user is done selecting options
        val = select.values[0]

        em = discord.Embed(
                    title="Shop",
                    color=discord.Color(0x0000FF)
                )
        with open(priceFile, "r") as f:
                    prices = json.load(f)
            
        front = prices["Establish Front"]
        prodLvl = prices["Production Level Up"]
        baseLvl = prices["Upgrade Base"]
        farms = prices["Farms"]
        roads = prices["Roads"]
        capital = prices["Capital"]
        
        spy = prices["Hire Spy"]
        sabo = prices["Sabotage"]
        espo = prices["Espionage"]
        
        guard = prices["Guard"]
        ambush = prices["Ambusher"]
        customUnit = prices["Custom Units"]
        guardhouse = prices["Guardhouse"]
        militia = prices["Militia"]
        militiaArcher = prices["Militia Archer"]
        customTroop = prices["Custom Troops"]
        barrack = prices["Barracks"]
        
        embassy = prices["Embassy"]
        loyalty = prices["Loyalty Campaign"]
        diplo = prices["Diplomatic Maneuvers"]
            
            
        match val:
            case "Infrastructure":
                em.add_field(name="Organization Infrastructure", value=f'''Establish Front -- {front} Gold
                                                            \nProduction Level Up -- {prodLvl} Gold
                                                            \nUpgrade Base -- {baseLvl} Gold''', inline=False)
                
                em.add_field(name="Faction Infrastructure", value=f'''Farms -- {farms} Gold
                                                            \nRoads base cost -- {roads} Gold
                                                            \nCapital -- {capital} Gold''')
                
            case "Organization Infrastructure":
                em.add_field(name="Organization Infrastructure", value=f'''Establish Front -- {front} Gold
                                                            \nProduction Level Up -- {prodLvl} Gold
                                                            \nUpgrade Base -- {baseLvl} Gold''')
                
            case "Faction Infrastructure":
                em.add_field(name="Faction Infrastructure", value=f'''Farms -- {farms} Gold
                                                            \nRoads base cost -- {roads} Gold
                                                            \nCapital -- {capital} Gold''')
                
            case "Intrigue":
                em.add_field(name="Intrigue", value=f'''Hire Spy -- {spy} Gold
                                                        \nSabotage -- {sabo} Gold
                                                        \nEspionage -- {espo} Gold''')
                
            case "Military":
                em.add_field(name="Organization Military", value=f'''Guard -- {guard} Gold
                                                        \nAmbusher -- {ambush} Gold
                                                        \nCustom Unit -- {customUnit} Gold
                                                        \nGuardhouse -- {guardhouse} Gold''', inline=False)
                
                em.add_field(name="Faction Military", value=f'''Guard -- {guard} Gold
                                                        \nAmbusher -- {ambush} Gold
                                                        \nCustom Unit -- {customUnit} Gold
                                                        \nGuardhouse -- {guardhouse} Gold''')
                
            case "Organization Military":
                em.add_field(name="Organization Military", value=f'''Guard -- {guard} Gold
                                                        \nAmbusher -- {ambush} Gold
                                                        \nCustom Unit -- {customUnit} Gold
                                                        \nGuardhouse -- {guardhouse} Gold''')
                
            case "Faction Military":
                em.add_field(name="Faction Military", value=f'''Guard -- {guard} Gold
                                                        \nAmbusher -- {ambush} Gold
                                                        \nCustom Unit -- {customUnit} Gold
                                                        \nGuardhouse -- {guardhouse} Gold''')
                
            case "Statecraft":
                em.add_field(name="Statecraft", value=f'''Embassy/Delegacy -- {embassy} Gold
                                                        \nLoyalty campaign -- {loyalty} Gold
                                                        \nDiplomatic Maneuvers -- {diplo} Gold''')
                
            case "All":
                em.add_field(name="Organization Infrastructure", value=f'''Establish Front -- {front} Gold
                                                            \nProduction Level Up -- {prodLvl} Gold
                                                            \nUpgrade Base -- {baseLvl} Gold''')
                
                em.add_field(name="Organization Military", value=f'''Guard -- {guard} Gold
                                                        \nAmbusher -- {ambush} Gold
                                                        \nCustom Unit -- {customUnit} Gold
                                                        \nGuardhouse -- {guardhouse} Gold''')
                
                em.add_field(name="Intrigue", value=f'''Spy -- {spy} Gold
                                                        \nSabotage -- {sabo} Gold
                                                        \nEspionage -- {espo} Gold''')
                
                em.add_field(name="Faction Infrastructure", value=f'''Farms -- {farms} Gold
                                                            \nRoads base cost -- {roads} Gold
                                                            \nCapital -- {capital} Gold''')
                
                em.add_field(name="Faction Military", value=f'''Militia -- {militia} Gold
                                                        \nArcher -- {militiaArcher} Gold
                                                        \nCustom troops -- {customTroop} Gold
                                                        \nBarracks -- {barrack} Gold''')
                
                em.add_field(name="Statecraft", value=f'''Embassy/Delegacy -- {embassy} Gold
                                                        \nLoyalty campaign -- {loyalty} Gold
                                                        \nDiplomacy -- {diplo} Gold''')
        
        await interaction.channel.send(embed=em)
        await interaction.response.edit_message(content=f"You are now looking at shop items of the category: {val}", view=None)
        
        return

class facRem(discord.ui.View):
    with open(FactionFile, "r") as f:
        Facs = json.load(f)
        
    groupnames = []
        
    for fac in Facs:
        if Facs[fac] != "Available":
            groupnames.append(Facs[fac]["name"])
    
    allOptions = []
    for name in groupnames:
        allOptions.append(discord.SelectOption(label=name))
    
    @discord.ui.select( # the decorator that lets you specify the properties of the select menu
        placeholder = "Which factioon would you like to remove?", # the placeholder text that will be displayed if nothing is selected
        min_values = 1, # the minimum number of values that must be selected by the users
        max_values = 1, # the maximum number of values that can be selected by the users
        options = allOptions
    )
    async def select_callback(self, interaction:discord.Interaction, select): # the function called when the user is done selecting options
        val = select.values[0]
        
        try:
            id, _ = idAndTypeFromName(val)
        except:
            await interaction.response.send_message("Something went wrong that shouldn't have! Please grab <@"+str(246913471415844864)+"> and get him to look into it")
            return
        
        with open(FactionFile, "r") as f:
            Facs = json.load(f)
        
        with open(ExistingUserFile, "r") as f:
            ExistingUsers:list = json.load(f)
                
        for uID in Facs[str(id)]["users"]:
            try:
                ExistingUsers[str(uID)]["factions"].remove(id)
            except:
                print("Key error, most likely that user can't be found in the ExistingUsers file, or that the group ID wasn't saved to the user")
        try:
            ExistingUsers[str(Facs[str(id)]["leader"])]["factions"].remove(id)
        except:
            print("Key error, most likely that the leader can't be found in the ExistingUsers file, or that the group ID wasn't saved to the leader")
        
        Facs[str(id)] = "Available"
        
        with open(FactionFile, "w") as f:
            json.dump(Facs, f, indent=4)
            
        with open(ExistingUserFile, "w") as f:
            json.dump(ExistingUsers, f, indent=4)
            
        await interaction.response.edit_message("Faction removed!", view=None)
        
        return

class orgRem(discord.ui.View):
    with open(organizationFile, "r") as f:
        orgs = json.load(f)
        
    groupnames = []
        
    for org in orgs:
        if orgs[org] != "Available":
            groupnames.append(orgs[org]["name"])
    
    allOptions = []
    for name in groupnames:
        allOptions.append(discord.SelectOption(label=name))
    
    @discord.ui.select( # the decorator that lets you specify the properties of the select menu
        placeholder = "Which organization would you like to remove?", # the placeholder text that will be displayed if nothing is selected
        min_values = 1, # the minimum number of values that must be selected by the users
        max_values = 1, # the maximum number of values that can be selected by the users
        options = allOptions
    )
    async def select_callback(self, interaction:discord.Interaction, select): # the function called when the user is done selecting options
        val = select.values[0]
        
        try:
            id, _ = idAndTypeFromName(val)
        except:
            await interaction.response.send_message("Something went wrong that shouldn't have! Please grab <@"+str(246913471415844864)+"> and get him to look into it")
            return

        with open(organizationFile, "r") as f:
            Orgs = json.load(f)
        
        with open(ExistingUserFile, "r") as f:
            ExistingUsers = json.load(f)
                

        for uID in Orgs[str(id)]["users"]:
            try:
                ExistingUsers[str(uID)]["organizations"].remove(id)
            except:
                print("Key error, most likely that user can't be found in the ExistingUsers file, or that the group ID wasn't saved to the user")
        try:
            ExistingUsers[str(Orgs[str(id)]["leader"])]["organizations"].remove(id)
        except:
            print("Key error, most likely that the leader can't be found in the ExistingUsers file, or that the group ID wasn't saved to the leader")
        
        Orgs[str(id)] = "Available"
                
        with open(organizationFile, "w") as f:
            json.dump(Orgs, f, indent=4)
            
        with open(ExistingUserFile, "w") as f:
            json.dump(ExistingUsers, f, indent=4)
            
        await interaction.response.edit_message("Organization removed!", view=None)
        
        return

class facBuy(discord.ui.View):
    #infrastructure = ["road", "capital", "farm"]
    #intrigue = ["spy", "sabotage", "espionage"]
    #statecraft = ["embassy", "campaign", "diplomacy"]
    #military = ["militia", "archer", "custom troop", "barrack"]
    #["farm", "front", "production level up", "road", "upgrade base", "capital", "spy", "sabotage", "espionage", "militia",
    # "archer", "custom", "barrack", "guard", "ambusher", "guardhouse", "embassy", "delegacy", "campaign", "diplomacy"]
    @discord.ui.select( # the decorator that lets you specify the properties of the select menu
        placeholder = "Which building would you like to purcahse?", # the placeholder text that will be displayed if nothing is selected
        min_values = 1, # the minimum number of values that must be selected by the users
        max_values = 1, # the maximum number of values that can be selected by the users
        options = [ # the list of options from which users can choose, a required field
            discord.SelectOption(
                label="Road"
            ),
            discord.SelectOption(
                label="Capital"
            ),
            discord.SelectOption(
                label="Farm"
            ),
            discord.SelectOption(
                label="Spy"
            ),
            discord.SelectOption(
                label="Sabotage"
            ),
            discord.SelectOption(
                label="Espionage"
            ),
            discord.SelectOption(
                label="Embassy"
            ),
            discord.SelectOption(
                label="Campaign"
            ),
            discord.SelectOption(
                label="Diplomacy"
            ),
            discord.SelectOption(
                label="Militia"
            ),
            discord.SelectOption(
                label="Archer"
            ),
            discord.SelectOption(
                label="Custom"
            ),
            discord.SelectOption(
                label="Barrack"
            )
        ]
    )
    async def select_callback(self, interaction:discord.Interaction, select): # the function called when the user is done selecting options
        infrastructure = ["road", "capital", "farm"]
        intrigue = ["spy", "sabotage", "espionage"]
        statecraft = ["embassy", "campaign", "diplomacy"]
        military = ["militia", "archer", "custom troop", "barrack"]
        val = select.values[0].lower()
        
        try:
            id, group_type = groupFromLeaderID(interaction.user.id)
        except:
            await interaction.response.send_message("Something went wrong that shouldn't have! Please grab <@"+str(246913471415844864)+"> and get him to look into it")
            return

        groups = fileFromGroupType(group_type)
    
        name = groups[str(id)]["name"]
    
        if val in infrastructure:
            await interaction.response.defer()
            success = await buyInfrastructure(name, interaction, val)
        elif val in intrigue:
            await interaction.response.defer()
            success = await buyIntrigue(name, interaction, val)
        elif val in military:
            await interaction.response.defer()
            success = await buyMilitary(name, interaction, val)
        elif val in statecraft:
            await interaction.response.defer()
            success = await buyStatecraft(name, interaction, val)
        
        response = await interaction.original_response()
        
        if success:
            await response.delete()
            await interaction.channel.send("The purchase was succesful")
        else:
            await response.delete()
            await interaction.channel.send("The purchase failed")
            
        return
    
class orgBuy(discord.ui.View):
    #infrastructure = ["upgrade base", "front", "production level up"]
    #intrigue = ["spy", "sabotage", "espionage"]
    #statecraft = ["embassy", "campaign", "diplomacy"]
    #military = ["guard", "ambusher", "custom unit", "guardhouse"]
    #["farm", "front", "production level up", "road", "upgrade base", "capital", "spy", "sabotage", "espionage", "militia",
    # "archer", "custom", "barrack", "guard", "ambusher", "guardhouse", "embassy", "delegacy", "campaign", "diplomacy"]
    @discord.ui.select( # the decorator that lets you specify the properties of the select menu
        placeholder = "Which building would you like to purcahse?", # the placeholder text that will be displayed if nothing is selected
        min_values = 1, # the minimum number of values that must be selected by the users
        max_values = 1, # the maximum number of values that can be selected by the users
        options = [ # the list of options from which users can choose, a required field
            discord.SelectOption(
                label="Upgrade Base"
            ),
            discord.SelectOption(
                label="Front"
            ),
            discord.SelectOption(
                label="Production Level Up"
            ),
            discord.SelectOption(
                label="Spy"
            ),
            discord.SelectOption(
                label="Sabotage"
            ),
            discord.SelectOption(
                label="Espionage"
            ),
            discord.SelectOption(
                label="Delegacy"
            ),
            discord.SelectOption(
                label="Campaign"
            ),
            discord.SelectOption(
                label="Diplomacy"
            ),
            discord.SelectOption(
                label="Guard"
            ),
            discord.SelectOption(
                label="Ambusher"
            ),
            discord.SelectOption(
                label="Custom"
            ),
            discord.SelectOption(
                label="Guardhouse"
            )
        ]
    )
    async def select_callback(self, interaction:discord.Interaction, select): # the function called when the user is done selecting options
        infrastructure = ["upgrade base", "front", "production level up"]
        intrigue = ["spy", "sabotage", "espionage"]
        statecraft = ["delegacy", "campaign", "diplomacy"]
        military = ["guard", "ambusher", "custom unit", "guardhouse"]
        val = select.values[0].lower()
        
        try:
            id, group_type = groupFromLeaderID(interaction.user.id)
        except:
            await interaction.response.send_message("Something went wrong that shouldn't have! Please grab <@"+str(246913471415844864)+"> and get him to look into it")
            return

        groups = fileFromGroupType(group_type)
    
        name = groups[str(id)]["name"]
    
        if val in infrastructure:
            await interaction.response.defer()
            success = await buyInfrastructure(name, interaction, val)
        elif val in intrigue:
            await interaction.response.defer()
            success = await buyIntrigue(name, interaction, val)
        elif val in military:
            await interaction.response.defer()
            success = await buyMilitary(name, interaction, val)
        elif val in statecraft:
            await interaction.response.defer()
            success = await buyStatecraft(name, interaction, val)
        
        response = await interaction.original_response()
        
        if success:
            await response.delete()
            await interaction.channel.send("The purchase was succesful")
        else:
            await response.delete()
            await interaction.channel.send("The purchase failed")
            
        return   
    

@tree.command(
    name="test",
    description=
    "a test command that tests various function"
)
async def Test(ctx):
    intrigueIncome()
    await ctx.response.send_message("command has been run")
    return

@tree.command(
    name="showgroup",
    description=
    "Used to see the current stats of a group"
)
async def ShowGroup(ctx):
    await ctx.response.send_message("Which group do you want shown?",view=showView())
    return

@tree.command(
    name="joingroup",
    description=
    "Used to send a request to join a group to that groups leader"
)
@app_commands.checks.cooldown(1, 3600.0)
async def JoinGroup(ctx):
    await ctx.response.send_message("Which group do you want to join?",view=joinView())
    return
@JoinGroup.error
async def on_application_command_error(ctx: discord.Interaction, error: discord.DiscordException):
    if isinstance(error, app_commands.CommandOnCooldown):
        await ctx.response.send_message("This command has a cooldown to prevent spam-pinging group leaders. You can send 1 request every hour")
    else:
        raise error  # Here we raise other errors to ensure they aren't ignored


@tree.command(
    name="changeleader",
    description=
    "Used by a mod to change the leader of a group"
)
@app_commands.describe(
    name='The name of the group you wish to change the leader of',
    new_leader="The @ of the person who will become the leader of the noted group"
)
@app_commands.checks.has_any_role(687105162569187430, 761621207270948874, 1047119025332813925)
async def changeLeader(ctx, name:str, new_leader:discord.Member):
    try:
        id, group_type = idAndTypeFromName(name)
    except:
        return
    
    groups = fileFromGroupType(group_type)
    
    if groups == None:
        return
    
    with open(ExistingUserFile, "r") as f:
        ExistingUsers:list = json.load(f)
        

    if ExistingUsers[str(new_leader.id)]["factions"] + ExistingUsers[str(new_leader.id)]["organizations"] == 4 and\
    (id not in ExistingUsers[str(new_leader.id)]["organizations"] and id not in ExistingUsers[str(new_leader.id)]["factions"]):    
        await ctx.response.send_message("This user is part of too many groups")
        return
    
    if new_leader.id in groups[str(id)]["users"]:
        groups[str(id)]["users"].remove(new_leader.id)
    
    if group_type.lower() == "organization":
        ExistingUsers[str(groups[str(id)]["leader"])]["organizations"].remove(id)
    elif group_type.lower() == "faction":
        ExistingUsers[str(groups[str(id)]["leader"])]["factions"].remove(id)
    
    groups[str(id)]["leader"] = new_leader.id
    
    if group_type.lower() == "organization":
        ExistingUsers[str(new_leader.id)]["organizations"].append(id)
    elif group_type.lower() == "faction":
        ExistingUsers[str(new_leader.id)]["factions"].append(id)
    
    
    groupToFile(groups, group_type)
    with open(ExistingUserFile, "w") as f:
        json.dump(ExistingUsers, f, indent=4)
    
    groupName = groups[str(id)]["name"]
    await ctx.response.send_message(f"Leader has been changed for {groupName}")
    return
@changeLeader.error
async def on_application_command_error(ctx: discord.Interaction, error: discord.DiscordException):
    if isinstance(error, app_commands.MissingAnyRole):
        await ctx.response.send_message("Sorry, only Mods or Admins can use this command!")
    else:
        raise error  # Here we raise other errors to ensure they aren't ignored


@tree.command(
    name="groupshop",
    description=
    "Used to show every item in the shop"
)
async def groupShop(ctx):
    await ctx.response.send_message("What category would you like to check out?",view=catView())
    return

@tree.command(
    name="buy",
    description=
    "The command used to buy from the group shop"
)
async def buy(ctx):
    try:
        _, group_type = groupFromLeaderID(ctx.user.id)
    except:
        await ctx.response.delete()
        await ctx.channel.send("You're not the leader of a group")
        return
    
    if group_type == "faction":
        await ctx.response.send_message("It seems you're the leader of a faction, lemme show you what you can buy for it", view=facBuy())
    else:
        await ctx.response.send_message("It seems you're the leader of an organization, lemme show you what you can buy for it", view=orgBuy())
        
    return


group = app_commands.Group(name="set", description="command used to set either bribes or tax/money cut")

@group.command(name="tax", description="used to set the taxation/money-cut level")
async def Tax(ctx):
    await ctx.response.send_message("How big should the taxes/money-cut be?",view=taxView(), ephemeral=True)
    return


@group.command(name="bribe", description="Used to decide whether you bribe anyone after your black-market front")
async def bribe(ctx):
    await ctx.response.send_message("Do you want to bribe government officials to look away from your black market fronts?",view=bribeView(), ephemeral=True)
    return

tree.add_command(group)



group = app_commands.Group(name="remove", description="command used by mods to remove various values from the databases")

@group.command(name="resource", description="remove a specific amount of a specific resouece from a specific group")
@app_commands.checks.has_any_role(687105162569187430, 761621207270948874, 1047119025332813925)
@app_commands.describe(
    name='The name of the group you wish to remove resources from',
    resource="the resource you wish to remove, either intrigue or gold",
    amt="the amount you wish to remove as a positive whole number"
)
async def RemRes(ctx, name:str, resource:str, amt:int):
    try:
        id, group_type = idAndTypeFromName(name)
    except:
        return
    
    groups = fileFromGroupType(group_type)
    
    if resource.lower() == "gold":
        groups[id]["gold"] -= amt
    elif resource.lower() == "intrigue":
        groups[id]["intrigue"] -= amt
    else:
        ctx.response.send_message("The only existing resources are gold and intrigue")
        return
    
    ctx.response.send_message(f"{amt} {resource} has been removed from {name}")
    
    return
@RemRes.error
async def on_application_command_error(ctx: discord.Interaction, error: discord.DiscordException):
    if isinstance(error, app_commands.MissingAnyRole):
        await ctx.response.send_message("Sorry, only Mods or Admins can use this command!")
    else:
        raise error  # Here we raise other errors to ensure they aren't ignored


@group.command(name="organization", description="remove an organization from the database")
@app_commands.checks.has_any_role(687105162569187430, 761621207270948874, 1047119025332813925)
async def RemOrg(ctx):
    await ctx.response.send_message("Which organization would you like to remove?", view=orgRem())
    return
@RemOrg.error
async def on_application_command_error(ctx: discord.Interaction, error: discord.DiscordException):
    if isinstance(error, commands.MissingAnyRole):
        await ctx.response.send_message("Sorry, only Mods or Admins can use this command!")
    else:
        raise error  # Here we raise other errors to ensure they aren't ignored

@group.command(name="faction", description="remove a faction from the database")
@app_commands.checks.has_any_role(687105162569187430, 761621207270948874, 1047119025332813925)
async def RemFac(ctx):   
    await ctx.response.send_message("Which faction would you like to remove?", view=facRem())
    return
@RemFac.error
async def on_application_command_error(ctx: discord.Interaction, error: discord.DiscordException):
    if isinstance(error, app_commands.MissingAnyRole):
        await ctx.response.send_message("Sorry, only Mods or Admins can use this command!")
    else:
        raise error  # Here we raise other errors to ensure they aren't ignored

tree.add_command(group)



group = app_commands.Group(name="add", description="command used by mods to add various values from the databases")

@group.command(name="custom_npc", description="add a custom npc to the group")
@app_commands.checks.has_any_role(687105162569187430, 761621207270948874, 1047119025332813925)
@app_commands.describe(
    group_name='The name of the group you wish to add the custom npc to',
    name="the name of the custom npc",
    offense="the offensive level of the custom npc",
    defense="the defensive level of the custom npc",
    loyalty="the loyalty level of the custom npc",
    speed="the speed level of the custom npc",
    cost_gold="the cost of the custom npc, in gold",
    cost_intrigue="the cost of the custom npc, in intrigue"
)
async def AddNPC(ctx, group_name:str, name:str, offense:int, defense:int, loyalty:int, speed:int, cost_gold:int, cost_intrigue:int):
    try:
        id, group_type = idAndTypeFromName(group_name)
    except:
        return
        
    groups = fileFromGroupType(group_type)
    
    if groups[id]["gold"] >= cost_gold and groups[id]["intrigue"] >= cost_intrigue:
        groups[id]["gold"] -= cost_gold
        groups[id]["intrigue"] -= cost_intrigue
        
    else:
        await ctx.response.send_message("{name} either does not have enough gold, or does not have enough intrigue")
        return
    
    if group_type == "organization":
        groups[str(id)]["custom units"][name] = {"offense": offense, "defense": defense, "loyalty": loyalty, "speed": speed}
    else:
        groups[str(id)]["custom troops"][name] = { "offense": offense, "defense": defense, "loyalty": loyalty, "speed": speed }
        
    groupToFile(groups, group_type)
    
    await ctx.response.send_message(f"Custom offensive NPCs have been added to {name}!")
    
    return
@AddNPC.error
async def on_application_command_error(ctx: discord.Interaction, error: discord.DiscordException):
    if isinstance(error, app_commands.MissingAnyRole):
        await ctx.response.send_message("Sorry, only Mods or Admins can use this command!")
    else:
        raise error  # Here we raise other errors to ensure they aren't ignored

@group.command(name="organization", description="add an organization to the database")
@app_commands.checks.has_any_role(687105162569187430, 761621207270948874, 1047119025332813925)
@app_commands.describe(
    name='The name of the organization you wish to create',
    leader="the @ of the leader of the organization"
)
async def AddOrg(ctx, name: str, leader: discord.Member):
    orgData = {}
    i = 1
    with open(organizationFile, "r") as f:
        Orgs = json.load(f)
        
    with open(ExistingUserFile, "r") as f:
        ExistingUsers = json.load(f)
        
    if groupFromLeaderID(leader.id) is tuple((int, str)):
        await ctx.response.send_message("That person is already leading a group")
        return
        
    if leader.id in ExistingUsers:
        if len(ExistingUsers[str(leader.id)]["organizations"]) + len(ExistingUsers[str(leader.id)]["factions"]) > 3:
            await ctx.response.send_message("That person is already in 4 groups")
            return
        
    if idAndTypeFromName(name) is tuple(int, str):
        await ctx.response.send_message("A group with that name already exists!")
        return
    
    for org in Orgs:
        if Orgs[org] == "Available":
            id = i
        else:
            id = len(Orgs)+1
        i=i+1
    
    orgData["name"] = name
    orgData["base level"] = 1
    orgData["gold"] = 0
    orgData["intrigue"] = 0
    orgData["id"] = id
    orgData["leader"] = leader.id
    orgData["users"] = []
    
    orgData["totalIncome"] = 0
    orgData["totalUpkeep"] = 0
    orgData["riot"] = False
    orgData["riotChance"] = 0
    
    orgData["ABfront"] = 0
    orgData["BMfront"] = 0
    orgData["bribes"] = False
    orgData["production level up"] = 0
    orgData["money cut"] = 0
    orgData["upgrade base"] = 0
    
    orgData["guard"] = 0
    orgData["ambusher"] = 0
    orgData["custom units"] = {}
    orgData["guardhouse"] = 0
    
    orgData["spy"] = []
    orgData["sabotage"] = {}
    orgData["espionage"] = {}
    
    orgData["delegacy"] = False
    orgData["loyalty campaign"] = {}
    orgData["diplomatic maneuvers"] = {}
    
    Orgs[str(id)] = orgData
    
    with open(organizationFile, "w") as f:
        json.dump(Orgs, f, indent=4)
        
    ExistingUsers[str(leader.id)]["organizations"].append(id)
    
    with open(ExistingUserFile, "w") as f:
        json.dump(ExistingUsers, f, indent=4)
    
    await ctx.response.send_message(f"Organization created with id: {id}!")
    
    return
@AddOrg.error
async def on_application_command_error(ctx: discord.Interaction, error: discord.DiscordException):
    if isinstance(error, app_commands.MissingAnyRole):
        await ctx.response.send_message("Sorry, only Mods or Admins can use this command!")
    else:
        raise error  # Here we raise other errors to ensure they aren't ignored

@group.command(name="faction", description="add a faction to the database")
@app_commands.checks.has_any_role(687105162569187430, 761621207270948874, 1047119025332813925)
@app_commands.describe(
    name='The name of the faction you wish to create',
    leader="the @ of the leader of the faction"
)
async def AddFac(ctx, name: str, leader: discord.Member):
    FacData = {}
    i = 1
    with open(FactionFile, "r") as f:
        Facs = json.load(f)
        
    with open(ExistingUserFile, "r") as f:
        ExistingUsers = json.load(f)
        
    if leader.id in ExistingUsers:
        if len(ExistingUsers[str(leader.id)]["organizations"]) + len(ExistingUsers[str(leader.id)]["factions"]) > 3:
            await ctx.response.send_message("That person is already in 4 groups")
            return
        
    if groupFromLeaderID(leader.id) is tuple((int, str)):
        await ctx.response.send_message("That person is already leading a group")
        return
        
    if idAndTypeFromName(name) is tuple((int, str)):
        await ctx.response.send_message("A group with that name already exists!")
        return
        
    for fac in Facs:
        if Facs[fac] == "Available":
            id = i
        else:
            id = len(Facs)+1
        i=i+1
    
    FacData["name"] = name
    FacData["base level"] = 1
    FacData["gold"] = 0
    FacData["intrigue"] = 0
    FacData["id"] = id
    FacData["leader"] = leader.id
    FacData["users"] = []

    FacData["totalIncome"] = 0
    FacData["totalUpkeep"] = 0
    FacData["riot"] = False
    FacData["riotChance"] = 0

    FacData["farms"] = 0
    FacData["roads"] = 0
    FacData["capital"] = 0
    FacData["taxation"] = 0

    FacData["militia"] = 0
    FacData["militia archer"] = 0
    FacData["custom troops"] = {}
    FacData["barracks"] = 0
    
    FacData["spy"] = []
    FacData["sabotage"] = {}
    FacData["espionage"] = {}

    FacData["embassy"] = False
    FacData["loyalty campaign"] = {}
    FacData["diplomatic maneuvers"] = {}
    
    Facs[str(id)] = FacData
    
    with open(FactionFile, "w") as f:
        json.dump(Facs, f, indent=4)
        
    ExistingUsers[str(leader.id)]["factions"].append(id)
    
    with open(ExistingUserFile, "w") as f:
        json.dump(ExistingUsers, f, indent=4)
    
    await ctx.response.send_message(f"Faction created with id: {id}!")
    
    return
@AddFac.error
async def on_application_command_error(ctx: discord.Interaction, error: discord.DiscordException):
    if isinstance(error, app_commands.MissingAnyRole):
        await ctx.response.send_message("Sorry, only Mods or Admins can use this command!")
    else:
        raise error  # Here we raise other errors to ensure they aren't ignored

@group.command(name="sabotage", description="add a successful sabotage to a group")
@app_commands.checks.has_any_role(687105162569187430, 761621207270948874, 1047119025332813925)
@app_commands.describe(
    name='The name of the group that launches the attack',
    target_name="The name of the group that is the target of the attack",
    unrest="The amount of unrest added to the target group, preferably a value between 5 and 30",
    length="How many upkeep-periods this sabotage will last (one upkeep period is 2 weeks)",
    cost_gold="The cost of the mission, in gold",
    cost_intrigue="The cose of the mission, in intrigue"
)
async def addSabotage(ctx, name:str, target_name:str, unrest:int, length:int, cost_gold:int, cost_intrigue:int):
    missionCount = 1
    
    try:
        id, group_type = idAndTypeFromName(name)
        _, _ = idAndTypeFromName(target_name)
    except:
        return
    
    attacker = fileFromGroupType(group_type)
    
    if attacker[id]["gold"] >= cost_gold and attacker[id]["Intrigue"] >= cost_intrigue:
        attacker[id]["gold"] -= cost_gold
        attacker[id]["intrigue"] -= cost_intrigue
    else:
        await ctx.response.send_message(f"{name} does not have enough Gold")
        return
    
    for mission in attacker[str(id)]["sabotage"]:
        
        if attacker[str(id)]["sabotage"][mission]["time left"] == 0:
            attacker[str(id)]["sabotage"][mission] = "Available"
            
        if attacker[str(id)]["sabotage"][mission] == "Available":
            attacker[str(id)]["sabotage"][mission] = { "target name": target_name, "unrest%": unrest, "Time left": length}
            
        else:
            attacker[str(id)]["sabotage"][str(missionCount)] = { "target name": target_name, "unrest%": unrest, "Time left": length}
    
    groupToFile(attacker, group_type)
    
    await ctx.response.send_message(f"Succesful sabotage against {target_name} has been added to {name}!")
            
    return
@addSabotage.error
async def on_application_command_error(ctx: discord.Interaction, error: discord.DiscordException):
    if isinstance(error, app_commands.MissingAnyRole):
        await ctx.response.send_message("Sorry, only Mods or Admins can use this command!")
    else:
        raise error  # Here we raise other errors to ensure they aren't ignored

@group.command(name="loyalty_campaign", description="add a successful loyalty campaign to a group")
@app_commands.checks.has_any_role(687105162569187430, 761621207270948874, 1047119025332813925)
@app_commands.describe(
    name='The name of the group that launches the attack',
    reduction="The amount of unrest added to the target group, preferably a value between 1 and 25",
    length="How many upkeep-periods this sabotage will last (one upkeep period is 2 weeks)",
    cost_gold="The cost of the mission, in gold",
    cost_intrigue="The cose of the mission, in intrigue"
)
async def addLoyalty(ctx, name:str, reduction:int, length:int, cost_gold:int, cost_intrigue:int):
    missionCount = 0
    
    try:
        id, group_type = idAndTypeFromName(name)
    except:
        return
    
    groups = fileFromGroupType(group_type)
    
    status = status.lower()
    
    if groups[id]["gold"] >= cost_gold and groups[id]["Intrigue"] >= cost_intrigue:
        groups[id]["gold"] -= cost_gold
        groups[id]["intrigue"] -= cost_intrigue
    else:
        await ctx.response.send_message(f"{name} does not have enough Gold")
        return
    
    for mission in groups[str(id)]["loyalty campaign"]:
        missionCount += 1
        if groups[str(id)]["loyalty campaign"][mission]["time left"] == 0:
            groups[str(id)]["loyalty campaign"][mission] = "Available"
            
        if groups[str(id)]["loyalty campaign"][mission] == "Available":
            groups[str(id)]["loyalty campaign"][mission] = { "unrest%": reduction, "Time left": length}
            
        else:
            groups[str(id)]["loyalty campaign"][str(missionCount)] = { "unrest%": reduction, "Time left": length}
    
    groupToFile(groups, group_type)
    
    await ctx.response.send_message(f"Loyalty campaign has been added to {name}!")
            
    return
@addLoyalty.error
async def on_application_command_error(ctx: discord.Interaction, error: discord.DiscordException):
    if isinstance(error, app_commands.MissingAnyRole):
        await ctx.response.send_message("Sorry, only Mods or Admins can use this command!")
    else:
        raise error  # Here we raise other errors to ensure they aren't ignored

tree.add_command(group)



@tree.command(
    name="changeprice",
    description=
    "Used to change the price of an item, given the name of the item and the new price"
)
@app_commands.checks.has_any_role(687105162569187430, 761621207270948874, 1047119025332813925)
async def changePrice(ctx, item:str, price:int):
    with open(priceFile, "r") as f:
                prices = json.load(f)
    newPrices = {}
    if item in prices:
        for ent in prices:
            if item == prices[ent]:
                newPrices[ent] = price
            else:
                newPrices[ent] = prices[ent]
                
        with open(priceFile, "w") as f:
            json.dump(newPrices, f, indent=4)
        
        await ctx.response.send_message(f"Price has been updated to {price} for {item}!")
    else:
        await ctx.response.send_message(f"{item} does not exist in the shop")
            
    return
@changePrice.error
async def on_application_command_error(ctx: discord.Interaction, error: discord.DiscordException):
    if isinstance(error, app_commands.MissingAnyRole):
        await ctx.response.send_message("Sorry, only Mods or Admins can use this command!")
    else:
        raise error  # Here we raise other errors to ensure they aren't ignored


client.run(
    'BUT TOKEN HERE')
