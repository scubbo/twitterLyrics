#!/usr/bin/python
'''
Dependencies:
* python-twitter
'''
#import twitter
import os, os.path
import sys
import pickle
import random
#import urllib2
#import re
import time

sys.path.append(os.path.dirname(os.path.abspath(__file__)) + os.path.sep + os.path.pardir + os.path.sep + 'twitterbot')
import tb

os.chdir(os.path.dirname(os.path.abspath(__file__)))

class App:
	def __init__(self, twitterBot = None):
		'''gens is a dictionary of {name:instance of phraseGenerator}'''
		self.twitterBot = twitterBot
	
	def postUpdate(self):
		lyric = self.randomLyric() + ' PLEASE RT'
		self.twitterBot.api.PostUpdate(lyric)
		print 'Just posted "' + lyric + '"'

	def postReply(self, mention):
		recip = mention.user.screen_name
		if recip != "trexlyrics":
			lyric = self.randomLyric()
			while len(lyric) > 138 - len(recip):
				lyric = self.randomLyric()
			self.twitterBot.api.PostUpdate('@' + recip + ' ' + lyric)
			print '\n' + time.asctime() + ' In reply to ' + mention.text + '\n\tPosted ' + lyric

	def randomLyric(self):
		with file('lyrics', 'r') as f:
			return random.choice(pickle.load(f))

	
	def replyMentions(self):
		if os.path.exists('lastMention.file'):
			with file('lastMention.file', 'r') as f:
				lastMention = int(f.read())
				mentions = self.twitterBot.api.GetMentions(since_id=lastMention)
		else:
			mentions = self.twitterBot.api.GetMentions()
		if len(mentions) > 0:
			with file('lastMention.file', 'w') as f:
				f.write(str(mentions[0].id))
		for mention in mentions:
			print '\nDealing with ' + mention.text + ' from ' + mention.user.screen_name
			self.postReply(mention)
	
	def makeFriends(self):
		#First, befriend anyone you haven't already
		newFriends = [newFriend.screen_name for newFriend in self.twitterBot.api.GetFollowers() if newFriend not in self.twitterBot.api.GetFriends()]
		for newFriend in newFriends:
			try:
				self.twitterBot.api.CreateFriendship(newFriend)
				print '\nFollowed ' + newFriend
			except:
				print 'Tried to follow ' + newFriend + ', but there was an error. Perhaps they have a hidden profile?'
				
	def scanFriendTweets(self):
		if os.path.exists('lastSearch.file'):
			with file('lastSearch.file', 'r') as f:
				lastSearch = int(f.read())
		else:
			lastSearch = 0
		
		tweets = self.twitterBot.api.GetUserTimeline(since_id=lastSearch)
		
		for tweet in tweets:
			if self.findNumber(tweet.text) != False and self.findNumber(tweet.text) > 4 and reduce(lambda x, y: x or y, [word in tweet.text for word in self.interestWords]):
				self.postReply(tweet)
		
		ids = [tweet.id for tweet in tweets]
		ids.sort()
		
		if len(ids) > 0:
			with file('lastSearch.record', 'w') as f:
				f.write(str(ids[-1]))

def addLyric(lyricList):
	lyric = ' '.join(lyricList)
	if len(lyric) > 130:
		print 'Nope, no can do buster, it\'s too long (is what she said!)'
	else:
		with file('lyrics', 'r') as f:
			lyrics = pickle.load(f)
		with file('lyrics', 'w') as f:
			pickle.dump(lyrics + [lyric], f)

def listLyrics():
	with file('lyrics', 'r') as f:
		print pickle.load(f)

def usage():
	print """OK you doofus, listen up.
Here are some example usages:

twitterLyrics.py list
  -> lists the saved lyrics

twitterLyrics.py add "We all live in a yellow submarine"
  -> Adds the lyrics to the list
  (bit dodgy, this one. Best use the web interface)

twitterLyrics.py post
  -> Posts a lyric

twitterLyrics.py listen
  -> Check if anyone's mentioned me/you/us/whatever, and replies to them
	"""

def main():
	if len(sys.argv) == 1:
		usage()
		return
	if sys.argv[1] == 'add':
		addLyric(sys.argv[2:])
		return
	if sys.argv[1] == 'list':
		listLyrics()
		return
	theTB = tb.Twitterbot()
	theApp = App(theTB)
	if sys.argv[1] == 'post':
		theApp.postUpdate()
	if sys.argv[1] == 'listen':
		theApp.replyMentions()
		#theApp.scanFriendTweets()
	if sys.argv[1] == 'makeFriends':
		theApp.makeFriends()
	if sys.argv[1] == 'postTest':
		theApp.postUpdateTest()
			
	
if __name__ == '__main__':
	main()
