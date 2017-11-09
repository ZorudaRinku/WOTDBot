import schedule
import praw
import config
import time
import os #Used for making the .txt files of words
import re
from vocabulary.vocabulary import Vocabulary as vb
import datetime

# Made by reddit user /u/Stronger1088
# Feel free to use this without crediting me but if anyone asks please let them know of the original developer! (Yours truly)
# This is my second bot so I hope its good enough! I tried to rule out all of the bugs possible but there might still be some. Feel free to message me! Ty!

now = datetime.datetime.now()

def authentication():
	print ("Authenticating...")
	reddit = praw.Reddit(username = config.username,
			password = config.password,
			client_id = config.client_id,
			client_secret = config.client_secret,
			user_agent = "Stronger1088's WOTD bot for a /r/requestABot user.")
	print ("Authenticated as {}".format(reddit.user.me()))
	time.sleep(2)
	return reddit

def pick_word():
	with open("unused_words.txt", "r") as f:
		unused_words = f.read()
		unused_words = unused_words.split("\n")
		unused_words = list(filter(None, unused_words))

	word = unused_words[0]

	print ("Picked word: "+ word.title())
	return word

def use_word(word, unused_words, used_words):
	if word in unused_words: 
		unused_words.remove(word)

	with open('unused_words.txt', 'r+') as f:
		t = f.read()
		f.seek(0)
		for line in t.split('\n'):
			if line != word:
				f.write(line + '\n')
		f.truncate()

	if word not in used_words:
		used_words.append(word)
	with open ("used_words.txt", "a") as f:
		f.write(word + "\n")

	return unused_words, used_words

def run_bot(reddit):
	print ("Running...")
	word = (pick_word()).lower()
	deff = vb.meaning(word, format = "list")
	if deff is False or len(word) < config.minimum or len(word) > config.maximum:
		use_word(word, unused_words, used_words)
		deff = []
		print ("Could not find deffinition/didnt meet length requirements of '" + word.title() + "'. Finding another...")
		run_bot(reddit)
	else:
		print ("Found deffinition for '" + word.title() + "'. Posting...")
		string = "# Word of the day: " + word.title()
		for i in range(len(deff)):
			if i < config.ammount:
				string += "\n\n"
				string += str(i + 1)
				string += ": "
				reFormattedString = re.sub(r"\<.\>", "", deff[i])
				reFormattedString1 = re.sub(r"\[.\]", "", reFormattedString)
				reFormattedString2 = re.sub(r"\</.\>", "", reFormattedString1)
				reFormattedString3 = re.sub(r"\[/.\]", "", reFormattedString2)
				string += reFormattedString3
				i += 1

		string += config.message
		reddit.subreddit(config.subreddit).submit("Word Of The Day - " + now.strftime("%B %d, %Y") + " - " + word.title(), string)
		print ("Posted Successfully!")
		use_word(word, unused_words, used_words)
		print ("Next: " + str(unused_words[0]).title())
		print ("Waiting till " + config.time + "...")

def unused_words():
	if not os.path.isfile("unused_words.txt"):
		unused_words = []
		with open ("unused_words.txt", "w") as f:
			f.write("")
	else:
		with open("unused_words.txt", "r") as f:
			unused_words = f.read()
			unused_words = unused_words.split("\n")
			unused_words = list(filter(None, unused_words))

	return unused_words

def used_words():
	if not os.path.isfile("used_words.txt"):
		used_words = []
		with open ("used_words.txt", "w") as f:
			f.write("")
	else:
		with open ("used_words.txt", "r") as f:
			used_words = f.read()
			used_words = used_words.split("\n")
			used_words = list(filter(None, used_words))

	return used_words

reddit = authentication()
unused_words = (unused_words())
used_words = (used_words())
print ("Unused Words: " + str(unused_words))
print ("Used Words: " + str(used_words))
print ("Next: " + str(unused_words[0]).title())
schedule.every().day.at(config.time).do(run_bot, reddit)
print ("Waiting till " + config.time + "...")
#run_bot(reddit)

while True:
    schedule.run_pending()
    time.sleep(1)
