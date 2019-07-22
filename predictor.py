import bs4 as bs
import re
import requests
import time
import numpy as np
import sklearn
from sklearn.linear_model import LinearRegression
from wordcloud import WordCloud, STOPWORDS
import matplotlib.pyplot as plt

from nltk.sentiment.vader import SentimentIntensityAnalyzer as SIA
import pandas as pd

print("##################START#####################\n")

flipkart={}
amazon={}
review_content=[]
review_content_amz=[]
flink=raw_input("\nEnter flipkart link: ")
alink=raw_input("\nEnter amazon link: ")
sauce=requests.get(flink).content
soup=bs.BeautifulSoup(sauce,'lxml')
print("###############FLIPKART####################")
for span in soup.find_all("span",class_='_35KyD6'):
    name=(span.text)
    print("\nNAME: "+name)
    flipkart["name"]=name
for div in soup.find_all("div",class_='_1vC4OE _3qQ9m1'):
    price=(div.text[1:]).replace(",","")
    price=int(price)
    print("\nPRICE: "+str(price))
    flipkart["price"]=price
for div in soup.find_all("div",class_='_1i0wk8'):
    rating=float(div.text)
    print("\nRATING: "+str(rating))
    flipkart["rating"]=rating

for span in soup.find("span",class_='_38sUEc'):
    sentence=span.text.replace(",","")
    print(sentence)
    qty=[int(s) for s in sentence.split() if s.isdigit()]
    num_revs=int(qty[1])
    flipkart["numrevs"]=num_revs 
reviewurl=flink.replace("/p/","/product-reviews/")
sauce=requests.get(reviewurl).content soup=bs.BeautifulSoup(sauce,'lxml')
ul = soup.find('ul', class_='_316MJb')

if(ul):
    last_page=soup.find("span",class_="_3v8VuN")
    last_page=int(last_page.text.split()[-1].replace(",",""))
    if(last_page>13):
        last_page=13

else:
    last_page=1

if(last_page>=3):
    for pg_counter in range(last_page,last_page-4,-1):
        rev=reviewurl+("&page="+str(pg_counter)+"&sort=MOST_RECENT")
        sauce=requests.get(rev).content
        soup=bs.BeautifulSoup(sauce,'lxml')
        for contents in soup.find_all("div",class_="qwjRop"):
            indicunts=(contents.text)[:-9]
            review_content.append(indicunts)
        review_content.reverse()
            
else:
    for pg_counter in range(last_page,0,-1):
        rev=reviewurl+("&page="+str(pg_counter)+"&sort=MOST_RECENT")
        sauce=requests.get(rev).content
        soup=bs.BeautifulSoup(sauce,'lxml')
        for contents in soup.find_all("div",class_="qwjRop"):
            indicunts=(contents.text)[:-9]
            review_content.append(indicunts)
        review_content.reverse()

if len(review_content)>30:
    review_content=review_content[:30]
flipkart["reviews"]=review_content
print("\nSOME REVIEWS: ")
for item in range(0,6):
    print(review_content[item])
    print("\n")


print("##################AMAZON####################")


while(True):
    if(requests.get(alink,timeout=8).status_code==200):
        sauce=requests.get(alink,headers={'User-Agent': 'Mozilla/5.0 (Windows NT 6.3; Win64;	x64)	AppleWebKit/537.36	(KHTML,	like	Gecko)	Chrome/67.0.3396.99 Safari/537.36'},timeout=5).content
        break
    
##	print(requests.get(alink,timeout=5).status_code)

soup=bs.BeautifulSoup(sauce,'lxml')
for span in soup.find_all("span",id=re.compile("^priceblock_")):
    ##	print(span.text.strip())
    if (re.match("^[1-9]",span.text.strip())):
        rice_amz=float(((span.text).strip().replace(",","")))
        print("\nPRICE: "+str(price_amz))
        amazon["price"]=price_amz
for span in soup.find_all("span",id='acrCustomerReviewText'):
    num_revs_amz=int((span.text).replace(",","").split()[0])
    print("Number of reviews:"+str(num_revs_amz))
    amazon["numrevs"]=int(num_revs_amz)

reviewurl_amz=alink.replace("/dp/","/product-reviews/")
sauce=requests.get(reviewurl_amz).content
soup=bs.BeautifulSoup(sauce,'lxml')
ul = soup.find('ul', class_='a-pagination')
if(ul):
    li=ul.find_all("li")
    last_page_amz=int(li[-2].text.replace(",",""))
    ##	print("Page"+str(last_page))

else:
    last_page_amz=1

for div in soup.find_all("div",class_="averageStarRatingNumerical"):
    rating_amz=float(div.text.strip()[:3])
    print("RATING: "+str(rating_amz))
    amazon["rating"]=rating_amz

if(last_page_amz>=3):
    for pg_counter in range(last_page_amz,last_page_amz-4,-1):
        rev=reviewurl_amz+("&sortBy=recent&pageNumber="+str(pg_counter))
        sauce=requests.get(rev).content
        soup=bs.BeautifulSoup(sauce,'lxml')
        for contents in soup.find_all("span",class_="review-text"):
            indicunt=contents.text
            review_content_amz.append(indicunt)
        review_content_amz.reverse()

else:
    for pg_counter in range(last_page_amz,0,-1):
        rev=reviewurl_amz+("?sortBy=recent&pageNumber="+str(pg_counter))
        sauce=requests.get(rev).content
        soup=bs.BeautifulSoup(sauce,'lxml')
        for contents in soup.find_all("span",class_="review-text"):
            indicunt=contents.text
            review_content_amz.append(indicunt)
        review_content_amz.reverse()

if len(review_content_amz)>30:
    review_content_amz=review_content_amz[:30]

amazon["reviews"]=review_content_amz
if(len(amazon["reviews"])>5):
    print("\nSOME REVIEWS: ")
    for item in range(0,6):
        print(review_content_amz[item])
        print("\n")

print("\n#############SENTIMENT SCORING#####################")

sid = SIA()
scores=()
negative=0
positive=0
neutral=0
scores_a=()
negative_a=0
positive_a=0
neutral_a=0

for sentence in flipkart["reviews"]:
    ss = sid.polarity_scores(sentence)
    negative+=(ss['neg'])
    positive+=(ss['pos'])
    neutral+=(ss['neu'])

positive/=len(flipkart["reviews"])
positive=round(positive,2)
negative/=len(flipkart["reviews"])
negative=round(negative,2)
neutral/=len(flipkart["reviews"])
neutral=round(neutral,2)
print("\nFLIPKART\n")

print("pos: " + str(positive)+"\nneg: "+str(negative)+"\nneu: "+str(neutral)+"\n")
scores=scores+(negative,positive,neutral,)
flipkart["scores"]=scores

negative=0
positive=0
neutral=0
negative_a=0
positive_a=0
neutral_a=0

for sentence in amazon["reviews"]:
    ss = sid.polarity_scores(sentence)
    negative+=(ss['neg'])
    positive+=(ss['pos'])
    neutral+=(ss['neu'])

positive/=len(amazon["reviews"])
positive=round(positive,2)
negative/=len(amazon["reviews"])
negative=round(negative,2)
neutral/=len(amazon["reviews"])
neutral=round(neutral,2)
print("\nAMAZON\n")
print("pos: " + str(positive)+"\nneg: "+str(negative)+"\nneu: "+str(neutral)+"\n") scores_a=scores_a+(negative,positive,neutral,)
amazon["scores"]=scores_a

prediction_f=4.01207030822+0.000006*flipkart["price"]+0.000005*flipkart["numrevs"]+0.749382*flipkart["scores"][0]-3.064320*flipkart['scores'][1]- 0.404451*flipkart['scores'][2]
print("FLIPKART MY RATING:")

print(prediction_f)
prediction_a=4.01207030822+0.000006*amazon["price"]+0.000005*amazon["numrevs"]+0.7493 82*amazon["scores"][0]-3.064320*amazon['scores'][1]-0.404451*amazon['scores'][2]
print("\nAMAZON MY RATING:")

print(prediction_a)
if(float(flipkart["price"])<amazon["price"]):
    print("\n##############FLIPKART IS BETTER CHOICE#############")
elif(flipkart["price"]>amazon["price"]):
    print("\n##############AMAZON IS BETTER CHOICE#############")

else:
    if(prediction_f>prediction_a):
        print("\n##############FLIPKART IS BETTER CHOICE#############")

    else:
        print("\n##############AMAZON IS BETTER CHOICE#############")

##########GRAPHS###########

label=['Flipkart','Amazon']
prices=[flipkart["price"],amazon["price"]]
index = np.arange(len(label))
plt.bar(index,prices,width=0.1)
plt.xlabel('Website', fontsize=5)
plt.ylabel('Price', fontsize=5)
plt.xticks(index, label, fontsize=5, rotation=30)
plt.title('Comparison of prices')
plt.show()

###########WORDCLOUD###########

df=pd.DataFrame(flipkart['reviews'])
col_name =df.columns[0]
df=df.rename(columns = {col_name:'reviews'})
##print(df)

comment_words = ' '
stopwords = set(STOPWORDS)
tokens=[]

for val in flipkart["reviews"]:
    tokens.extend(val.split())
for val in amazon["reviews"]:
    tokens.extend(val.split())
for i in range(len(tokens)):
    tokens[i] = tokens[i].lower()

for words in tokens:

comment_words = comment_words + words + ' '
wordcloud = WordCloud(width = 800, height = 800, background_color ='white', stopwords = stopwords, min_font_size = 10).generate(comment_words)
plt.figure(figsize = (8, 8), facecolor = None)
plt.imshow(wordcloud)
plt.axis("off")
plt.tight_layout(pad = 0)
plt.show()


    

        
    



    

