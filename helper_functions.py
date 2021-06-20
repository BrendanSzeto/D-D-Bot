import requests
import json
from random import randint

# Global variable for the url used in query commands
base_url = 'https://www.dnd5eapi.co/api/'

# Generate random numbers between 1 and the specified number of sides a number of times equal to the amount of dice
def roll_dice(amount, sides):
  results = []
  total = 0
  for i in range(amount):
    num = randint(1, sides)
    results.append(num)
    total += num
  return results, total

# Modifies an argument to fit the query search pattern
def modify_query(query):
    query = query.lower()
    query = query.replace(' ', '-')
    return query

# Checks if the request is valid, and returns the resulting resource if it is
def get_resource(query):
    url = base_url + query

    if (requests.get(url).status_code == 200):
        resource =  requests.get(url).json()
        return resource
    else:
        return False

# Splits a message into two halves by new lines (\n)
def split_msg(msg):
  mid = len(msg) // 2
  split_at = mid + min(-msg[mid::-1].index('\n'), msg[mid:].index('\n'), key=abs)
  return msg[:split_at], msg[split_at:]