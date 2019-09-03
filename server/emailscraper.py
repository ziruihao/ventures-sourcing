import os
import sys
import csv
from dotenv import load_dotenv
from lib.google_search_results import GoogleSearchResults
from difflib import SequenceMatcher
load_dotenv()

"""
These two lists are a reference guide for the parsing process.
It will check these domains to quickly identify email addresses in the Google query.
If an email does not include on of these domains, it will still be considered.
"""
commonDomains = [".com ", ".ai ", ".net ", ".io ", ".org "]
commonDomainsWithDot = []
for domain in commonDomains:
    commonDomainsWithDot.append(domain[:-1] + ".")
commonDomains = commonDomainsWithDot + commonDomains

def email_check(fileDir):
    SERPAPI_API_KEY = os.getenv("SERPAPI_API_KEY")
    with open(fileDir, mode="r") as inputFile:
        with open('./data/email.csv', mode='w') as outputFile:
            reader = csv.reader(inputFile, delimiter=',', quotechar='"')
            writer = csv.writer(outputFile, delimiter=',', quotechar='"')
            for row in reader:
                companyName = row[0]
                candidate = {}
                otherCandidates = []
                print(companyName)

                # SERPAPI parameters
                searchParams = {
                    "engine": "google",
                    "q": '"' + companyName + '"' + " crunchbase contact info",
                    "google_domain": "google.com",
                    "gl": "us",
                    "hl": "en",
                    "filter": "0",
                    "api_key": SERPAPI_API_KEY,
                }
                client = GoogleSearchResults(searchParams)
                results = client.get_dict()

                for result in results['organic_results']:

                    if (verifyResult(result)):
                        if (result['position'] is 1):
                            candidate = {
                                "companyName": companyName,
                                "companyEmail": extractContact(result),
                                "confidence": getSimilarity(result, companyName),           
                            }
                        else:
                            otherCandidates.append({
                                "companyName": companyName,
                                "companyEmail": extractContact(result),
                                "confidence": getSimilarity(result, companyName),
                            })

                otherCandidates.sort(key = sortConfidence, reverse = True)
                
                try:
                    row.append(candidate['companyEmail'])
                    row.append(candidate['confidence'])
                    writer.writerow(row)

                    print("Main Candidate: ")
                    print("\t" + candidate["companyEmail"])
                    print("\t" + str(candidate["confidence"]))

                    print("Other Candidate: ")
                    for entry in otherCandidates:
                        print("\t" + entry["companyEmail"])
                        print("\t" + str(entry["confidence"]))
                except:
                    print('fuck')
                    print(candidate)

    # Returns the file path that the server then sends for download
    return './data/email.csv'

"""
Verifies that the Google result is a CB page
"""
def verifyResult(result):
    # testing url
    if ("https://www.crunchbase.com/organization" not in result["link"]):
        return False
    return True

"""
Gets a general string match similarity to assess confidence that we have matched the company.
"""
def getSimilarity(result, companyName):
    crunchbaseName = result["link"][40:]
    crunchbaseName.replace('-', ' ')
    similarity = SequenceMatcher(None, crunchbaseName.lower(), companyName.lower()).ratio()
    return similarity

"""
Parsesthe result body snippet text to find the email address.
Weakest part of algorithm.
"""
def extractContact(result):
    potentialEmail = "not found"
    positioner = result["snippet"].find("Contact Email")
    if (positioner is not -1):
        potentialEmail = result["snippet"][(positioner + 14):]
        print(potentialEmail)
        for domain in commonDomains:
            if (domain in potentialEmail):
                positioner = potentialEmail.find(domain)
        potentialEmail = potentialEmail[:(positioner + len(domain))]
        if (potentialEmail[-1:] is "."):
            potentialEmail = potentialEmail[:-1]
        if ("Phone Number" in potentialEmail):
            potentialEmail = potentialEmail[:((potentialEmail.find("Phone Number")))]
    return potentialEmail

"""
A helper function to sort confidence
"""
def sortConfidence(companyObject):
    return companyObject['confidence']