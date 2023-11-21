import time
import requests

if __name__=="__main__":
    history_url = "https://api.wikimedia.org/core/v1/wikipedia/en/page/Earth/history"

    revisions = []

    start_time = time.time()
    try:
        while True:
            print("Iteration", str(len(revisions)//20))
            response = requests.get(history_url).json()

            revisions += response["revisions"]

            if "older" in response.keys():
                history_url = response["older"]
            else:
                break
    except Exception as error:
        print("Exception:", error)
    end_time = time.time()
    print("Fetching of",str(len(revisions)),"revisions took", end_time-start_time, "seconds")
