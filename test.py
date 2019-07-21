import requests

word = {'word':'Verloop'}
for i in range(20):
    requests.post(url = "http://localhost:5000/add",data=word)
