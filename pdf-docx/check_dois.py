import urllib.request
import urllib.error

dois = [
    "10.1109/ACCESS.2020.2989175",
    "10.1109/TCSS.2021.3126628",
    "10.1109/ACCESS.2021.3104985",
    "10.1007/s00371-021-02115-4",
    "10.31436/iiumej.v24i1.2597",
    "10.1007/s11042-021-11170-x",
    "10.1109/ACCESS.2023.3335172",
    "10.3390/app13106132",
    "10.1080/00051144.2025.2460877",
    "10.1109/ACCESS.2025.3574477",
    "10.17487/RFC8439",
    "10.6028/NIST.SP.800-57pt1r5"
]

for doi in dois:
    url = f"https://doi.org/{doi}"
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        res = urllib.request.urlopen(req)
        print(f"[OK] {doi} -> Resolves to: {res.url}")
    except urllib.error.HTTPError as e:
        if e.code == 404:
            print(f"[404] {doi} -> NOT FOUND")
        else:
            # Other errors like 403 Forbidden might just mean bot protection, which means it exists
            print(f"[{e.code}] {doi} -> Might exist, got {e.reason}")
    except Exception as e:
        print(f"[ERR] {doi} -> {e}")
