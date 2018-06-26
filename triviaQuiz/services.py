import requests
import json

class APICaller():

    URL = "https://opentdb.com/"
    CATEGORIES = "api_category.php"
    QUESTION_COUNT = 10
    QUESTION_TYPE = "multiple"

    def get_categories(self):
        return requests.get(self.URL + self.CATEGORIES)

    def get_questions(self, urlParams):
        url = self.URL + "api.php?amount=" + str(self.QUESTION_COUNT) + "&type=" + self.QUESTION_TYPE
        # Get the data given the paramaters
        request = requests.get(url)
        return request

def get_questions(create_object):
    # Get the data given the paramaters
    difficulty = create_object.getDifficulty()
    params = dict()
    if (difficulty != 'Random'):
        params['difficulty'] = create_object.getDifficulty()
    if (create_object.category):
        params['category'] = create_object.category

    r = APICaller().get_questions(params)
    # Loop though al questions
    jsonResults = r.json()['results']
    questions = ([question for question in jsonResults])
    return questions

def get_categories():
    """ Gets all the categories for the website
    
    Returns:
        List -- The list of categories
    """
    # Get request
    r = APICaller().get_categories()
    # Get json from request
    jsonResults = r.json()['trivia_categories']
    # Loop through all categories given from the json
    categories = list()
    for category in jsonResults:
        categories.append((str(category['id']), category['name']))
    #categories = ([category for category in jsonResults])
    return categories