import time
import requests
import pickle

if __name__ == "__main__":
    # article_name = "Earth"
    # history_url = "https://api.wikimedia.org/core/v1/wikipedia/en/page/"+article_name+"/history"

    article_ids = [47758247, 33782488, 28922023, 31574141]
    article_names = ["Murray_Art_Museum_Albury", "Lammers", "Peugeot_EX1_Concept", "Floyd_Bedbury"]

    for article_name in article_names:
        history_url = "https://api.wikimedia.org/core/v1/wikipedia/en/page/" + article_name + "/history"

        revisions = []

        start_time = time.time()
        try:
            while True:
                if len(revisions)%100 == 0:
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
        print("Fetching of", str(len(revisions)),"revisions took", end_time-start_time, "seconds")

        with open('wiki_raw/'+article_name+'.pkl', 'wb') as f:
            pickle.dump(revisions, f)
