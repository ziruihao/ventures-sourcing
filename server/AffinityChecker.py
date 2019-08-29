import os
import sys
import csv
import requests
from dotenv import load_dotenv
load_dotenv()


def affinity_check(fileDir):
    AFFINITY_API_KEY = os.getenv("AFFINITY_API_KEY")
    print(AFFINITY_API_KEY)
    headers = {
        'Authorization': 'Basic ' + AFFINITY_API_KEY
    }
    newCount = 0
    totalCount = 0
    with open(fileDir, mode="r") as inputFile:
        with open(fileDir + '-affinity.csv', mode="w") as outputFile:
            reader = csv.reader(inputFile, delimiter=',', quotechar='"')
            writer = csv.writer(outputFile, delimiter=',', quotechar='"')
            for row in reader:
                companyDomain = row[0].replace('https://', '').replace('http://','').replace('www.', '')
                print(companyDomain)
                if (companyDomain[:-1] is '/'):
                    companyDomain = companyDomain[:-1]
                r = requests.get('https://api.affinity.co/organizations?term=' + companyDomain, headers = headers).json()
                if (r):
                    totalCount = totalCount + 1
                    if (len(r['organizations']) is not 0):
                        candidateID = r['organizations'][0]['id']
                        r2 = requests.get('https://api.affinity.co/organizations/' + str(candidateID) + '?with_interaction_dates=true', headers = headers).json()
                        if (r2['interaction_dates']['first_email_date'] is None):
                            print('\tNot in contact')
                            row.append('New')
                            writer.writerow(row)
                            newCount = newCount + 1
                        else:
                            print('\tIn contact')
                            row.append('In Contact')
                            writer.writerow(row)

                    else:
                        row.append('New')
                        writer.writerow(row)
                        newCount = newCount + 1

    return (fileDir + '-affinity.csv')