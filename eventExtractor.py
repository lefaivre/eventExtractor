#-------------------------------------------------------------------------------------------------
# Adam Lefaivre - 001145679
# CPSC 5310 - Dr. Yllias Chali
# Programming Portion Assn. 3 - Scheduling classifier and email/date/time extractor
#-------------------------------------------------------------------------------------------------
from nltk import word_tokenize
from nltk import WordNetLemmatizer
from nltk import NaiveBayesClassifier
from nltk import classify
from nltk import pos_tag
from nltk import sent_tokenize
from nltk import word_tokenize
from nltk.corpus import stopwords
from nltk import RegexpParser
import random
from random import randint
import os
import glob
import re
from nltk import tree
import shutil
import ntpath

# Some helpful globals
infoTypes = ["LOCATION", "DATE", "TIME_START", "TIME_END", "EVENT"]
meals = ["breakfast", "brunch", "lunch", "dinner", "supper", "dessert"]

# My program is designed so that you can easily check for things like "wedding" or "shower" or "graduation"
# given that they are tagged as nouns.  For the time being, these words are enough! :)
# (feel free to mess with the helpfulWords list and emails to see if it shows up under EXTRA_DATE_INFO)
helpfulWords = ["this", "next", "tomorrow", "tonight", "evening",
                "morning", "autumn", "fall", "spring", "winter",
                "afternoon", "dawn", "dusk", "later", "soon", "weekend",
                "twilight", "whenever", "night", "sunset", "sunrise" "daytime",
                "daybreak", "nightfall", "monday", "tuesday", "wednesday",
                "thursday", "friday", "saturday", "sunday", "month",
                "week", "year", "day", "soonish", "monthly", "weekly", "annually",
                "daily", "occasional", "perennial", "hourly", "january", "february",
                "march", "april", "may", "june", "july", "august", "september",
                "october", "november", "december"]

# A simple regex for times, just for double checking if the tagger didn't pick up on times
numbers = "(one|two|three|four|five|six|seven|eight|nine|ten| \
          eleven|twelve|thirteen|fourteen|fifteen|sixteen|seventeen| \
          eighteen|nineteen|twenty|thirty|forty|fifty|sixty|seventy|eighty| \
          ninety|hundred|thousand|noon|midnight)"
timeExpression = re.compile("((2[0-3](:)?[0-5][0-9]|[0-1][0-9](:)?[0-5][0-9]|24(:)?00)" + "|(" + numbers + ")+)")

# Random list of lists for file randomized file changes on corpus generation!
# I included the original string that I wish to change in every 0th position of every sub list for easier replacement
scheduler1Changes = [["Hello", "Hi", "Greetings"],
                     ["curriculum meeting", "production meeting", "doctor's appointment", "lunch meeting"],
                     ["in room D635", "on the Golden Gate bridge", "in room D701", "in the Blue Room", "in Pops West"],
                     ["from 12:00 to 12:50", "from 1 to 3", "from 8am and will probably go to 9"]]
scheduler2Changes = [["Hi John", "Hi Bud", "Oi John", "Greetings Joe"],
                     ["lunch", "dinner", "brunch", "breakfast"], ["from 12:30 to 1:00 pm", "from noon to 1", "8 to 9"],
                     ["Penny Coffee House", "Bar A Star Search", "Cool Cafe", "Triptykon's Diner"],
                     ["March 20th", "June 21st", "Saturday March 1st", "Wednesday, June 8th, 1991"],
                     ["in the afternoon", "next evening", "tomorrow morning"],
                     ["Thanks", "Regards", "Cheers"]]
scheduler3Changes = [["Hi John", "Hi Jake Gyllenhall", "Hi Mark Cuban", "Hello Emma Stone"],
                     ["at 12:45 pm and goes to 1:30pm", "from noon to 1:30pm", "from 1 to 2"],
                     ["We're going to be at Streetside Eatery", "We'll be having lunch at the Zoo",
                      "Hope to see you at the Watertower"],
                     ["on 12/12/1991", "soon, maybe, July 8th?"],
                     ["tomorrow evening", "next weekend", "soonish"]]
scheduler4Changes = [["beers", "Big George's tequila shots", "dinner", "gifts", "Guinness beer"],
                     ["for everyone", "for you and your friends", "for our cpsc4310 class"],
                     ["in the Zoo, at the University", "at Backstreet, on the Westside", "on campus, at the Zoo"],
                     ["so I'll be there at 8pm", "so, I think maybe I will be there at seven"],
                     ["4 am or something!", "4 am", "4 o'clock", "4", "four"],
                     ["hahahaha", "I sure hope to see you there!", "See you guys soon"]]
scheduler5Changes = [["dinner friday night", "brunch saturday", "dinner tomorrow", "an evening supper"],
                     ["February 10th", "January 2nd", "March 3rd"],
                     ["six to eight", "noon to two"], ["reschedule", "do this to you", "let you down like this"],
                     ["We should go eat at Sushi Supreme", "We should have a fancy dinner somewhere in Downtown Lethbridge"],
                     ["Mark Cuban", "Stressed out Boyfriend", "Crappy Person", "A sad man"]]
scheduler6Changes = [["We have", "We've got", "Hi, remember that we have", "Hey, we've"],
                     ["in the lounge", "in the classroom", "by the classroom"],
                     ["curriculum matters", "doctor's results", "jam"]]
scheduler7Changes = [["I am going to go", "I will be driving", "I will leave to go", "I'll be headed"],
                     ["Calgary", "Amsterdam", "Vietnam"],
                     ["to meet with my folks", "to have a meeting"],
                     ["6:00", "six", "seven", "6"]]

# This scheduling email really shows off the capability of my POS tagging functionality (I'm such a nerd...)
scheduler8Changes = [["deforestation meeting", "tea party", "cake eating contest", "dance party", "gaming convention"],
                     ["at the lodge", "at the club", "at Buckingham's Palace", "at McDonald's", "at the arcade"]]
scheduler9Changes = [["to have a discussion", "to talk", "to converse", "to speak to you"],
                     ["the impending doom of a certain superhero.", "various matters of concern", "my toothache"],
                     ["in the laboratory", "across the street", "in D631"]]
scheduler10Changes = [["I really need to see you", "I really want to see you", "I am sure I am going to see you"],
                      ["I want to see a movie with you", "I want to go on a picnic", "We are going for ice cream",
                       "We are going to go and watch a movie"],
                      ["movie called", "place named", "area known as"]]

nonScheduler1Changes = [["Hey man", "Hey Dude", "Hey Sister", "Hey bro", "sup Dude"],
                        ["How are things", "What's shakin", "What's good", "How do ya do", "Whatsup"],
                        ["check up on you", "see how things are going", "ask what's going on with you",
                         "express my interest"],
                        ["sad lately", "happy a lot", "running low on energy", "having a hard time"]]
nonScheduler2Changes = [["Hey man,", "Yo!!!!", "Hey pal,"],
                        ["I am getting hungry", "I am absolutely starving", "emaciated and dying"],
                        ["eat soon", "have some food right away", "have a whole lot of food", "get good food to eat"],
                        ["Sincerely", "Regards", "Peace", "ttyl", "Thanks", "Cheers"],
                        ["Hungry man", "Mark Cuban", "A sad man", "Hungry Joe", "Hungry Bob", "Joe"]]
nonScheduler3Changes = [["Yllias", "John", "Hua", "Mark Cuban", "Jake Gyllenhall", "Wendy", "Howard"],
                        ["where to find the corpus", "where I should get the corpus from"],
                        ["I can't seem to find any dataset online for email scheduling", "I can't find anything I need",
                         "I just can't seem to find any good data out there", "I need the correct data for this task"],
                        ["nltk's corpora", "Joe's dataset", "A Sad Man's Corpora", "anywhere that I could find"]]
nonScheduler4Changes = [["No worries Thanx", "No problem, thank you", "No issue at all, thanks for that",
                         "No sweat, thanks by the way"],
                        ["How was test", "How well did you perform on your exam", "what grade did you get on your quiz",
                         "I don't think you did too good on that NLP midterm, you probably failed, didn't you"],
                        ["Heart Dad", "See ya later gator", "Heart Mom", "Savage friend", "Troll"]]
nonScheduler5Changes = [["Hey Wendy", "Hi Buddy Guy", "Hi BB King", "Hey there Muddy Waters", "Hi Blues dude"],
                        ["Okay, no problem", "Okay, no issue, trust me", "K, no worries"],
                        ['power point', "slides", "presentation"],
                        ["fine", "dandy", "good by me", "totally okay", "cool", "great"],
                        ["whatever format I need", "be whatever way I need", "however I need", "make it how I want"],
                        ["Thanks", "Sincerely", "Regards", "Peace", "ttyl", "Cheers"]]
nonScheduler6Changes = [["Okay will do", "Okay, I shall do this", "I'll Make sure Emma Stone does this", "I got this"],
                        ["make extra sure to", "definitely ensure that I will", "double check"]]
nonScheduler7Changes = [["Hi Lazima", "Hello Adam", "Hello my fellow Rafael"],
                        ["am uploading", "have written", "started writing", "finished making"],
                        ["one you have downloaded", "most recent version", "latest update"],
                        ["this mistake", "the change that needed to be made", "that ammendment"],
                        ["Nicole", "Emma Stone", "Mark Cuban", "Professor Charles Xavier", "Logan"]]
nonScheduler8Changes = [["C++", "Python", "Java", "Scheme", "Prolog", "Cobal"],
                        ["Hahaha", "Hope to see you there!", "See you guys soon"],
                        ["improve on", "modify", "change up"],
                        ["purists", "Adam", "the Toronto Blue Jays", "my fellow Americans"]]
nonScheduler9Changes = [["Hey Tom", "Hello Emma Stone", "Hi Magneto", "Good day Logan"],
                        ["cracked open", "opened", "had a look at", "observed", "checked out"],
                        ["talk to", "discuss this with", "make sure to mention it to"],
                        ["John", "Mark Cuban", "Logan"]]
nonScheduler10Changes = [["Homie", "my dearest friend", "my compadre", "Mulan", "Mr. Silly-Man",
                          "my good friend from around the same location"],
                          ["Whatsup", "How are you doing on this fine day", "What is new with you magoo",
                           "How is NLP going for you"]]

def generateCorpus():

    # Get generator files
    listOfSchedulingGenerators = glob.glob(parentPath + '/generatorFiles/scheduling/*.txt')
    listOfNonSchedulingGenerators = glob.glob(parentPath + '/generatorFiles/nonScheduling/*.txt')

    schedulingPath = parentPath + "/scheduling/"
    nonSchedulingPath = parentPath + "/nonScheduling/"

    # Create folders for corpus containment, if they already exist
    # trash them and restart to get newly generated emails
    if not os.path.exists(schedulingPath):
        os.makedirs(schedulingPath)
    else:
        shutil.rmtree(schedulingPath)
        os.makedirs(schedulingPath)
    if not os.path.exists(nonSchedulingPath):
        os.makedirs(nonSchedulingPath)
    else:
        shutil.rmtree(nonSchedulingPath)
        os.makedirs(nonSchedulingPath)

    # Begin populating scheduling files
    if not os.listdir(schedulingPath):
        counter = 1
        for generatorPath in listOfSchedulingGenerators:
            contentsOfNewFile = open(generatorPath, 'r').read()
            fileName = ntpath.basename(generatorPath)
            for i in range(0, 500):
                if "1" in fileName:
                    for change in scheduler1Changes:
                        rand = randint(0, len(change) - 1)
                        contentsOfNewFile = contentsOfNewFile.replace(change[0], change[rand])
                elif "2" in fileName:
                    for change in scheduler2Changes:
                        rand = randint(0, len(change) - 1)
                        contentsOfNewFile = contentsOfNewFile.replace(change[0], change[rand])
                elif "3" in fileName:
                    for change in scheduler3Changes:
                        rand = randint(0, len(change) - 1)
                        contentsOfNewFile = contentsOfNewFile.replace(change[0], change[rand])
                elif "4" in fileName:
                    for change in scheduler4Changes:
                        rand = randint(0, len(change) - 1)
                        contentsOfNewFile = contentsOfNewFile.replace(change[0], change[rand])
                elif "5" in fileName:
                    for change in scheduler5Changes:
                        rand = randint(0, len(change) - 1)
                        contentsOfNewFile = contentsOfNewFile.replace(change[0], change[rand])
                elif "6" in fileName:
                    for change in scheduler6Changes:
                        rand = randint(0, len(change) - 1)
                        contentsOfNewFile = contentsOfNewFile.replace(change[0], change[rand])
                elif "7" in fileName:
                    for change in scheduler7Changes:
                        rand = randint(0, len(change) - 1)
                        contentsOfNewFile = contentsOfNewFile.replace(change[0], change[rand])
                elif "8" in fileName:
                    for change in scheduler8Changes:
                        rand = randint(0, len(change) - 1)
                        contentsOfNewFile = contentsOfNewFile.replace(change[0], change[rand])
                elif "9" in fileName:
                    for change in scheduler9Changes:
                        rand = randint(0, len(change) - 1)
                        contentsOfNewFile = contentsOfNewFile.replace(change[0], change[rand])
                elif "0" in fileName:
                    for change in scheduler10Changes:
                        rand = randint(0, len(change) - 1)
                        contentsOfNewFile = contentsOfNewFile.replace(change[0], change[rand])

                newSchedulingFile = schedulingPath + "scheduling" + str(counter) + ".txt"
                text_file = open(newSchedulingFile, "w")
                text_file.write(contentsOfNewFile)
                text_file.close()
                counter = counter + 1

    # Begin populating scheduling files
    if not os.listdir(nonSchedulingPath):
        counter = 1
        for generatorPath in listOfNonSchedulingGenerators:
            contentsOfNewFile = open(generatorPath, 'r').read()
            fileName = ntpath.basename(generatorPath)
            for i in range(0, 500):
                if "1" in fileName:
                    for change in nonScheduler1Changes:
                        rand = randint(0, len(change)- 1)
                        contentsOfNewFile = contentsOfNewFile.replace(change[0], change[rand])
                elif "2" in fileName:
                    for change in nonScheduler2Changes:
                        rand = randint(0, len(change)- 1)
                        contentsOfNewFile = contentsOfNewFile.replace(change[0], change[rand])
                elif "3" in fileName:
                    for change in nonScheduler3Changes:
                        rand = randint(0, len(change)- 1)
                        contentsOfNewFile = contentsOfNewFile.replace(change[0], change[rand])
                elif "4" in fileName:
                    for change in nonScheduler4Changes:
                        rand = randint(0, len(change)- 1)
                        contentsOfNewFile = contentsOfNewFile.replace(change[0], change[rand])
                elif "5" in fileName:
                    for change in nonScheduler5Changes:
                        rand = randint(0, len(change)- 1)
                        contentsOfNewFile = contentsOfNewFile.replace(change[0], change[rand])
                elif "6" in fileName:
                    for change in nonScheduler6Changes:
                        rand = randint(0, len(change)- 1)
                        contentsOfNewFile = contentsOfNewFile.replace(change[0], change[rand])
                elif "7" in fileName:
                    for change in nonScheduler7Changes:
                        rand = randint(0, len(change)- 1)
                        contentsOfNewFile = contentsOfNewFile.replace(change[0], change[rand])
                elif "8" in fileName:
                    for change in nonScheduler8Changes:
                        rand = randint(0, len(change)- 1)
                        contentsOfNewFile = contentsOfNewFile.replace(change[0], change[rand])
                elif "9" in fileName:
                    for change in nonScheduler9Changes:
                        rand = randint(0, len(change)- 1)
                        contentsOfNewFile = contentsOfNewFile.replace(change[0], change[rand])
                elif "0" in fileName:
                    for change in nonScheduler10Changes:
                        rand = randint(0, len(change)- 1)
                        contentsOfNewFile = contentsOfNewFile.replace(change[0], change[rand])


                newNonSchedulingFile = nonSchedulingPath + "nonScheduling" + str(counter) + ".txt"
                text_file = open(newNonSchedulingFile, "w")
                text_file.write(contentsOfNewFile)
                text_file.close()
                counter = counter + 1


def getListOfData(parseTree):
    #Iterate through elements if the popped element is a tree
    #Then parse further and get data from it
    listOfInfo = []
    tag = parseTree.pop()
    while(tag):
        if (type(tag) is tree.Tree):

            #okay we know it is an inner tree now. Check to see which one it is...LOCATION, DATE, TIME_START, TIME_END, EVENT
            #once we know that then append the children to form the info to return

            stringToForm = ""
            for infoType in infoTypes:
                if infoType in str(tag):
                    firstIter = True
                    tag = tree.Tree.flatten(tag)
                    for childNode in tag:
                        if firstIter:
                            stringToForm += infoType
                            firstIter = False
                            stringToForm += ": "
                        stringToForm += childNode[0]
                        stringToForm += " "
                    stringToForm = stringToForm.rstrip()
                    listOfInfo.append(stringToForm)
                    break
        try:
            tag = parseTree.pop()
        except:
            break

    # So now our list of info should include "LOCATION", "DATE", "TIME_START", "TIME_END", and "EVENT"
    # However, if the tagger didn't work (which is often the case), then we should check
    # if the list only contains the infoType "DATES" and has more than one match, then we must use a regex to
    # check and see if "tomorrow", "evening", etc. are matched and give that as additional date information!

    flag = True
    for info in listOfInfo:
        if "DATE" not in info:
            flag = False
            break

    # Now use the following simple algorithm for catching:
    # DATE1 for "tonight", "tomorrow night", "this afternoon", "this evening", etc.
    # DATE2 for catching things like "friday night" or "thursday night" where the day isn't capitalized and thus is JJ
    # DATE3 for "the evening time" or something like that.
    # DATE4 for "this Friday"

    # Note: Regex wasn't necessary to catch this extra data here, however it was used for time information later on!
    if(flag):
        newList = []
        extraDateInfoString = ""
        for info in listOfInfo:
            info = info.replace("DATE: ", "")
            words = info.split()
            for word in words:
                if word.lower() in helpfulWords:
                    extraDateInfoString += word
                    extraDateInfoString += " "
            if(not ((extraDateInfoString == "this") or (extraDateInfoString == "next") or (extraDateInfoString == "next ") or (extraDateInfoString == "this "))):
                if(not (extraDateInfoString == "")):
                    extraDateInfoString = extraDateInfoString.rstrip()
                    newList.append("EXTRA_DATE: " + extraDateInfoString)
                    extraDateInfoString = ""
        listOfInfo = newList

    # And return the info we found.
    return listOfInfo

# This function is just used to extract the time from the email using a regular expression as well.
# It is only using in the case that the tagger fails.
def doubleCheckStartAndEndTimesUsingRegex(rawTokens):
    times = []
    for token in rawTokens[0]:
        result = timeExpression.match(token)
        if(result):
            times.append(result.group())

    times = sorted(times)
    if(len(times) == 2):
        return times[0], times[1]
    else:
        return "", ""

def tryToFindTheOtherTime(rawTokens, timeFoundByTagger):
    times = []
    taggerTime = re.findall(timeExpression, timeFoundByTagger)
    for token in rawTokens[0]:
        result = timeExpression.match(token)
        if(result):
            times.append(result.group())

    # We can only return the other time value with uncertainty if the value is greater than 2
    if(len(times) >= 2):
        for time in times:
            if (not (time == taggerTime)):
                return time
    elif (len(times) == 1):
        if(not (times[0] == taggerTime)):
            return times[0]
    else:
        return ""

def cleanTaggedExpressions(overallParseTree, dateNounParseTree, eventParseTree, rawTokens ,rawEmailString):

    timeStart = ""
    timeEnd = ""
    location = ""
    date = ""
    event = ""

    listOfOverallInfo = getListOfData(overallParseTree)
    listOfDateNounInfo = getListOfData(dateNounParseTree)
    listOfEventInfo = getListOfData(eventParseTree)

    # Here give priority to meals, like "breakfast" etc.
    eventFoundAlready = False
    if (len(listOfEventInfo) > 1):
        for eventIter in listOfEventInfo:
            eventIter = eventIter.replace('EVENT: ', '')
            if eventIter in meals:
                eventFoundAlready = True
                event = 'EVENT: ' + eventIter


    for item in listOfOverallInfo:
        if "TIME_START" in item:
            if timeStart == "":
                timeStart = item
        elif "TIME_END" in item:
            timeEnd = item
        elif "LOCATION" in item:
            location = item
        elif "DATE" in item:
            date = item


    # Now return the first catch w.r.t. the email.  Relying on the fact that the event is normally within the
    # first noun phrase in the email.
    # Also, I am using a ratio:
    #       loc = (location of NP in raw email string)
    #       count = (# of words in NP)
    #       ratio: loc/(3^count)
    # The value with the lowest result gets chosen as the event.
    # Therefore, if the location is 0, then it is automatically chosen.

    currMaxRatio = len(rawEmailString)
    newEventPos = 0
    if ((not eventFoundAlready) and (not (len(listOfEventInfo) == 0))):
        for item in listOfEventInfo:
            itemsLocation = 0
            tempItem = item.replace('EVENT: ', '')
            itemsLocation = rawEmailString.find(tempItem)
            numItems = len(tempItem.split())
            nextMaxRatio = itemsLocation/pow(3, numItems)
            if (nextMaxRatio < currMaxRatio):
                currMaxRatio = nextMaxRatio
                newEventPos = listOfEventInfo.index(item)
        event = listOfEventInfo[newEventPos]

    # If there is no result at all returned for the start and end times, try using a regex to capture the times.
    # If regex couldn't find precisely 2 times either...well then we are S.O.L. so just ignore the start and end times.
    if (timeStart == "" and timeEnd == ""):
        timeStart, timeEnd = doubleCheckStartAndEndTimesUsingRegex(rawTokens)
        if (timeStart == "" and timeEnd == ""):
            listOfOverallInfo.append("TIME_START: undetermined")
            listOfOverallInfo.append("TIME_END: undetermined")
        else:
            listOfOverallInfo.append("TIME_START: " + timeStart)
            listOfOverallInfo.append("TIME_END: " + timeEnd)

    elif(timeStart == "" and (not(timeEnd == ""))):
        timeStart = tryToFindTheOtherTime(rawTokens, timeEnd)
        if (timeStart == ""):
            listOfOverallInfo.append("TIME_START: undetermined")
        else:
            listOfOverallInfo.append("TIME_START: " + timeStart)


    elif(timeEnd == "" and (not (timeStart == ""))):
        timeEnd = tryToFindTheOtherTime(rawTokens, timeStart)
        if (timeEnd == ""):
            listOfOverallInfo.append("TIME_END: undetermined")
        else:
            listOfOverallInfo.append("TIME_END: " + timeEnd)

    #If the tagger couldn't find the location, date, or event, then just return undetermined.
    if(date == ""):
        listOfOverallInfo.append("DATE: undetermined")
    if(location == ""):
        listOfOverallInfo.append("LOCATION: undetermined")
    if (event == ""):
        listOfOverallInfo.append("EVENT: undetermined")
    elif (not(event =="")):
        listOfOverallInfo.append(event)

    # Still make sure to return extra date info if it is found, as well as EVENT INFORMATION!!!!!!!!!
    listOfOverallInfo.extend(listOfDateNounInfo)

    return listOfOverallInfo


# A function that does the heavy lifting of extracting the date, time, location, and event of a tester email as input
def taggerAndResultBuilder(emailInput):

    #Use a sent tokenizer (to maintain things like colons, for times, etc.)
    sentences = sent_tokenize(emailInput)
    sentencesBeforeTagging = [word_tokenize(sent) for sent in sentences]
    sentences = [pos_tag(sent) for sent in sentencesBeforeTagging]



    # This was the best that I could possibly come up with given the time I had.

    overallGrammar = """
        CLAUSE0: {<IN>?<NNP>+<CD><CD>?}
    	CLAUSE1: {<DT><CD>}
    	DATE: {<CLAUSE0|CLAUSE1>}
    	CLAUSE2: {<VBZ>?<TO><CD><CC|NN|VBP|VBZ>?}
    	CLAUSE3: {<IN|VB><RB><CD|IN><CD>?<NN|NNS>}
    	CLAUSE4: {<IN><IN><CD><NN>?}
    	TIME_END: {<CLAUSE2|CLAUSE3|CLAUSE4>}
    	CLAUSE5: {<IN><DT>?<NN>*<NNP>+<NNPS>*<NN>?}
    	CLAUSE6: {<IN><DT><NN>}
    	CLAUSE7: {<TO><NNP>}
        LOCATION: {<CLAUSE5|CLAUSE6|CLAUSE7>}
        TIME_START: {<CD><NN|VBP|VBZ>?}
    	"""


    #	DA1: {<IN>?<NNP>+<CD><CD>?}
    #	DA2: {<DT><CD>}
    #	DATE: {<DA1|DA2>}
    #	TE3: {<IN><RB><CD><NN|NNS>}
    #	TE4: {<VB><RB><IN><CD>}
    #	TIME_END: {<TE1|TE2|TE3|TE4>}
    #	TS1: {<CD><NN|VBP|VBZ>?}
    #	TS2: {<VBZ><IN><CD>}
    #	TIME_START: {TS1|TS2}
    #   L1: {<IN><DT>?<NN>*<NNP>+<NNPS>*<NN>?}
    #    L2: {<IN><DT><NN>}
    #    L3: {<TO><NNP>}
    #    LOCATION: {<L1|L2|L3>}
    # 	"""


    # Location has an optional noun at the end in case the word "building" or "place" or something like this is included.

    # So in the off case that someone enters "am" instead of "A.M." then this
    # can actually be mistaken as a verb that's why there are the cases for
    # VBP and VBZ in TIME_START

    # Get grammar for nouns like "tonight", "tomorrow", "this afternoon", "this evening", etc.
    # And check to see if these nouns exist.  If they do then compare against the overall grammar
    # If there is no date then record these
    dateNounGrammar = """
        DATE1: {<JJ><NN>+}
        DATE2: {<DT><NN>+}
        DATE3: {<DT><NNP>+}
        DATE4: {<DT|JJ|NN><VBG>}
        DATE5: {<NN>+}
        DATE6: {<JJ><NNP>}
        """

    # DATE1 for catching things like "friday night" or "thursday night" where the day isn't capitalized and thus is JJ
    # DATE2 for "the evening time" or something like that.
    # DATE3 for "this Friday" (the tagger messes up the classification of capitalized days, etc.)
    # DATE4 for "this evening", or "(t/T)hursday evening"
    # DATE5 for "tonight", "tomorrow night", "this afternoon", "this evening", "lunch", "dinner", etc.
    # DATE6 for "this Friday", etc.

    # -----------------------------------------------------------------------------------------------------------
    # -----------------------------------------------------------------------------------------------------------
    #
    # This is now the Grammar that will be used to extract events.
    # Keep in mind that it is often the first noun in the scheduling email that will be found
    # This is a known fact in information extraction.
    #
    # For example see:
    # http://www.iosrjournals.org/iosr-jce/papers/Conf-%20ICFTE%E2%80%9916/Volume-1/12.%2072-79.pdf?id=7557
    #
    # I was also able to come up with a grammar based on all of the random sentences I generate.
    #
    # -----------------------------------------------------------------------------------------------------------
    # -----------------------------------------------------------------------------------------------------------

    eventGrammar = """
        EVENT1: {<DT><NN><VBG><NN>}
        EVENT2: {<DT|VBG><NN>+}
        EVENT3: {<VB|VBG><IN><NN>+}
        EVENT4: {<VBG|VBP><NNP>?<NNS>}
        EVENT5: {<NNS><VBP>}
        EVENT6: {<VB><NN|RP>}
        EVENT7: {<VB><DT><NN>}
        EVENT8: {<DT><NN><VBG><NN>}
        EVENT9: {<NN>}
        """
    # EVENT1 for "a cake eating contest
    # EVENT2 for "having lunch" or "a meeting", or "curriculum meeting" etc.
    # EVENT3 for "wrestling in space" or "wrestle in space" or "going for ice cream" , etc.
    # EVENT4 for things like "buying Guinness beer"
    # EVENT5 for "doctor's appointment"
    # EVENT6 for "drive home" or "run away"
    # EVENT7 for "running the tap"
    # EVENT8 for "lunch" or "dinner", etc.This is last because the other POS sequences should have priority.
    # EVENT9 for pretty much everything else that could be valid.


    # Extra location grammar


    # file_object = open( homeDirectory+ "testerDataOutput.txt", "a")
    dateTimeLocationAndEventList = []
    parser1 = RegexpParser(overallGrammar)
    parser2 = RegexpParser(dateNounGrammar)
    parser3 = RegexpParser(eventGrammar)
    for sentence in sentences:
        result1 = parser1.parse(sentence)
        result2 = parser2.parse(sentence)
        result3 = parser3.parse(sentence)
        dateTimeLocationAndEventResult = cleanTaggedExpressions(result1, result2, result3, sentencesBeforeTagging, emailInput)
        dateTimeLocationAndEventList.append(dateTimeLocationAndEventResult)

    resultString = ""
    for result in dateTimeLocationAndEventList:
        for iter in result:
            if ("undetermined" not in iter) and (iter not in resultString):
                resultString += iter
                resultString += ", "
    for info in infoTypes:
        if info not in resultString:
            resultString += info + ": undetermined"
            resultString += ", "

    resultString = resultString.rstrip(" ")
    resultString = resultString.lstrip(" ")
    resultString = resultString.rstrip(",")
    resultString = resultString.lstrip(",")

    # So if multiple dates were found by the tagger then just offer
    # The other date as additional info, this ultimately makes the program more robust!
    # Forget about checking times, because this is already double checked by regex!
    for info in infoTypes:
        if(info == 'DATE'):
            checkerInfo = info + ":"
            count = resultString.count(info)
            if(count > 1):
                newString = resultString.rsplit(info, resultString.count(info) - 1)
                new = info + "_ADDITIONAL_INFO_FOUND"
                resultString = new.join(newString)

    return resultString


# A function to check for all non-stop words (like 'the', 'is', etc.) given an input email as a string
# The function returns feature words that are important for the classification
def getFeatures(emailAsInputString):
    # get all of the stop words as a set (i.e. remove any duplicate stop words, if need be)
    stopWords = set(stopwords.words('english'))

    # Declare a lemmatizer so that the input string can be lemmatized
    # Here we are using the word net lemmatizer which is based on the word net corpora
    lemmatizer = WordNetLemmatizer()

    # Now lemmatize the tokens from the email
    wordtokens = []
    wordTokenizationResult = word_tokenize(emailAsInputString)
    for word in wordTokenizationResult:
        wordtokens.append(lemmatizer.lemmatize(word.lower()))

    # Now loop through the potential non-stop words to check to see if they
    # are actually non-stop words. If they are in fact non-stop words
    # then we can make return a dictionary with each value for that word
    # as true, meaning that yes, it is a non-stop word
    dictToReturn = {}
    for word in wordtokens:
        if word not in stopWords:
            # Assign the value true if the word is not a stop word
            dictToReturn[word] = True
    return dictToReturn


# Beggining of the main portion of this program:

# If the folder is not there ask the user to give the path for it.
# Also check for scheduling & non-scheduling folders too!
print ("This program uses emails based on the scheduling email supplied by the question")
print("Now loading in the generator emails that were supposed to be in the .tar submission file.")
parentPath = os.path.abspath(os.path.join(os.path.realpath(__file__), os.pardir))
schedulingPath = parentPath

if (not os.path.isdir(schedulingPath +"/generatorFiles")):
    print "For some reason the generatorFiles folder cannot be found"
    print "Please ensure this path exists, and make place some scheduling/non-scheduling emails in this path:",\
        parentPath + "/generatorFiles/"
    print "Exiting.  Please try this program again with the template emails in the right directory!"
    exit()

if (not os.path.isdir(schedulingPath +"/generatorFiles/scheduling")):
    print "For some reason the generatorFiles/scheduling folder cannot be found"
    print "Please ensure this path exists, and make place some scheduling email templates in this path:",\
        parentPath + "/generatorFiles/scheduling/"
    print "Exiting.  Please try this program again with the scheduling emails in the right directory!"
    exit()

if (not os.path.isdir(schedulingPath +"/generatorFiles/nonScheduling")):
    print "For some reason the generatorFiles/nonScheduling folder cannot be found"
    print "Please ensure this path exists, and make place some nonScheduling email templates in this path:",\
        parentPath + "/generatorFiles/nonScheduling/"
    print "Exiting.  Please try this program again with the nonScheduling emails in the right directory!"
    exit()

#Programmatically generate files
print("Generating scheduling and non-scheduling emails.")
generateCorpus()

# Declare lists for the two different types of emails
schedEmails = [] # scheduling emails
nonSchedEmails = [] # non-scheduling emails

print("Acquiring the generated scheduling/non-scheduling emails from corpora")
# We must now get all of the nonScheduling emails using glob.
for emailFile in glob.glob(os.path.join(schedulingPath + '/nonScheduling/' + '*.txt')):
    # Open this file and append its contents to the realEmails list declared above
    # Strip away all punctuation
    fileToBeRead = open(emailFile, "r")
    stringFromFileToBeAppended = fileToBeRead.read()
    stringFromFileToBeAppended = re.sub("[^a-zA-Z\d\s]+", "", stringFromFileToBeAppended)
    nonSchedEmails.append(stringFromFileToBeAppended)
    fileToBeRead.close()

# We must now get all of the scheduling emails using glob.
for emailFile in glob.glob(os.path.join(schedulingPath + '/scheduling/' + '*.txt')):
    # Open this file and append its contents to the scheduling list declared above
    # Strip away all punctuation
    fileToBeRead = open(emailFile, "r")
    stringFromFileToBeAppended = fileToBeRead.read()
    stringFromFileToBeAppended = re.sub("[^a-zA-Z\d\s]+", "", stringFromFileToBeAppended)
    schedEmails.append(stringFromFileToBeAppended)
    fileToBeRead.close()

# Store the email (which, recall, is a string) as a tuple, with the scheduling/nonScheduling keywords for our classifier
allEmails = ([(email, 'scheduling') for email in schedEmails])
allEmails += ([(email, 'nonScheduling') for email in nonSchedEmails])

#Shuffle ensures randomness when splitting data into tester and trainer files
random.shuffle(allEmails)

# Now, get all non-stop words per email (as string), if the word is a non-stop word it will be of the type: (word, true)
# Note that getFeatures returns a dictionary, so featureSets will be a list of dictionaries of tuples.
print("Acquiring feature words (i.e. non-stop words), for each email...")
featureSets = [(getFeatures(k), v) for (k, v) in allEmails]

print("Splitting data into tester/trainer data.  80% trainer, 20% tester")
splittingRatio = len(featureSets) * 0.8

rawTesterData = allEmails[int(splittingRatio):]
rawTrainerData = allEmails[:int(splittingRatio)]

testerDataFeatures = featureSets[int(splittingRatio):]
trainerDataFeatures = featureSets[:int(splittingRatio)]

print("Training Naive Bayes classifier")
classifier = NaiveBayesClassifier.train(trainerDataFeatures)

print("Classifying emails as scheduling/non-scheduling and printing out date/time/location/EVENT for scheduling emails ONLY.")
print("NOW CREATING OUTPUT FILE!")
print("File can be found here: " + parentPath + "\OUTPUT.TXT")

if(os.path.isfile(parentPath + '/OUTPUT.txt')):
    try:
        os.remove(parentPath + '/OUTPUT.txt')
    except:
        print "OUTPUT FILE ALREADY BEING USED.  CLOSE FIRST PLEASE"
        exit()

#Open a new file and begin writing out the results to the file.
with open(parentPath + '/OUTPUT.txt', 'a') as outFile:
    for i in range(0, len(rawTesterData)):
        isClassifier = classifier.classify(testerDataFeatures[i][0])
        if (isClassifier == "scheduling"):
            stringToPrint = "----SCHEDULING---- ORIGINAL_STRING: " + repr(rawTesterData[i][0])
            outFile.write(stringToPrint)
            outFile.write("\n")
            outFile.write("                   " + taggerAndResultBuilder(rawTesterData[i][0]))
        elif (isClassifier == "nonScheduling"):
            stringToPrint = "---NONSCHEDULING-- ORIGINAL_STRING: " + repr(rawTesterData[i][0])
            outFile.write(stringToPrint)

        outFile.write("\n")

allClassifier = NaiveBayesClassifier.train(featureSets)
#Go ahead and allow for user input!
print("Output file now printed, user can now classify her/his own documents")
while(True):
    controlInput = raw_input('Please enter your own email to classify (as a text file, for ex. /dir1/dir2/something.txt), or type q to quit: ')
    if(controlInput == "q"):
        print("good bye!")
        exit()

    while(not os.path.isfile(controlInput)):
        controlInput = raw_input('This is not a file.  Please enter your own email to classify (as a text file, for ex. /dir1/dir2/something.txt), or type q to quit: ')
        if(controlInput == "q"):
            print("good bye!")
            exit()

    fileToBeRead = open(controlInput, "r")
    stringFromFileToBeAppended = fileToBeRead.read()

    keyWords = getFeatures(stringFromFileToBeAppended)
    isClassifier = allClassifier.classify(keyWords)
    print ("\n")
    print "This email is", isClassifier
    if (isClassifier == "scheduling"):
        stringToPrint = taggerAndResultBuilder(stringFromFileToBeAppended)
        stringToPrint = "Data extracted from email is: " + stringToPrint
        print stringToPrint
        print ("\n")
