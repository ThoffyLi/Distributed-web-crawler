from django.shortcuts import render
from django.views.generic.base import View
# Create your views here.
from search.models import HupuType
from django.http import HttpResponse
import json
from elasticsearch import Elasticsearch
from LVCSearch.settings import ES_HOST


client = Elasticsearch(hosts = [ES_HOST])


class SearchSuggest(View):

    def get(self,request):
        key_words = request.GET.get('s','')
        re_data = []
        if key_words:
            s = HupuType.search()
            s = s.suggest('my_suggest',key_words, completion = {
                "field" : "suggest",
                "fuzzy":{
                    "fuzziness": 2
                },
                "size": 10
            })
            a = s.to_dict()
            suggestions = s.execute()
            a = suggestions.to_dict()

            for match in suggestions.suggest.my_suggest[0].options:
                source = match._source
                re_data.append(source["title"])

        return HttpResponse(json.dumps(re_data),content_type="application/json")


class SearchView(View):

    def get(self,request):
        key_words = request.GET.get("q","")
        response = client.search(
            index = "hupu",
            body = {
                "query":{
                    "multi_match":{
                        "query": key_words,
                        "fields":["title"]
                    }
                },
                "from":0,
                "size":10,
                "highlight":{
                    "pre_tags": ['<span class="keyWord">'],
                    "post_tags": ['</span>'],
                    "fields":{
                        "title":{}
                    }
                }
            }
        )

        total_nums = response["hits"]["total"]
        hit_list = []
        for hit in response["hits"]["hits"]:
            hit_dict = {}
            if "title" in hit["highlight"]:
                hit_dict["title"] = "".join(hit["highlight"]["title"])
            else:
                hit_dict["title"] = "".join(hit["_source"]["title"])

            hit_dict["url"] = hit["_source"]["url"]

            hit_list.append(hit_dict)

        return render(request, "result.html", {"all_hits":hit_list, "key_words":key_words})



