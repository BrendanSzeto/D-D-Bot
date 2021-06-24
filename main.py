import discord
import os
import helper_functions as helper_functions
from discord.ext import commands

token = os.environ['BOT_TOKEN']

bot = commands.Bot(command_prefix='!', case_insensitive=True, help_command=None)

# Events
# Bot goes online
@bot.event
async def on_ready():
  print('Logged in as {0.user}'.format(bot))

# Bot recieves message
@bot.event
async def on_message(message):
    if message.author.bot:                # Ignore messages sent by other bots
        return  
    await bot.process_commands(message)   # Check if message contains a command


# Commands
# Shows what commands the bot can perform
@bot.command(name='help')
async def help(ctx):
  msg = 'Use the following list to find what you are looking for!\n' \
        '**!hello** - Hello!\n' \
        '**!roll** *<number-of-dice>*d*<number-of-sides>* - Rolls a specified number of dice. \n' \
        '**!stats** - Generates a set of ability scores for a character randomly.\n' \
        '**!query-spell** *<spell-name>* - Gives information about a spell when given its name.\n' \
        '**!query-magic-item** *<item-name>* - Gives information about a magic item when given its name.\n' \
        '**!query-item** *<item-name>* - Gives information about a piece of equipment when given its name' \
        ' (includes weapons, armor, and adventuring gear).'
  await ctx.send(msg)

# Says hello
@bot.command(name='hello')
async def hello(ctx):
    await ctx.send("Hello!")

#Rolls a specificed number of dice
@bot.command(name='roll')
async def roll(ctx, arg : str):
  roll = arg.split('d')

  # Check if number of dice and number of sides are valid
  try:
    amount = int(roll[0])
    sides = int(roll[1])
  except ValueError:
    await ctx.send('**Error:** Please make sure the number of dice/sides are numbers.')

  # Check if number of dice and number of sides are positive
  if amount > 0 and sides > 0:
    msg = '**Result (' + arg + '):** '

    # "Roll" the dice and display the results and total
    results, total = helper_functions.roll_dice(amount, sides)
    str_results = [str(int) for int in results]
    msg += ' '.join(str_results)
    if len(msg) < 2000:
      await ctx.channel.send(msg + '\n**Total:** ' + str(total))
    else:
      await ctx.channel.send('**Total:** ' + str(total) + '\n*Result cut off due to length*')

  else:
    await ctx.send('**Error:** Please make sure the number of dice/sides are valid numbers.')
    
# Rolls four 6-sided dice, removes the lowest number in that set, and then sums the remaining three. Does this 6 times, once for each stat
@bot.command(name='stats')
async def stats(ctx):
  msg = '**Randomly Generated Stats:**\n```'
  for i in range(6):
    results, total = helper_functions.roll_dice(4, 6)
    str_results = [str(int) for int in results]
    msg += ' '.join(str_results)

    results.pop(results.index(min(results)))
    str_results = [str(int) for int in results]
    msg += "\t->\t" + ' '.join(str_results)
    msg += ":\t" + str(sum(results)) + "\n"
  msg += "```"
  await ctx.send(msg)

# Searches the D&D API for specified spells
@bot.command(name='query-spell')
async def query_spell(ctx, *, arg : str):
  query = 'spells/'
  query += helper_functions.modify_query(arg)
  resource = helper_functions.get_resource(query)

  if resource == False:
    msg = '**Error:** The resource you were looking for could not be found.'
  else:
    msg = '__**' + resource.get('name') + '**__\n' \
          + '**Level: **' + str(resource.get('level')) + '\n' \
          + '**School: **' + resource.get('school').get('name') + '\n' \
          + '**Casting Time: **' + resource.get('casting_time') + '\n' \
          + '**Range: **' + resource.get('range') + '\n' \
          + '**Components: **' + ' '.join(resource.get('components')) + '\n\n' \
          + '\n'.join(resource.get('desc')) + '\n\n'
    if ('higher_level' in resource):
      msg += '***At Higher Levels. ***' + resource.get('higher_level')[0]

  # If the message is longer than the character limit Discord allows, split the message into two halves
  if len(msg) > 2000:          
    msg1, msg2 = helper_functions.split_msg(msg)
    await ctx.send(msg1)
    await ctx.send(msg2)
  else:
    await ctx.send(msg)

# Searches the D&D API for specified equipment
@bot.command(name='query-item')
async def query_item(ctx, *, arg: str):
  query = 'equipment/'
  query += helper_functions.modify_query(arg)
  resource = helper_functions.get_resource(query)

  if resource == False:
    msg = '**Error:** The resource you were looking for could not be found.'
  else:
    msg = '__**' + resource.get('name') + '**__\n' \
          + '*' + resource.get('equipment_category').get('name') + ', '

    # Customize the return message depending on the type of equipment the resource is
    # Armor and Shields
    if 'armor_category' in resource:
      msg += resource.get('armor_category') + '*\n' \
              + 'AC ' + str(resource.get('armor_class').get('base'))
      if (resource.get('armor_class').get('dex_bonus') == True):
        msg += ' + Dex'
      if (resource.get('armor_category') == 'Medium'):
        msg += ' (Max 2)'
      if (resource.get('str_minimum') > 0):
        msg += '\nMin Str ' + str(resource.get('str_minimum'))
      if (resource.get('stealth_disadvantage') == True):
        msg += '\nDisadvantage on Stealth rolls'

    # Weapons
    elif 'weapon_category' in resource:
      msg += resource.get('category_range') + '*\n' \
              + resource.get('damage').get('damage_dice') + ' ' \
              + resource.get('damage').get('damage_type').get('name') + '\n' \
              + 'Special Properties: '
      if len(resource.get('properties')):
        for x in resource.get('properties'):
          msg += x.get('name')
          if (x != resource.get('properties')[-1]):
            msg += ', '
      else:
        msg += '*None*'

    # Adventuring Gear & Misc
    else:
      msg += resource.get('gear_category').get('name') + '*'
      if 'desc' in resource:
        msg += '\n' + '\n'.join(resource.get('desc'))

      if 'contents' in resource:
        msg += '\nContents:'
        for x in (resource.get('contents')):
          msg += '\n- ' + x.get('item').get('name') + ' [' + str(x.get('quantity')) + ']'

    msg += '\n(Costs ' + str(resource.get('cost').get('quantity')) + ' ' \
            + resource.get('cost').get('unit') + ')'

  await ctx.send(msg)

# Searches the D&D API for specified magic items
@bot.command(name='query-magic-item')
async def query_magic_items(ctx, *, arg: str):
  query = 'magic-items/'
  query += helper_functions.modify_query(arg)
  resource = helper_functions.get_resource(query)

  if resource == False:
    msg = '**Error:** The resource you were looking for could not be found.'
  else:
    msg = '__**' + resource.get('name') + '**__\n' \
          + '\n'.join(resource.get('desc'))

  # If the message is longer than the character limit Discord allows, split the message into two halves
  if len(msg) > 2000:          
    msg1, msg2 = helper_functions.split_msg(msg)
    await ctx.send(msg1)
    await ctx.send(msg2)
  else:
    await ctx.send(msg)
  

bot.run(token)