"""Google search utils """
from apiclient.discovery import build
from ...config import config

cses = {
    'wiki': '004999571245303029695:vg9td7rxfom',  # wiki + keywords
    'sot': '004999571245303029695:4-4ruya5u_y',  # stackoverflow tags
    'itjobs': '004999571245303029695:8dgxffq9eui',  # itjobswatch.co.uk/jobs/uk
    'everywhere': '004999571245303029695:95bfezmqesy'  # looks almost everywhere
}


def google_search(query, page=0, cse=None, cse_name=None, related=None):
    if cse_name is None and cse is None:
        raise KeyError("Not custom search engine id nor name presented.")
    if cse is None:
        cse = cses[cse_name]
    service = build("customsearch", "v1",
                    developerKey=config['google_api_key'])
    res = service.cse().list(
        q=query,
        cx=cse,
        start=page * 10 + 1,
        relatedSite=related
    ).execute()
    return res



if __name__ == "__main__":
    pass