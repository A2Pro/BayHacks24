import requests

def scrape(main, addn):
    # url format https://clinicaltrials.gov/study/NCT01438905?cond=ankle&term=twisted&rank=1
    link = f'https://clinicaltrials.gov/study/NCT01438905?cond={main}&term={addn}&rank='
    for i in range(3):
        newlink = link +i
        requests.get(newlink)