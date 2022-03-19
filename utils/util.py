import re
import datetime
import emoji
import regex


def startsWithDateAndTimeAndroid(s):
    pattern = '^([0-9]+)(\/)([0-9]+)(\/)([0-9]+), ([0-9]+):([0-9]+)[ ]?(AM|PM|am|pm)? -' 
    result = re.match(pattern, s)
    if result:
        return True
    return False

def startsWithDateAndTimeios(s):
    pattern = '^\[([0-9]+)([\/-/.])([0-9]+)([\/-/.])([0-9]+)[,]? ([0-9]+):([0-9][0-9]):([0-9][0-9])?[ ]?(AM|PM|am|pm)?\]' 
    result = re.match(pattern, s)
    if result:
        return True
    return False

def FindAuthor(s):
  s=s.split(":")
  if len(s)==2:
    return True
  else:
    return False

def getDataPointAndroid(line):   
    splitLine = line.split(' - ') 
    dateTime = splitLine[0]
    date, time = dateTime.split(', ') 
    message = ' '.join(splitLine[1:])
    if FindAuthor(message): 
        splitMessage = message.split(':') 
        author = splitMessage[0] 
        message = ' '.join(splitMessage[1:])
    else:
        author = None
    return date, time, author, message

def getDataPointios(line):
    splitLine = line.split('] ')
    dateTime = splitLine[0]
    if ',' in dateTime:
        date, time = dateTime.split(',')
    else:
        date, time = dateTime.split(' ')
    message = ' '.join(splitLine[1:])
    if FindAuthor(message):
        splitMessage = message.split(':')
        author = splitMessage[0]
        message = ' '.join(splitMessage[1:])
    else:
        author = None
    if time[5]==":":
        time = time[:5]+time[-3:]
    else:
        if 'AM' in time or 'PM' in time:
            time = time[:6]+time[-3:]
        else:
            time = time[:6]
    return date, time, author, message


def dateconv(date):
    year=''
    if '-' in date:
        year = date.split('-')[2]
        if len(year) == 4:
            return datetime.datetime.strptime(date, "[%d-%m-%Y").strftime("%Y-%m-%d")
        elif len(year) ==2:
            return datetime.datetime.strptime(date, "[%d-%m-%y").strftime("%Y-%m-%d")
    elif '/' in date:
        year = date.split('/')[2]
        if len(year) == 4:
            return datetime.datetime.strptime(date, "[%d/%m/%Y").strftime("%Y-%m-%d")
        if len(year) ==2:
            return datetime.datetime.strptime(date, "[%d/%m/%y").strftime("%Y-%m-%d")
    elif '.' in date:
        year = date.split('.')[2]
        if len(year) == 4:
            return datetime.datetime.strptime(date, "[%d.%m.%Y").strftime("%Y-%m-%d")
        if len(year) ==2:
            return datetime.datetime.strptime(date, "[%d.%m.%y").strftime("%Y-%m-%d")

def split_count(text):

    text = emoji.demojize(text)
    text = re.findall(r'(:[^:]*:)', text)
    emoji_list = [emoji.emojize(x) for x in text]

    return emoji_list