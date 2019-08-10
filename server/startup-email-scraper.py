import os
import sys
from dotenv import load_dotenv
from lib.google_search_results import GoogleSearchResults
from difflib import SequenceMatcher
load_dotenv()

companyName = str(sys.argv[1])
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
SERPAPI_API_KEY = os.getenv("SERPAPI_API_KEY")

candidate = {}
otherCandidates = []
commonDomains = [".com ", ".ai ", ".net ", ".io ", ".org "]
commonDomainsWithDot = []
for domain in commonDomains:
    commonDomainsWithDot.append(domain[:-1] + ".")
commonDomains = commonDomainsWithDot + commonDomains

searchParams = {
    "engine": "google",
    "q": companyName + " crunchbase contact info",
    "google_domain": "google.com",
    "gl": "us",
    "hl": "en",
    "api_key": SERPAPI_API_KEY,
}
client = GoogleSearchResults(searchParams)
results = client.get_dict()

def verifyResult(result):
    # testing url
    if ("https://www.crunchbase.com/organization" not in result["link"]):
        return False
    return True

def getSimilarity(result):
    crunchbaseName = result["link"][40:]
    crunchbaseName.replace('-', ' ')
    similarity = SequenceMatcher(None, crunchbaseName.lower(), companyName.lower()).ratio()
    return similarity

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

def sortConfidence(companyObject):
    return companyObject['confidence']

resultNumber = 0

for result in results['organic_results']:

    if (verifyResult(result)):
        if (resultNumber is 0):
            candidate = {
                "companyName": companyName,
                "companyEmail": extractContact(result),
                "confidence": getSimilarity(result),           
            }
        else:
            otherCandidates.append({
                "companyName": companyName,
                "companyEmail": extractContact(result),
                "confidence": getSimilarity(result),
            })
    resultNumber =+ 1

otherCandidates.sort(key = sortConfidence, reverse = True)

print("Main Candidate: ")
print(candidate["companyName"])
print("\t" + candidate["companyEmail"])
print("\t" + str(candidate["confidence"]))

print("Other Candidate: ")
for entry in otherCandidates:
    print(entry["companyName"])
    print("\t" + entry["companyEmail"])
    print("\t" + str(entry["confidence"]))



