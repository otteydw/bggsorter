import xml.etree.ElementTree as ET
import requests
import csv


def loadRSS(username):

    # url of rss feed
    url = "https://www.boardgamegeek.com/xmlapi/collection/" + username + "?played=1"

    # creating HTTP response object from given url
    resp = requests.get(url)

    # saving the xml file
    with open(username + '.xml', 'wb') as f:
        f.write(resp.content)


def parseXML(xmlfile):

    # create element tree object
    tree = ET.parse(xmlfile)

    # get root element
    root = tree.getroot()

    # print('\nAll attributes:')
    # for elem in root:
    #     for subelem in elem:
    #         print(subelem.attrib)

    print('\nAll item data:')
    for elem in root:

        # print(str(elem.attrib) + '     ' + str(elem.text) + 'AAA')
        objectid = elem.attrib.get('objectid')
        name = elem[0].text
        year = elem[1].text
        image = elem[2].text
        thumbnail = elem[3].text
        print(objectid, name, year, image, thumbnail)

        # for subelem in elem:
        #     print(str(subelem.attrib) + '     ' + str(subelem.text))

        # objectid = elem

    # # create empty list for news items
    # games = []

    # # iterate news items
    # # for item in root.findall('./channel/item'):
    # for item in root.findall('./item'):

    #     # empty news dictionary
    #     news = {}

    #     # iterate child elements of item
    #     # for child in item:

    #     #     # special checking for namespace object content:media
    #     #     if child.tag == '{http://search.yahoo.com/mrss/}content':
    #     #         news['media'] = child.attrib['url']
    #     #     else:
    #     #         news[child.tag] = child.text.encode('utf8')

    #     # append news dictionary to news items list
    #     games.append(item)

    # # return news items list
    # return games


# def savetoCSV(games, filename):

#     # specifying the fields for csv file
#     # fields = ['guid', 'title', 'pubDate', 'description', 'link', 'media']
#     fields=['objectid', 'name']

#     # writing to csv file
#     with open(filename, 'w') as csvfile:

#         # creating a csv dict writer object
#         writer=csv.DictWriter(csvfile, fieldnames=fields)

#         # writing headers (field names)
#         writer.writeheader()

#         # writing data rows
#         writer.writerows(games)


def main():
    username = 'otteydw'
    # load rss from web to update existing xml file
    loadRSS(username)

    # parse xml file
    # games = parseXML(username + '.xml')
    parseXML(username + '.xml')

    # store news items in a csv file
    # savetoCSV(games, username + '.csv')


if __name__ == "__main__":

    # calling main function
    main()
