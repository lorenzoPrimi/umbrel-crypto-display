from datetime import datetime
from PIL import Image, ImageFilter, ImageDraw, ImageFont, ImageColor
import json
import math
import subprocess
import time

cryptos=["btc", "eth", "ada"]
priceurl="https://api.coingecko.com/api/v3/coins/markets?vs_currency=usd&symbols="
outputFolder="/home/umbrel/umbrel-crypto-display/images/"
colorRed=ImageColor.getrgb("#FF0000")
colorGreen=ImageColor.getrgb("#32CD30")
colorGold=ImageColor.getrgb("#FFD700")
colorD9D9D9=ImageColor.getrgb("#D9D9D9")
color404040=ImageColor.getrgb("#404040")
color40FF40=ImageColor.getrgb("#40FF40")
color000000=ImageColor.getrgb("#000000")
colorFFFFFF=ImageColor.getrgb("#ffffff")
fontDeja12=ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",12)
fontDeja16=ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",16)
fontDeja20=ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",20)
fontDeja24=ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",24)
fontDeja128=ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",128)
last=1
low=1
high=1

def drawsatssquare(draw,dc,dr,spf,satw,bpx,bpy):
    satsleft = spf
    for y in range(10):
        for x in range(10):
            if satsleft > 0:
                tlx = (bpx + (dc*11*satw) + (x*satw))
                tly = (bpy + (dr*11*satw) + (y*satw))
                brx = tlx+satw-2
                bry = tly+satw-2
                draw.rectangle(xy=((tlx,tly),(brx,bry)),fill=color40FF40)
            satsleft = satsleft - 1

def getdateandtime():
    now = datetime.utcnow()
    return now.strftime("%Y-%m-%d %H:%M:%S")
def getfont(size):
    if size == 12:
        return fontDeja12
    if size == 16:
        return fontDeja16
    if size == 20:
        return fontDeja20
    if size == 24:
        return fontDeja24
    if size == 128:
        return fontDeja128

def drawcenteredtext(draw, s, fontsize, x, y, textcolor=colorFFFFFF):
    thefont = getfont(fontsize)
    sw,sh = draw.textsize(s, thefont)
    ox,oy = thefont.getoffset(s)
    sw += ox
    sh += oy
    draw.text(xy=(x-(sw/2),y-(sh/2)), text=s, font=thefont, fill=textcolor)

def drawbottomlefttext(draw, s, fontsize, x, y, textcolor=colorFFFFFF):
    thefont = getfont(fontsize)
    sw,sh = draw.textsize(s, thefont)
    ox,oy = thefont.getoffset(s)
    sw += ox
    sh += oy
    draw.text(xy=(x,y-sh), text=s, font=thefont, fill=textcolor)

def drawbottomrighttext(draw, s, fontsize, x, y, textcolor=colorFFFFFF):
    thefont = getfont(fontsize)
    sw,sh = draw.textsize(s, thefont)
    ox,oy = thefont.getoffset(s)
    sw += ox
    sh += oy
    draw.text(xy=(x-sw,y-sh), text=s, font=thefont, fill=textcolor)

def createimage(ticker, width=480, height=320):
    name,last,high,low,percentage = getpriceinfo(ticker)
    satw=int(math.floor(width/87))
    padleft=int(math.floor((width-(87*satw))/2))
    padtop=40
    im = Image.new(mode="RGB", size=(width, height))
    draw = ImageDraw.Draw(im)
    drawcenteredtext(draw, str(last), 128, int(width/2), int(height/2), colorD9D9D9)
    drawcenteredtext(draw, str(last), 128, int(width/2)-2, int(height/2)-2, colorFFFFFF)
    drawcenteredtext(draw, name + " price:", 24, int(width/2), int(padtop/2))
    if percentage >= 0 :
        drawcenteredtext(draw, "24h: " + str(percentage) + "%", 20, int(width/8*4), height-padtop, colorGreen)
    if percentage < 0 :
        drawcenteredtext(draw, "24h: " + str(percentage) + "%", 20, int(width/8*4), height-padtop, colorRed)
    drawcenteredtext(draw, "High: " + str(low), 20, int(width/8*7), height-padtop)
    drawcenteredtext(draw, "Low: " + str(high), 20, int(width/8*1), height-padtop)
    drawbottomlefttext(draw, "Market data by coingecko", 16, 0, height, color40FF40)
    drawbottomrighttext(draw, "as of " + getdateandtime(), 12, width, height)
    outputFile = outputFolder + ticker + ".png"
    im.save(outputFile)

def getpriceinfo(ticker):
    cmd = "curl --silent \"" + priceurl +  ticker + "\""
    global last
    global high
    global low
    global name
    global percentage
    global price
    try:
        cmdoutput = subprocess.check_output(cmd, shell=True).decode("utf-8")
        if len(cmdoutput) > 0:
            j = json.loads(cmdoutput)
            name = str(j[0]["name"])
            price = float(j[0]["current_price"])
            if price < 1000 :
                last = round(float(j[0]["current_price"]), 2)
                high = round(float(j[0]["high_24h"]), 2)
                low = round(float(j[0]["low_24h"]), 2)
            if price >= 1000 :
                last = int(math.floor(float(j[0]["current_price"])))
                high = int(math.floor(float(j[0]["high_24h"])))
                low = int(math.floor(float(j[0]["low_24h"])))
            percentage = round(float(j[0]["price_change_percentage_24h"]), 2)
    except subprocess.CalledProcessError as e:
        cmdoutput = "{\"error\":  }"
    return (name,last,high,low,percentage)

for ticker in cryptos:
    createimage(ticker)
    time.sleep(1)
