import requests
from bs4 import BeautifulSoup
#from pymongo import MongoClient
from time import sleep
import csv
import json
index = 0
headers = {'referer': 'https://eutils.ncbi.nlm.nih.gov', 'user-agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64; rv:47.0) Gecko/20100101 Firefox/47.0'}

# same images
def save_info(res_url,pmccode):
    global index
    html = ''
    trytime = 0
    while(trytime<=3):
        try:
            html = BeautifulSoup(requests.get(res_url, headers=headers,timeout=10).text,features="xml")
            break
        except:
            pass
        finally:
            trytime = trytime + 1
            sleep(5)
    if(html == '' and trytime == 0):
        return []
    #print(html)
    result = []
    for node in html.findAll('body'):
        try:
            bodytext = ''.join(node.findAll(text=True))
            captiontexts = []
            tmpbodytext = bodytext
            hrefs = []
            for fig in node.findAll('fig'):
                captiontexttmp = ''.join(fig.find('caption').findAll(text=True))
                #print(captiontexttmp)
                captiontexts.append(captiontexttmp)
                tmpbodytext = tmpbodytext.replace(captiontexttmp,"")
                href = ''.join(fig.find('graphic').get('xlink:href'))
                hrefs.append(href)
        except :
            continue

        #print(''.join(node.findAll(text=True)))
        #print(tmpbodytext)
        i=0
        for captiontext in captiontexts:
            try:
                dics = {}
                cowords = []
                #https://www.ncbi.nlm.nih.gov/pmc/articles/PMC4415602/bin/nihms651721f11.jpg
                dics['PMCID'] = pmccode
                dics['url'] = 'https://www.ncbi.nlm.nih.gov/pmc/articles/PMC' + pmccode + "/bin/" +  hrefs[i] + ".jpg"
                dics['caption'] = captiontext
                newstr = captiontext.replace("\n"," ").replace(","," ").replace(";"," ").replace(")","").replace("(","")
                words = newstr.split()
                for j in range(len(words)):
                    if words[j][len(words[j]) - 1] == '.':
                        words[j] = words[j].rstrip('.')

                    '''
                    words = list(set(words))
                    #print(words[j])
                    try:
                        if words[j] in tmpbodytext:
                            cowords.append(words[j])
                    except :
                        print(j)
                        pass
                    '''
                    if words[j] in tmpbodytext:
                        cowords.append(words[j])
                #print("####################")
                cowords = list(set(cowords))
                #print(cowords)
                #print("##################")
                #print(''.join(fig.find('caption').findAll(text=True)))
                dics['co-occurrence-words'] = cowords
                dics['co-occurrence-count'] = len(cowords)
                result.append(dics)
            except:
                pass
            finally:
                i = i + 1
            #print(''.join(fig.find('caption').findAll(text=True)))
        break
    return result
    #print(result[0])
    '''
    for link in html.find_all('a', {'class': 'view_img_link'}):
        with open('{}.{}'.format(index, link.get('href')[len(link.get('href'))-3: len(link.get('href'))]), 'wb') as jpg:
            jpg.write(requests.get("http:" + link.get('href')).content)
        print("Now scrapying the num %s data entities" % index)
        index += 1
    '''

if __name__ == '__main__':
    #read pmcid
    predictions_file = open("data.csv", "w", newline="")
    filecsv = csv.writer(predictions_file)
    filecsv.writerow(["PMCID","url","capition","co-occurrence-words","co-occurrence-count"])
    filejson = open("data.json", "w")
    filejson.write("["+"\n")
    rejson = []
    reader = open("pmcid.csv","r",encoding="utf-8")
    i=0
    for line in reader:
        if i != 0:
            line = line.replace('\n','')
            url = 'https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=pmc&id='+line
            print(url)
            if len(line) == 0:
                continue
            result = save_info(url,line)
            if (len(result) == 0):
                continue
            for item in result:
                #print([item['PMCID'],item['url'],item['caption'],",".join(item['co-occurrence-words']),item['co-occurrence-count']])
                captiontxt = item['caption'].replace("\n"," ").replace("\"","")
                #print(captiontxt)
                filecsv.writerow([item['PMCID'],item['url'],captiontxt,(",".join(item['co-occurrence-words'])).replace("\"",""),item['co-occurrence-count']])
                filejson.write(json.dumps(item)+",\n")
            sleep(1)
            #print(result)
        i = i + 1
    filejson.write("{}\n]")
    predictions_file.close()
    filejson.close()
    reader.close()
    #print(result[0])
    #print(len(result))
    #url = 'https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=pmc&id=4415602'
    #save_jpg(url,pmccode)
    '''
    for i in range(0, 5):
        save_jpg(url)
        url = BeautifulSoup(requests.get(url, headers=headers).text).find('a', {'class': 'previous-comment-page'}).get('href')
    '''
