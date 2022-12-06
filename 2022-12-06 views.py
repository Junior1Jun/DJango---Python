# Create your views here.
from django.http import HttpResponse
from django.shortcuts import render

import xmltodict
import requests as req


from .models import JSON
from rest_framework.response import Response
from rest_framework.views import APIView
from .serializers import JSONSerializer
from .serializers import JSON_1Serializer
from .serializers import JSON_2Serializer


import pymysql as pms
import pandas as pd


class JSONListAPI(APIView):
    def get(self,request,page_num,content_num):
        if content_num == 1:
            df = pd.read_json("https://api.odcloud.kr/api/15092231/v1/uddi:f485c10f-f5d2-4a00-a993-b85d929565ec?page="+ str(page_num) +"&perPage=10&serviceKey=Ar6tat092yzvcQYUO8wCqMtbnxBjQwCGjNL4BsE6kmpaWXECc153R13Nj2eUkD%2FHQw3Zi9YroLnnTzc4q1L%2Flw%3D%3D")['data']
            mapping_list = {'title':{'전문자료 메인 제목':'org'},'subjects':{'주제1':'org1','주제2':'org2','주제3':'org3','전문자료 문서 타입':'org4'},'description':{'전문자료 문서 목차':'toc','전문자료 문서 새요약':'summary'},'publisher':{'전문자료 부서 코드':'org'},'contributors':{'전문자료 문서 저자':'author','전문자료 등록자':'donator'},'date':{'전문자료 등록 일자':'registered','전문자료 승인 일자':'available'},'language':{'org':'ko'},'identifier':{'전문자료 문서 아이디':'site'}}
        elif content_num == 2:
            data = req.get("https://www.law.go.kr/DRF/lawSearch.do?OC=helena0809&target=law&type=XML&page="+str(page_num))
            xmlObject = xmltodict.parse(data.content)
            mapping_list = {"type":{"org":"T007:법령"},"title":{"법령명한글":"org"},"subjects":{"법령약칭명":"org"},"publisher":{"소관부처명":"org"},"date":{"공포일자":"issued","시행일자":"available"},"language":{"org":"ko"},"identifier":{"법령일련번호":"site","법령상세링크":"url"},"relation":{"제개정구분명":"isPartOF"}}
            unrefined_df = xmlObject['LawSearch']['law']
            df = []
            for i in range(len(unrefined_df)):
                del(unrefined_df[i]["@id"])
                df.append(unrefined_df[i])
        elif content_num == 3:
            data = req.get("https://www.law.go.kr/DRF/lawSearch.do?OC=helena0809&target=admrul&type=XML&page="+str(page_num))
            xmlObject = xmltodict.parse(data.content)
            mapping_list = {"type":{"org":"T007:법령"},"title":{"행정규칙명":"org"},"publisher":{"소관부처명":"org"},"date":{"발령일자":"issued","시행일자":"available"},"identifier":{"행정규칙ID":"site","행정규칙상세링크":"url"},"relation":{"제개정구분명":"isPartOF"}}
            unrefined_df = xmlObject['AdmRulSearch']['admrul']
            df = []
            for i in range(len(unrefined_df)):
                del(unrefined_df[i]["@id"])
                df.append(unrefined_df[i]) 

        queryset = []
        df_len =  len(df)

        for k in range(df_len):
            new_dict = {}
            for i, j in mapping_list.items():
                added_dict ={}
                if i == "type":
                    new_dict[i] = j
                elif i != 'language':
                    for key,value in j.items():
                        added_dict[value] = df[k][key]
                    new_dict[i]=added_dict
                else:
                    for key,value in j.items():
                        added_dict[key] = value
                    new_dict[i] = added_dict
            queryset.append(new_dict)  

        if content_num == 1:
            serializer = JSONSerializer(queryset, many = True)
        elif content_num == 2 :
            serializer = JSON_1Serializer(queryset, many = True)
        elif content_num == 3 :
            serializer = JSON_2Serializer(queryset, many = True)

        return Response(serializer.data)


def JSON(request):
    if request.method == "POST":
        page_num = request.POST["page_num"]
        service_key = request.POST["service_key"]
        page_num = page_num.replace(" ","")
        
        page_num1 = 'page='+page_num
        service_key1 = service_key.replace('page=1', page_num1)
        try:
            int_page_num = int(page_num)
            if "https://www.law.go.kr/DRF/lawSearch.do" in service_key1:
                if "target=law" in service_key1:
                    data_name = "현행법령"
                    data = req.get(service_key1)
                    xmlObject = xmltodict.parse(data.content)
                    mapping_list = {"type":{"org":"{T007:법령}"},"title":{"법령명한글":"org"},"subjects":{"법령약칭명":"org"},"publisher":{"소관부처명":"org"},"date":{"공포일자":"issued","시행일자":"available"},"language":{"org":"ko"},"identifier":{"법령일련번호":"site","법령상세링크":"url"},"relation":{"제개정구분명":"isPartOF"}}
                    unrefined_df = xmlObject['LawSearch']['law']
                    df = []
                    for i in range(len(unrefined_df)):
                        del(unrefined_df[i]["@id"])
                        df.append(unrefined_df[i])

                elif "target=admrul" in service_key1:
                    data_name = "행정규칙"
                    data = req.get(service_key1)
                    xmlObject = xmltodict.parse(data.content)
                    mapping_list = {"type":{"org":"{T007:법령}"},"title":{"행정규칙명":"org"},"publisher":{"소관부처명":"org"},"date":{"발령일자":"issued","시행일자":"available"},"identifier":{"행정규칙ID":"site","행정규칙상세링크":"url"},"relation":{"제개정구분명":"isPartOF"}}
                    unrefined_df = xmlObject['AdmRulSearch']['admrul']
                    df = []
                    for i in range(len(unrefined_df)):
                        del(unrefined_df[i]["@id"])
                        df.append(unrefined_df[i])
                else:
                    error_message = "오류."
                    return render(request,'polls/Forjson.html',{"error_message":error_message,"page_num":page_num,"service_key":service_key})
        

            elif "https://api.odcloud.kr/api/" in service_key1:
                data_name = "전문자료"
                mapping_list = {'title':{'전문자료 메인 제목':'org'},'subjects':{'주제1':'org1','주제2':'org2','주제3':'org3','전문자료 문서 타입':'org4'},'description':{'전문자료 문서 목차':'toc','전문자료 문서 새요약':'summary'},'publisher':{'전문자료 부서 코드':'org'},'contributors':{'전문자료 문서 저자':'author','전문자료 등록자':'donator'},'date':{'전문자료 등록 일자':'registered','전문자료 승인 일자':'available'},'language':{"org":"ko"},'identifier':{'전문자료 문서 아이디':'site'}}
                df = pd.read_json(service_key1)['data']
                
            else:
                error_message = "오류."
                return render(request,'polls/Forjson.html',{"error_message":error_message,"page_num":page_num,"service_key":service_key})
        except:
            error_message = "오류."
            return render(request,'polls/Forjson.html',{"error_message":error_message,"page_num":page_num,"service_key":service_key})
        

        
        key_list = list(df[0].keys())
        df_len =  len(df)
        df_len_list = [i+1 for i in range(df_len)]


        
        first_key = key_list[0]
        last_key = key_list[len(key_list)-1]
        Values_list = []
        for i in range(df_len):
            Values_list.append(df[i])

        
        modified_list = []
        for k in range(df_len):
            new_dict = {}
            for i, j in mapping_list.items():
                added_dict ={}
                if i == "type":
                    new_dict[i] = j
                elif i != 'language':
                    for key,value in j.items():
                        added_dict[value] = df[k][key]
                    new_dict[i]=added_dict
                else:
                    for key,value in j.items():
                        added_dict[key] = value
                    new_dict[i] = added_dict
            modified_list.append(new_dict)

        Values_zip = zip(df_len_list, Values_list)
        concat_zip = zip(df_len_list, modified_list)

        return render(request,'polls/Forjson.html',{"data_name":data_name,"service_key":service_key,"df_len":df_len,"key_list":key_list,"Values_list":Values_list,"Values_zip":Values_zip,"first_key":first_key,"last_key":last_key,"page_num":page_num,"mapping_list":mapping_list,"concat_zip":concat_zip})
        
    return render(request,'polls/Forjson.html')

def saveDB(request):
    page_num = request.POST["checked_page_num"]
    service_key = request.POST["hidden_service_key"]
    data_name = request.POST["data_name"]

    enter_data = page_num + " 페이지를 DB에 저장하는데 성공했습니다!!"
    page_num1 = 'page='+page_num
    service_key1 = service_key.replace('page=1', page_num1)

    if data_name == "전문자료":
        mapping_list = {'title':{'전문자료 메인 제목':'org'},'subjects':{'주제1':'org1','주제2':'org2','주제3':'org3','전문자료 문서 타입':'org4'},'description':{'전문자료 문서 목차':'toc','전문자료 문서 새요약':'summary'},'publisher':{'전문자료 부서 코드':'org'},'contributors':{'전문자료 문서 저자':'author','전문자료 등록자':'donator'},'date':{'전문자료 등록 일자':'registered','전문자료 승인 일자':'available'},'language':{"org":"ko"},'identifier':{'전문자료 문서 아이디':'site'}}
        df = pd.read_json(service_key1)['data']

    elif data_name == "현행법령":
        mapping_list = {"type":{"org":"{T007:법령}"},"title":{"법령명한글":"org"},"subjects":{"법령약칭명":"org"},"publisher":{"소관부처명":"org"},"date":{"공포일자":"issued","시행일자":"available"},"language":{"org":"ko"},"identifier":{"법령일련번호":"site","법령상세링크":"url"},"relation":{"제개정구분명":"isPartOF"}}
        data = req.get(service_key1)
        xmlObject = xmltodict.parse(data.content)
        unrefined_df = xmlObject['LawSearch']['law']
        df = []
        for i in range(len(unrefined_df)):
            del(unrefined_df[i]["@id"])
            df.append(unrefined_df[i])

    elif data_name == '행정규칙':
        mapping_list = {"type":{"org":"{T007:법령}"},"title":{"행정규칙명":"org"},"publisher":{"소관부처명":"org"},"date":{"발령일자":"issued","시행일자":"available"},"identifier":{"행정규칙ID":"site","행정규칙상세링크":"url"},"relation":{"제개정구분명":"isPartOF"}}
        data = req.get(service_key1)
        xmlObject = xmltodict.parse(data.content)
        unrefined_df = xmlObject['AdmRulSearch']['admrul']
        df = []
        for i in range(len(unrefined_df)):
            del(unrefined_df[i]["@id"])
            df.append(unrefined_df[i])

    df_len =  len(df)
    df_len_list = [i+1 for i in range(df_len)]


    key_list = list(df[0].keys())
    first_key = key_list[0]
    last_key = key_list[len(key_list)-1]
    Values_list = []
    for i in range(df_len):
        Values_list.append(df[i])

    
    modified_list = []
    for k in range(df_len):
        new_dict = {}
        for i, j in mapping_list.items():
            added_dict ={}
            if i == "type":
                new_dict[i] = j
            elif i != 'language':
                for key,value in j.items():
                    added_dict[value] = df[k][key]
                new_dict[i]=added_dict
            else:
                for key,value in j.items():
                    added_dict[key] = value
                new_dict[i] = added_dict
        modified_list.append(new_dict)
    
    conn = pms.connect(host = '127.0.0.1',user = 'root', password = '1234', db = 'link', charset = 'utf8mb4')
    cur = conn.cursor()
    key_list = list(modified_list[0].keys())

    if data_name == "전문자료":
        table_name = "if_dk_item_전문자료 (META_TITLE, META_SUBJECT, META_DESC, META_PUBLISHER, META_CONTRIBUTOR, META_DATE, META_LANGUAGE, META_IDENTIFIER) values("
    elif data_name == "현행법령":
        table_name = "if_dk_item_현행법령 (META_TYPE, META_TITLE, META_SUBJECT, META_PUBLISHER, META_DATE, META_LANGUAGE, META_IDENTIFIER, META_RELATION) values("
    elif data_name == "행정규칙":
        table_name = "if_dk_item_행정규칙 (META_TYPE, META_TITLE, META_PUBLISHER, META_DATE, META_IDENTIFIER, META_RELATION) values("

    for i in modified_list:
        str1 = "INSERT INTO link." + table_name 
        
        for key, value in i.items():
            if key != key_list[len(key_list)-1]:
                added_str =  "'"+ str(value).replace("'","")+"'," 
                str1 = str1 + added_str
            else:
                added_str = "'"+str(value).replace("'","")+"'"  
                str1 = str1 + added_str

        str1 = str1 + ")"
        cur.execute(str1)

    conn.commit()
    conn.close()

    

    Values_zip = zip(df_len_list, Values_list)
    concat_zip = zip(df_len_list, modified_list)


    return render(request,'polls/Forjson.html',{"data_name":data_name,"enter_data":enter_data,"service_key":service_key,"df_len":df_len,"key_list":key_list,"Values_list":Values_list,"Values_zip":Values_zip,"first_key":first_key,"last_key":last_key,"page_num":page_num,"mapping_list":mapping_list,"concat_zip":concat_zip})
 