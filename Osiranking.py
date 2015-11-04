#!/usr/bin/env python
import os
import sys
import time
import json
import gspread
from oauth2client.client import SignedJwtAssertionCredentials

def getSheet():
	json_key = json.load(open('./Jason.json'))
	scope = ['https://spreadsheets.google.com/feeds']
	credentials = SignedJwtAssertionCredentials(json_key['client_email'], json_key['private_key'], scope)
	gc = gspread.authorize(credentials)
	wks = gc.open("Osi Squash ranking (Responses)").sheet1
	values = wks.get_all_values()
	del values[0]
	return values

class Match(object):


	def __init__(self, win, loss, rating, time, num, beststring):
		self.win = win
		self.loss = loss
		self.ranking = rating
		self.time = time
		self.num = num
		self.beststring = beststring

	
	def info(self):
		return "| %s | %s +%2.1f | %s -%2.1f| %s |" %(self.time.split()[0], self.win.name, self.ranking, self.loss.name, self.ranking, self.beststring) 


class Player(object):

	
	def __init__(self, name, ranking):
		self.name = name
		self.ranking = ranking
		self.c = 10
		self.progress = []
		
	def win(self, other, date, multi, beststring):
		diff = self.ranking - other.ranking
		for i in ELO:
			if diff < i[0]:
				expected = last
				
				break
			last = i[1]

		old = self.ranking
		otherold = other.ranking

		change = 16*multi*(1-expected)
		self.ranking = old + change
		other.ranking = otherold - change
		

		dates = date.split(" ")
		self.progress.append(self.ranking-old)
		other.progress.append(other.ranking-otherold)
		matches.append(Match(self, other, change, date, multi, beststring))

	def winScore(self, other, date, scoreSelf, scoreOther):
		diff = self.ranking - other.ranking
		for i in ELO:
			if diff < i[0]:
				expected = last
				
				break
			last = i[1]

		old = self.ranking
		otherold = other.ranking

		numMatches = scoreSelf + scoreOther
		actual = float(scoreSelf) / float(scoreOther)

		change = 30*numMatches*(actual-expected)
		self.ranking = old + change
		other.ranking = otherold - change
		
		beststring = "" + str(scoreSelf) + " - " +  str(scoreOther)

		dates = date.split(" ")
		self.progress.append(self.ranking-old)
		other.progress.append(other.ranking-otherold)
		matches.append(Match(self, other, change, date, actual, beststring))


	def info(self):
		trend = 0
		pluss = ""
 		if len(self.progress) < 5:
 			trend = sum(self.progress)
 		else:
 			trend = sum(self.progress[-5:])
 		if trend >= 0:
 			pluss = "+"

		return "|%-18s | %4.1f | %s%-4.1f| %d |" %(self.name, self.ranking, pluss,trend, len(self.progress))




	def getName(self):
		return self.name
	def getRank(self):
		print "%4.1f" %self.ranking
		return "%4.1f" %self.ranking
	def getTrend(self):
		trend = 0
		pluss = ""
 		if len(self.progress) < 5:
 			trend = sum(self.progress)
 		else:
 			trend = sum(self.progress[-5:])
 		if trend >= 0:
 			pluss = "+"
 		return "%s%-4.1f" %(pluss, trend)


ELO = [[-100000, 0.03], [-400, 0.07],[-300, 0.16], [-200, 0.18], [-180, 0.21], 
		  [-160, 0.24], [-140, 0.27], [-120, 0.31], [-100, 0.34], 
		  [-80, 0.38], [-60, 0.42], [-40, 0.47], [-20, 0.5],[20,	0.53],[40,	0.58],[60,	0.62],[80,	0.66],[100,	0.69],
			[120,	0.73],[140,	0.76],[160,	0.79],[180,	0.82],[200,	0.84],
		[300,	0.93],[400, 0.97], [100000, 0.98]]



names = []
playerlist = []
resultlist = []
matches = []

values = getSheet()

for line in values:
	name1 = line[1].lower().title().strip()
	name2 = line[2].lower().title().strip()
	
	if name1 == name2:
		continue

	if name1 not in names:
		playerlist.append(Player(name1, 1600.))
		names.append(name1)
	if name2 not in names:
		playerlist.append(Player(name2, 1600.))
		names.append(name2)

	for player in playerlist:
		if player.name == name1:
			p1 = player
		if player.name == name2:
			p2 = player
	bestof = 0
	if line[6] == "":
		bestof = 1
		line[6] = "Best of 1"
		p1.win(p2, line[0], bestof, line[6])
	elif line[6] == "Best of 1":
		p1.win(p2, line[0], bestof, line[6])
		bestof = 1
	elif line[6] == "Best of 3":
		bestof = 1.5
		p1.win(p2, line[0], bestof, line[6])
	elif line[6] == "Best of 5":
		bestof = 2
		p1.win(p2, line[0], bestof, line[6])
	elif line[6] == "Best of 7":
		bestof = 2.5
		p1.win(p2, line[0], bestof, line[6])
	elif line[6] == "Best of 9":
		bestof = 3
		p1.win(p2, line[0], bestof, line[6])
	else:
		p1.winScore(p2, line[0], int(line[6]), int(line[7]))
	
	
	

playerlist.sort(key=lambda x: x.ranking, reverse=True)

date = time.strftime("%d.%m.%Y %H:%M")

README = open("./README.md", "w")

README.write("###OSI Squash ranking %s\n" %date)
README.write("Trend = ranting change last 5 matches\n\n")

README.write("#####Current ratings\n")
README.write("|Name:              |Rank:   |Trend: |Total  |\n")
README.write("|:------------------|:-------|:------|:------|\n")
for player in playerlist:
	README.write(player.info()+ "\n")

README.write("\n#####Last 100 matches\n")
README.write("|Date:              |Win:   |Loss: |Length| \n")
README.write("|:------------------|:-------|:------|:------|\n")

match_print = 100
if len(matches) < 100:
	match_print = len(matches)


for i in range(1, match_print+1):
	README.write(matches[-i].info()+ "\n")


README.close()

