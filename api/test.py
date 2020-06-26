from bs4 import BeautifulSoup 

def crawler():
    import requests
    import json
    import re
    result = {}
    sku = "9789353020460"
    url = "https://www.amazon.in/s?url=search-alias%3Daps&field-keywords="+sku

    # print(self.config_dct["target_url"])

    try:
        req = requests.get(url)
        soup = BeautifulSoup(req.text, 'lxml')

        # anchors = soup.find_all('img')
        imge = soup.find("div",{"class":"a-column a-span12 a-text-center"})
        ratingDiv = soup.find("div", {"class":"a-column a-span5 a-span-last"})
        # print('image is')
        imageUrl = imge.find('img').get('src')
        # print(imageUrl)
        amazonRating = ratingDiv.find('span',{"class":"a-icon-alt"}).text

        authorDiv = soup.find("span",{"class":"a-size-small a-color-secondary"})
        authorDivD = authorDiv.text 
        if authorDivD == 'by':
            print(authorDiv.next_sibling)
            
        # print(amazonRating)
        result['status'] = True
        result['ISBN'] = sku
        result['image'] = imageUrl
        result['Amazon Rating'] = amazonRating

    except Exception as e:
        print('Exception in crawler for crawling: ', e)
        result['status'] = False
        result['ISBN'] = sku
        result['Amazon Rating'] = 'Not Available'
        result['image'] = 'Not Available'

    # self.client.close()
    
    return result

def get_goodreads_data(to,from,subject,body,cc,sender):
    import requests
    import json 
    url = "http://101.53.139.41:8083/wishbooks/wishbookMail"
    dataToPost = {}
    dataToPost['to'] = "sheetal@freenet.zone"
    dataToPost['from'] = "operations@justbooksclc.com"
    dataToPost['subject'] = "New Releases"
    dataToPost['body'] = "We have uploaded Releases for October Month on MIS Portal.<br/><br/> Please order books before 25th Oct.Note: Super Lead title will be arranged on priority."
    dataToPost['cc'] = "sheetalsrk05@gmail.com"
    dataToPost['sender'] = "Prashanth.R"
    headers = {
        'content-type': "application/json",
        'cache-control': "no-cache"
    }
    try:
        response = requests.request("POST", url, data=json.dumps(dataToPost,  sort_keys=True, indent=4), headers=headers)
        print(response.text)
        return True
    except Exception as e:
        return False


def convertdate():
    from datetime import datetime
    s = "2018-8-20"
    strdate = datetime(*map(int, s.split('-')))
    print(strdate)
    print(type(strdate))

def some_view(request):
    import io
    from django.http import FileResponse
    from reportlab.pdfgen import canvas
    # Create a file-like buffer to receive PDF data.
    buffer = io.BytesIO()

    # Create the PDF object, using the buffer as its "file."
    p = canvas.Canvas(buffer)

    # Draw things on the PDF. Here's where the PDF generation happens.
    # See the ReportLab documentation for the full list of functionality.
    p.drawString(100, 100, "Hello world.")

    # Close the PDF object cleanly, and we're done.
    p.showPage()
    p.save()

    # FileResponse sets the Content-Disposition header so that browsers
    # present the option to save the file.
    return FileResponse(buffer, as_attachment=True, filename='hello.pdf')


def check():
    import urllib
    sku_list = ["232r","2323222"]
    tu = {"sku":sku_list}
    print(urllib.parse.urlencode(tu,True))

# check()