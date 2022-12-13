# Create your views here.
from django.shortcuts import render

import xmltodict
import requests as req 

from rest_framework.response import Response
from rest_framework.views import APIView
from .serializers import JSON_jeonmoon_Serializer
from .serializers import JSON_hyeonhang_Serializer
from .serializers import JSON_hangjeong_Serializer


import pymysql as pms
import pandas as pd

# Forjson.html로부터 페이지 수와(page_num) 인증키를(content_num) 받아서 원본데이터 수집하고,
# 매핑화된 데이터만을 rest API로 변환 후, 화면에 띄워주는 클래스 및 함수. 
# 여기서 Forjson.html로부터 받은 content_num이 1이면 "전문자료" // 2이면 "현행법령" // 3이면 "행정규칙"의 데이터를 이 JSONListAPI 클래스의 메서드 get이 수집하게 됨.
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
        # 표준 메타데이터 셋에 맞게 매핑된, 데이터셋의 각 행을 저장하게 될 리스트임.          

        df_len =  len(df)
        # 행의 개수


        # 여기부터 원본 데이터를 표준 메타데이터 셋에 맞게 매핑 후, 매핑한 각 행들을 queryset에 추가하는 코드.
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
        # 여기까지 원본 데이터를 표준 메타데이터 셋에 맞게 매핑 후, 매핑한 각 행들을 queryset에 추가하는 코드.


        # 변수 content_num에 저장된 값에 따라 이에 대응되는, 사전에 지정해준 Serializer클래스(JSON_jeonmoon_Serializer, ..)로 
        # query 변수에 저장된 데이터셋을 json 형태의 데이터셋으로 변환 
        if content_num == 1:
            serializer = JSON_jeonmoon_Serializer(queryset, many = True)
        elif content_num == 2 :
            serializer = JSON_hyeonhang_Serializer(queryset, many = True)
        elif content_num == 3 :
            serializer = JSON_hangjeong_Serializer(queryset, many = True)

        return Response(serializer.data)
        # serializer.data에 저장된 json형태의 데이터셋을 Response 모듈을 사용하여 REST API로 변환


# Forjson.html로부터 받은 인증키와 페이지 수로 원본 데이터를 수집하고, 표준화된 메타데이터 형식에 맞게 매핑 후, 
# 원본데이터와 매핑화된 데이터를 다시 Forjson.html에 보내주는 함수 
def JSON(request):
    if request.method == "POST":
    # Forjson.html의 submit을 통해 POST 요청 받았으면,

        page_num = request.POST["page_num"]
        service_key = request.POST["service_key"]
        page_num = page_num.replace(" ","")
        # Forjson.html에서 name이 page_num인 input value 값을 page_num에 저장
        # Forjson.html에서 name이 service_key input value 값을 service_key 저장 (오픈 api 호출을 위한 인증키)
        # 인증키에 'page=1'이라는 문자열이 있음을 주목
        # 사용자가 Forjson.html에서 name이 page_num인 input에 공백 하나 띄우고 페이지 숫자를 대입했을 수 있으므로, replace 메서드를 통해 공백 제거

        page_num1 = 'page='+page_num
        service_key1 = service_key.replace('page=1', page_num1)
        # 예를 들어, page_num에 값이 2가 있으면, page_num1에 "page="+"2" = "page=2"를 대입
        # 변수 service_key의 값에서 'page=1'을 page_num1에 저장된 값으로 변경하고, 변경된 문자열을 service_key1에 저장.


        try:
            int_page_num = int(page_num)
            # 페이지 수가 아닌 다른 값이 입력되면 except문으로 이동.
        except:
            error_message = "원본데이터 수집 ERROR!!"
            error_code = "EF_R_003"
            cause = "올바른 페이지 수를 입력해주시기 바랍니다."
            return render(request,'polls/Forjson.html',{"page_num":page_num,"service_key1":service_key1,"cause":cause,"error_code":error_code,"error_message":error_message,"page_num":page_num,"service_key":service_key})

        try:
        # Forjson.html에서 인증키를 잘못 입력하면,
        # except문의 코드 또는 try문의 else 코드가 실행됨.

            if "https://www.law.go.kr/DRF/lawSearch.do" in service_key1:
                if "target=law" in service_key1:  # 현행법령 데이터셋을 요구하는 인증키라면, 
                    data_name = "현행법령"         # 웹 사이트에 띄울 문자열 값을 data_name 변수에 저장

                    if int_page_num >= 263 or int_page_num <= 0:
                        error_message = "데이터수집 ERROR 발생!! " 
                        error_code = "EF_R_003"
                        cause = "현행법령의 페이지 수 범위는 1 ~ 262쪽입니다."
                        return render(request, 'polls/Forjson.html',{"page_num":page_num,"service_key1":service_key1,"cause":cause,"error_code":error_code,"error_message":error_message,"data_name":data_name,"service_key":service_key,"page_num":page_num})
                    

                    data = req.get(service_key1)   # requests 라이브러리의 get메서드를 통해, service_key1에 저장된 인증키 값으로 xml파일 불러오기 >> data 변수에 xml파일 저장
                    xmlObject = xmltodict.parse(data.content) # data에 있는 xml파일 내용들을 파싱하여, xmlObject에 저장 >> 딕셔너리 형태로 저장됨.

                    mapping_list = {"type":{"org":"{T007:법령}"},"title":{"법령명한글":"org"},"subjects":{"법령약칭명":"org"},"publisher":{"소관부처명":"org"},"date":{"공포일자":"issued","시행일자":"available"},"language":{"org":"ko"},"identifier":{"법령일련번호":"site","법령상세링크":"url"},"relation":{"제개정구분명":"isPartOF"}}
                    # 현행법령에 대응되는 메타데이터 리스트를 지정.

                    unrefined_df = xmlObject['LawSearch']['law']
                    # xmlObject의 'LawSearch'키에 대응되는 value는 딕셔너리 형태이고, 이 딕셔너리 value의 'law'키에 대응되는 value는 
                    # 20개의 dict 형식 데이터를(행*열에서 행에 해당) 원소로 가지는 리스트. >> [{'@id': '1','법령일련번호': '232157', ...},{'@id': '2',..  ...}]
                    # 이 리스트를 unrefined_df에 저장.   

                    df = []
                    for i in range(len(unrefined_df)):
                        del(unrefined_df[i]["@id"])
                        df.append(unrefined_df[i])
                    # unrefined_df에 저장된 각 원소에 "@id"는 필요없는 데이터이므로, 각 원소에 있는 @id를 모두 삭제 
                    neccessary_col = ['title', 'identifier']
                    



                elif "target=admrul" in service_key1:  # 행정규칙 데이터셋을 요구하는 인증키라면,
                    data_name = "행정규칙"              # 위의 현행법령과 동일.

                    if int_page_num >= 968 or int_page_num <= 0:
                        error_message = "데이터수집 ERROR 발생!! " 
                        error_code = "EF_R_003"
                        cause = "행정규칙의 페이지 수 범위는 1 ~ 967쪽입니다."
                        return render(request, 'polls/Forjson.html',{"page_num":page_num,"service_key1":service_key1,"cause":cause,"error_code":error_code,"error_message":error_message,"data_name":data_name,"service_key":service_key,"page_num":page_num})
                  
                    data = req.get(service_key1)
                    xmlObject = xmltodict.parse(data.content)
                    mapping_list = {"type":{"org":"{T007:법령}"},"title":{"행정규칙명":"org"},"publisher":{"소관부처명":"org"},"date":{"발령일자":"issued","시행일자":"available"},"identifier":{"행정규칙ID":"site","행정규칙상세링크":"url"},"relation":{"제개정구분명":"isPartOF"}}
                    unrefined_df = xmlObject['AdmRulSearch']['admrul']
                    df = []
                    for i in range(len(unrefined_df)):
                        del(unrefined_df[i]["@id"])
                        df.append(unrefined_df[i])
                    neccessary_col = ['title', 'identifier']
                      

                else: # service_key1에 있는 인증키를 통하여 xml형식의 데이터셋을 json형식으로 수집
                    data_name = "알 수 없는 데이터"
                    data = req.get(service_key1)
                    xmlObject = xmltodict.parse(data.content)
                    xmlObject_KEYlist = list(xmlObject.keys())
                    refined_dict = xmlObject[xmlObject_KEYlist[0]]
                    refined_dict_KEYlist = list(refined_dict.keys())
                    df = refined_dict[refined_dict_KEYlist[len(refined_dict_KEYlist)-1]]
                    

            elif "https://api.odcloud.kr/api/" in service_key1 and "f485c10f-f5d2-4a00-a993-b85d929565ec" in service_key1 : # 전문자료 데이터셋을 요구하는 인증키라면, 
                data_name = "전문자료" 
                mapping_list = {'title':{'전문자료 메인 제목':'org'},'subjects':{'주제1':'org1','주제2':'org2','주제3':'org3','전문자료 문서 타입':'org4'},'description':{'전문자료 문서 목차':'toc','전문자료 문서 새요약':'summary'},'publisher':{'전문자료 부서 코드':'org'},'contributors':{'전문자료 문서 저자':'author','전문자료 등록자':'donator'},'date':{'전문자료 등록 일자':'registered','전문자료 승인 일자':'available'},'language':{"org":"ko"},'identifier':{'전문자료 문서 아이디':'site'}}
                neccessary_col = ['title', 'description', 'identifier']
                
                if int_page_num >= 2401 or int_page_num <= 0:
                    error_message = "데이터수집 ERROR 발생!! " 
                    error_code = "EF_R_003"
                    cause = "전문자료의 페이지 수 범위는 1 ~ 2400쪽입니다."
                    return render(request, 'polls/Forjson.html',{"page_num":page_num,"service_key1":service_key1,"cause":cause,"error_code":error_code,"error_message":error_message,"data_name":data_name,"service_key":service_key,"page_num":page_num})
                df = pd.read_json(service_key1)['data'] 
                # df[0]['전문자료 문서 새요약'] = None

                
                
                # df에 {"전문자료 등록 일자":"2011-08-01","전문자료 등록자":" ",..},{"전문자료 등록 일자":"2011-08-16","전문자료 등록자":" ",..}, ...  
                # 즉, 원본 데이터 셋의 json 형식인 행들을 저장.
                
            else: # 전문자료 // 현행법령 // 행정규칙 데이터셋이 아니라면, xml 또는 json 형식의 파일을 가져오고, data_name 변수에 '알 수 없는 데이터' 문자열 저장.
                try:
                    data_name = "알 수 없는 데이터"
                    df = pd.read_json(service_key1)['data'] 
                except:
                    data_name = "알 수 없는 데이터"
                    data = req.get(service_key1)
                    xmlObject = xmltodict.parse(data.content)
                    xmlObject_KEYlist = list(xmlObject.keys())
                    refined_dict = xmlObject[xmlObject_KEYlist[0]]
                    refined_dict_KEYlist = list(refined_dict.keys())
                    df = refined_dict[refined_dict_KEYlist[len(refined_dict_KEYlist)-1]]

        except: # service_key1에 잘못된 인증키가 입력되어 있으면 에러메시지, 사용자가 입력한 페이지번호와 인증키를 Forjson.html에 전달
            error_message = "원본데이터 수집 ERROR!!"
            error_code = "EF_R_003"
            cause = " 정확한 인증키를 입력해주시기 바랍니다."
            return render(request,'polls/Forjson.html',{"page_num":page_num,"service_key1":service_key1,"cause":cause,"error_code":error_code,"error_message":error_message,"page_num":page_num,"service_key":service_key})


        key_list = list(df[0].keys())    # df[0].keys()는 전문자료를 예로 들면, ["전문자료 등록 일자","전문자료 등록자", ...] 등 원본데이터의 컬럼명 리스트를 가지고 있다.
        df_len =  len(df)                # df_len 변수는 df에 있는 행의 개수를 저장함. 
        df_len_list = [i+1 for i in range(df_len)]     # df_len_list는 1부터 df에 저장된 행의 개수까지의 숫자를 원소로 가지는 리스트
                                                       # 예를 들어, df에 행의 개수가 20개이면 df_len_list는 [1 ,2 ,3 , .....,20] 리스트를 가짐.

        first_key = key_list[0]                        # 원본 데이터의 첫 번째 컬럼을 저장
        last_key = key_list[len(key_list)-1]           # 원본 데이터의 마지막 번째 컬럼을 저장

        Values_list = []                               
        # 원본 데이터의 각 행을 저장하게 될 리스트임.
        
        for i in range(df_len):                        
            Values_list.append(df[i])
        # 원본 데이터의 각 행을 Values_list에 저장함.

        Values_zip = zip(df_len_list, Values_list)
        # Values_zip >> 원본 데이터 셋과 "df_len_list = [1, 2, ..., 행의 갯수]"를 가지는 zip 형식의 iterator를 가짐.

        if data_name == "알 수 없는 데이터":           # 전문자료 // 현행법령 // 행정규칙 이외의 데이터셋이면, data_name에 '알 수 없는 데이터' 문자열이 저장되어 있음. 
            error_message = "매핑 ERROR 발생!!"        # error_message 변수에 "매핑 ERROR 발생!!" 문자열을 저장해놓고 error_message, data_name 등을 Forjson.html에 전달
            error_code = "EF_R_002"
            cause = "전문자료 // 현행법령 // 행정규칙 이외의 데이터셋을 수집하셨습니다."
            return render(request,'polls/Forjson.html',{"page_num":page_num,"service_key1":service_key1,"cause":cause,"error_code":error_code,"error_message":error_message,"data_name":data_name,"service_key":service_key,"df_len":df_len,"key_list":key_list,"Values_zip":Values_zip,"first_key":first_key,"last_key":last_key,"page_num":page_num})

        try: # 전문자료 // 현행법령 // 행정규칙 데이터셋인데, 원본 데이터의 메타 데이터 변경 등의 이유로 매핑에 실패할 때는 except문으로 넘어감.
            modified_list = []
            # 표준 메타데이터 셋에 맞게 매핑된, 데이터의 각 행을 저장하게 될 리스트임.
        
            # 여기부터 원본 데이터를 표준 메타데이터 셋에 맞게 매핑 후, 매핑한 각 행들을 modified_list에 추가하는 코드.
            for k in range(df_len):
                new_dict = {}
                for i, j in mapping_list.items():
                    mapping_col = i                       # 매핑될 컬럼들 중, 매핑이 안되는 컬럼명이 mapping_col 변수에 저장됨.    
                    added_dict ={}
                    if i == "type":
                        new_dict[i] = j
                    elif i != 'language':
                        for key,value in j.items():
                            unmapping_col = key               #원본 데이터의 컬럼들 중, 매핑이 안되는 컬럼명이 unmapping_col 변수에 저장됨.    
                            added_dict[value] = df[k][key]
                        if i in neccessary_col:
                            checking_blank_list = list(added_dict.values())
                            blank = True

                            for blank_element in checking_blank_list:
                                if blank_element != None:
                                    blank = False

                            if blank == True:
                                error_message = "데이터수집 ERROR 발생!! " 
                                error_code = "EF_R_003"
                                cause = i + "에 해당하는 원본데이터가 존재하지 않습니다."
                                return render(request, 'polls/Forjson.html',{"page_num":page_num,"service_key1":service_key1,"cause":cause,"error_code":error_code,"error_message":error_message,"data_name":data_name,"service_key":service_key,"df_len":df_len,"key_list":key_list,"Values_zip":Values_zip,"first_key":first_key,"last_key":last_key,"page_num":page_num})
                            
                        new_dict[i]=added_dict
                    else:
                        for key,value in j.items():
                            added_dict[key] = value
                        new_dict[i] = added_dict
                modified_list.append(new_dict)
            # 여기까지 원본 데이터를 표준 메타데이터 셋에 맞게 매핑 후, 매핑한 각 행들을 modified_list에 추가하는 코드.
    
            concat_zip = zip(df_len_list, modified_list)
            # concat_zip >> 매핑된 데이터 셋과 "df_len_list = [1, 2, ..., 행의 갯수]"를 가지는 zip 형식의 iterator를 가짐.

            return render(request,'polls/Forjson.html',{"data_name":data_name,"service_key":service_key,"df_len":df_len,"key_list":key_list,"Values_zip":Values_zip,"first_key":first_key,"last_key":last_key,"page_num":page_num,"concat_zip":concat_zip})
            # 매핑을 성공하였다면, 원본 데이터셋이름, 원본 데이터셋, 매핑된 데이터셋 등을 Forjson.html에 전달함.

        except:    
            error_message = "증분데이터 ERROR 발생!!"
            error_code = "EF_R_001"
            before_error = str(mapping_list).split(unmapping_col)[0]
            after_error = str(mapping_list).split(unmapping_col)[1]
            cause = "수정되어야 할 메타데이터 부분은 " + mapping_col +"의 "+unmapping_col+" 입니다."
            return render(request,'polls/Forjson.html',{"before_error":before_error,"after_error":after_error,"page_num":page_num,"service_key1":service_key1,"mapping_list":mapping_list,"unmapping_col":unmapping_col,"error_message":error_message,"error_code":error_code,"cause":cause,"data_name":data_name,"service_key":service_key,"df_len":df_len,"key_list":key_list,"Values_zip":Values_zip,"first_key":first_key,"last_key":last_key,"page_num":page_num})
            # # 전문자료 // 현행법령 // 행정규칙 데이터셋인데, 매핑에 실패할 때는 매핑에 실패한 컬럼명들과 에러메시지 등을 출력

    return render(request,'polls/Forjson.html')
    # Forjson.html의 submit을 통해 POST 요청 받은 것이 아니면(Forjson.html화면을 단순히 url주소를 입력해서 띄울 때를 의미함.) 아무 데이터 전달없이 Forjson.html로 넘어감. 


# saveDB : Forjson.html으로부터 받은 인증키와 페이지 수를 받은 다음, 인증키와 페이지 수를 통해 얻은 데이터 셋을 매핑하고 MySQL DB에 저장하는 함수.
def saveDB(request):
    page_num = request.POST["checked_page_num"]          
    service_key = request.POST["hidden_service_key"]
    data_name = request.POST["data_name"]
    # Forjson.html에서 name이 checked_page_num인 input value 값을 page_num에 저장 >> 지정된 페이지 수
    # Forjson.html에서 name이 hidden_service_key인 input value 값을 service_key 저장 >> 지정된 인증키
    # Forjson.html에서 name이 data_name input value 값을 data_name 저장 >> 지정된 데이터셋 이름


    enter_data = page_num + " 페이지를 DB에 저장하는데 성공했습니다!!"
    page_num1 = 'page='+page_num
    service_key1 = service_key.replace('page=1', page_num1)
    # enter_data >> 지정된 페이지에 있는 데이터셋을 DB에 저장성공 했으면, Forjson.html에 띄워 줄 문구를 저장
    # 예를 들어, page_num에 값이 2가 있으면, page_num1에 "page="+"2" = "page=2"를 대입
    # 변수 service_key의 값에서 'page=1'을 page_num1에 저장된 값으로 변경하고, 변경된 문자열을 service_key1에 저장.


    if data_name == "전문자료": # DB에 저장할 데이터셋이 전문자료에 해당되면,
        mapping_list = {'title':{'전문자료 메인 제목':'org'},'subjects':{'주제1':'org1','주제2':'org2','주제3':'org3','전문자료 문서 타입':'org4'},'description':{'전문자료 문서 목차':'toc','전문자료 문서 새요약':'summary'},'publisher':{'전문자료 부서 코드':'org'},'contributors':{'전문자료 문서 저자':'author','전문자료 등록자':'donator'},'date':{'전문자료 등록 일자':'registered','전문자료 승인 일자':'available'},'language':{"org":"ko"},'identifier':{'전문자료 문서 아이디':'site'}}
        df = pd.read_json(service_key1)['data']
        # 매핑 리스트 지정 및 지정된 페이지의 전문자료 데이터셋을 가져옴. 

    elif data_name == "현행법령": # DB에 저장할 데이터셋이 현행법령에 해당되면,
        mapping_list = {"type":{"org":"{T007:법령}"},"title":{"법령명한글":"org"},"subjects":{"법령약칭명":"org"},"publisher":{"소관부처명":"org"},"date":{"공포일자":"issued","시행일자":"available"},"language":{"org":"ko"},"identifier":{"법령일련번호":"site","법령상세링크":"url"},"relation":{"제개정구분명":"isPartOF"}}
        data = req.get(service_key1)
        xmlObject = xmltodict.parse(data.content)
        unrefined_df = xmlObject['LawSearch']['law']
        df = []
        for i in range(len(unrefined_df)):
            del(unrefined_df[i]["@id"])
            df.append(unrefined_df[i])

    elif data_name == '행정규칙': # DB에 저장할 데이터셋이 행정규칙에 해당되면,
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
    # pms모듈의 connect메서드를 통해, Mysql의 지정된 user//password에 존재하는 "link" DB을 파이썬과 연결하는 객체를 생성 후, 객체를 conn 변수에 저장.

    cur = conn.cursor()  
    # 변수 conn에 저장된 객체의 cursor 메서드를 통해, sql문을 실행하고 실행된 결과를 돌려받는 객체를 생성 후, 객체를 cur 변수에 저장.   

    key_list = list(modified_list[0].keys())
    # 매핑화된 데이터셋의 컬럼명들을 key_list에 저장함.


    if data_name == "전문자료":
        table_name = "if_dk_item_전문자료 (META_TITLE, META_SUBJECT, META_DESC, META_PUBLISHER, META_CONTRIBUTOR, META_DATE, META_LANGUAGE, META_IDENTIFIER) values("
    elif data_name == "현행법령":
        table_name = "if_dk_item_현행법령 (META_TYPE, META_TITLE, META_SUBJECT, META_PUBLISHER, META_DATE, META_LANGUAGE, META_IDENTIFIER, META_RELATION) values("
    elif data_name == "행정규칙":
        table_name = "if_dk_item_행정규칙 (META_TYPE, META_TITLE, META_PUBLISHER, META_DATE, META_IDENTIFIER, META_RELATION) values("
   

    # 여기부터 매핑화된 데이터셋을 mysql db에 추가하는 sql문을 실행해주는 코드임. (단, sql문의 실행결과만 가지고 있을 뿐, 실제로 실행결과가 db에 저장되는 코드는 아님.)
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
        # str1에 저장된 sql문을 실행 후, 실행된 결과를 저장하고 있음.
        # 하지만 이는 실행 결과만 가지고 있을 뿐, 실제로 실행 결과가 db에 적용되는 것은 아님.

    # 여기까지 매핑화된 데이터셋을 mysql db에 추가하는 sql문을 실행해주는 코드임.

    conn.commit()
    # conn의 commit 메서드를 통해, cur에 저장되어 있는 sql문 실행결과들을 mysql db에 적용.

    conn.close()
    # 저장하고자 하는 데이터셋을 mysql DB에 모두 저장하였으므로, conn의 close 메서드를 통해서 DB와의 연결을 해제함. 

    

    Values_zip = zip(df_len_list, Values_list)
    concat_zip = zip(df_len_list, modified_list)
    # Values_zip >> 원본 데이터 셋과 "df_len_list = [1, 2, ..., 행의 갯수]"를 가지는 zip 형식의 iterator를 가짐.
    # concat_zip >> 매핑된 데이터 셋과 "df_len_list = [1, 2, ..., 행의 갯수]"를 가지는 zip 형식의 iterator를 가짐.

    return render(request,'polls/Forjson.html',{"data_name":data_name,"enter_data":enter_data,"service_key":service_key,"df_len":df_len,"key_list":key_list,"Values_list":Values_list,"Values_zip":Values_zip,"first_key":first_key,"last_key":last_key,"page_num":page_num,"mapping_list":mapping_list,"concat_zip":concat_zip})
    # 원본 데이터셋 이름( 전문자료, 현행법령 등) // 인증키 // db저장 성공 메시지 // 원본 데이터 셋 // 매핑된 데이터 셋 등의 정보를 Forjson.html에 전달해줌.







