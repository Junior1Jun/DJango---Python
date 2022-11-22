from django.shortcuts import render

# Create your views here.
from django.http import HttpResponse
from django.template import loader
from .models import Question
from django.core.files.storage import FileSystemStorage  # 파일저장
import pandas as pd
import os


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
