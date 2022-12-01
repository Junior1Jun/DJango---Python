# Create your views here.
from django.http import HttpResponse
from django.shortcuts import render
from django.template import loader
from django.core.files.storage import FileSystemStorage  # 파일저장
import os

from .models import Question
import pandas as pd
from sklearn.datasets import load_iris
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier

data = load_iris()
X_data = pd.DataFrame(data.data, columns = data.feature_names)
Y_data = pd.Series(data.target, name = 'Targets')
X_train,X_test,Y_train,Y_test = train_test_split(X_data, Y_data , test_size = 0.2)

model = RandomForestClassifier()
model.fit(X_train, Y_train)

def index(request):
   latest = Question.objects.order_by("id")[:1]
    # output = ", ".join([q.question_text for q in latest])
   template = loader.get_template('polls/index.html')
   context = {"listes":latest,}
   return HttpResponse(template.render(context,request))

def detail(request,question_id):
    return HttpResponse("You're looking at question %s." % question_id)

def results(request,question_id):
    return HttpResponse("You're looking at the results of question %s." % question_id)

def vote(request, question_id):
    return HttpResponse("You're voting on question %s." % question_id)

def predictor(request):
    if request.method == 'POST':
        sepal_length = request.POST["sepal_length"]
        sepal_width = request.POST["sepal_width"]
        petal_length = request.POST["petal_length"]
        petal_width = request.POST["petal_width"]
        y_pred = model.predict([[sepal_length, sepal_width, petal_length, petal_width]])
        if y_pred[0] == 0 :
            result = 'Setosa'
        elif y_pred[0] == 1 :
            result = 'Verscicolor'
        else:
            result = 'Virginica'
        return render(request, 'polls/user.html', {'result' : result})
    return render(request, 'polls/user.html')

def CSV(request):
    if request.method == 'POST':
        try:
            col_li = []
            total_data_li = []
            file = request.FILES['fileInput']
            fs = FileSystemStorage()
            filename = fs.save("파일명.csv", file)
            try:
                dfs = pd.read_csv("C:/Users/user/mysite/파일명.csv",encoding = 'ansi').head(5)
            except:
                dfs = pd.read_csv("C:/Users/user/mysite/파일명.csv",encoding = 'utf-8').head(5)
            
            os.remove("C:/Users/user/mysite/파일명.csv")
            df_len = len(dfs)
            columns = dfs.columns

            for i in columns:
                col_li.append(i)

            for i in range(df_len):
                data_li = []
                for j in columns:
                    data_li.append(dfs.loc[i,j])
                total_data_li.append(data_li)
            

            return render(request,'polls/index.html',{'result':col_li,"data":total_data_li,"file": file})
        except:
            return render(request,'polls/index.html') 

    return render(request,'polls/index.html')

def CSV2(request):
    if request.method == 'POST':

        file_name = request.POST['hidden_name']

        col_li = request.POST['columns']
        col_li = col_li.lstrip("[")
        col_li = col_li.rstrip("]")
        col_li = col_li.replace("'" , "")
        col_li = col_li.split(", ")

        total_data_li = request.POST['datas']
        total_data_li = total_data_li[1:len(total_data_li)-1]
        total_data_li = total_data_li.split("], ")


        new_data_li = []
        for i in total_data_li:
            elements = i + "]"
            elements = elements.lstrip("[")
            elements = elements.rstrip("]")
            elements = elements.replace("'","")
            elements = elements.split(", ")
            new_data_li.append(elements)

        exclusive_list = []

        df = pd.DataFrame(new_data_li, columns = col_li)
        
        for i in col_li:
            exclusive_num = request.POST[i]
            if exclusive_num == "1":
                booleans = True
            else:
                booleans = False
            exclusive_list.append(booleans)
        
        df = df.loc[:, exclusive_list]

        df_len = len(df)
        columns = df.columns

        updated_col_li = []

        for i in columns:
            updated_col_li.append(i)


        updated_total_data_li = []

        for i in range(df_len):
            data_li = []
            for j in updated_col_li:
                data_li.append(df.loc[i,j])
            updated_total_data_li.append(data_li)


        return render(request,'polls/index.html',{'result':col_li,"data":new_data_li,"updated_col_li":updated_col_li,"updated_total_data_li":updated_total_data_li,"file":file_name})
    return render(request,'polls/index.html') 


def JSON(request):
    if request.method == "POST":
        page_num = request.POST["page_num"]
        page_num = page_num.replace(" ","")
        page_num1 = 'page='+page_num
        service_key = request.POST["service_key"]
        service_key1 = service_key.replace('page=1', page_num1)
        try:
            int_page_num =int(page_num)
            df = pd.read_json(service_key1)
        except:
            error_message = "숫자를 입력하시오."
            return render(request,'polls/Forjson.html',{"error_message":error_message,"page_num":page_num,"service_key":service_key})
        

        df_len =  len(df)
        df_len_list = [i+1 for i in range(df_len)]


        key_list = list(df['data'][0].keys())
        first_key = key_list[0]
        last_key = key_list[len(key_list)-1]
        Values_list = []
        for i in range(df_len):
            Values_list.append(df['data'][i])

        mapping_list = {'제목':{'전문자료 메인 제목':'org'},'주제어':{'주제1':'org1','주제2':'org2','주제3':'org3','전문자료 문서 타입':'org4'},'설명':{'전문자료 문서 목차':'toc','전문자료 문서 새요약':'summary'},'발행기관':{'전문자료 부서 코드':'org'},'원작자':{'전문자료 문서 저자':'author','전문자료 등록자':'donator'},'날짜':{'전문자료 등록 일자':'registered','전문자료 승인 일자':'available'},'언어':'ko','식별자':{'전문자료 문서 아이디':'site'}}

        modified_list = []
        for k in range(df_len):
            old_dict=df['data'][k]
            new_dict = {}
            for key, values in mapping_list.items():
                if key != '언어':
                    added_dict ={}
                    for i,j in values.items():
                        added_dict[j] = old_dict[i]
                    new_dict[key]=added_dict

                else:
                    added_dict ={}
                    added_dict['org'] = "ko"
                    new_dict[key] = added_dict
            modified_list.append(new_dict)

        Values_zip = zip(df_len_list, Values_list)
        concat_zip = zip(df_len_list, modified_list)
        return render(request,'polls/Forjson.html',{"service_key":service_key,"df_len":df_len,"key_list":key_list,"Values_list":Values_list,"Values_zip":Values_zip,"first_key":first_key,"last_key":last_key,"page_num":page_num,"mapping_list":mapping_list,"concat_zip":concat_zip})

    return render(request,'polls/Forjson.html')


# def JSON2(request):
#     if request.method == "POST":
#         page_num = request.POST["checked_page_num"]
#         service_key = request.POST["service_key"]
#         df = pd.read_json("https://api.odcloud.kr/api/15092231/v1/uddi:f485c10f-f5d2-4a00-a993-b85d929565ec?page=" + page_num + "&perPage=10&serviceKey=" + service_key)
        
#         mapping_list = {'제목':{'전문자료 메인 제목':'org'},'주제어':{'주제1':'org1','주제2':'org2','주제3':'org3','전문자료 문서 타입':'org4'},'설명':{'전문자료 문서 목차':'toc','전문자료 문서 새요약':'summary'},'발행기관':{'전문자료 부서 코드':'org'},'원작자':{'전문자료 문서 저자':'author','전문자료 등록자':'donator'},'날짜':{'전문자료 등록 일자':'registered','전문자료 승인 일자':'available'},'언어':'ko','식별자':{'전문자료 문서 아이디':'site'}}

#         modified_list = []
#         df_len =  len(df)

#         for k in range(df_len):
#                 old_dict=df['data'][k]
#                 new_dict = {}
#                 for key, values in mapping_list.items():
#                     if key != '언어':
#                         added_dict ={}
#                         for i,j in values.items():
#                             added_dict[j] = old_dict[i]
#                         new_dict[key]=added_dict

#                     else:
#                         added_dict ={}
#                         added_dict['org'] = "ko"
#                         new_dict[key] = added_dict
#                 modified_list.append(list(new_dict.values()))
        
#         toCSV = pd.DataFrame(modified_list,columns = list(mapping_list.keys()))



