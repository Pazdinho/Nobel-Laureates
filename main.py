

import math
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import os
import requests
import sys


if __name__ == '__main__':
    if not os.path.exists('../Data'):
        os.mkdir('../Data')

    # Download data if it is unavailable.
    if 'Nobel_laureates.json' not in os.listdir('../Data'):
        sys.stderr.write("[INFO] Dataset is loading.\n")
        url = "https://www.dropbox.com/s/m6ld4vaq2sz3ovd/nobel_laureates.json?dl=1"
        r = requests.get(url, allow_redirects=True)
        open('../Data/Nobel_laureates.json', 'wb').write(r.content)
        sys.stderr.write("[INFO] Loaded.\n")

 


#cleaning data
def stage1():
    nobel = pd.read_json('../Data/Nobel_laureates.json')
    #first insight
    print(nobel.info())
    #how many Nan
    print(nobel.isna().sum())
    #looking for duplicates
    print(nobel.duplicated().sum())
    #dropping all the rows where the gender column does not contain any values.
    nobel.dropna(subset = ['gender'], inplace= True)
    #reseting index
    nobel.reset_index(inplace=True, drop = True)
    return nobel
#cleaning data
def stage2():
    nobel = stage1()
    #extracting country names from place_of_birth column
    lista = nobel['place_of_birth'].str.rsplit(",",n = 1,expand = True)
    #getting rid of whitespaces
    lista[1] = lista[1].str.strip()
    nobel['place_of_birth'] = lista[1]
    #to fill in empty born_in values with place_of_birth.
    for i in range(len(nobel.born_in)):
        if nobel.iloc[i,0] == "":
            nobel.iloc[i, 0] = nobel.iloc[i,8]
    #adjusting some country names
    nobel.place_of_birth.replace({'US': 'USA', 'United States': 'USA', 'U.S.': 'USA', 'United Kingdom': 'UK'}, inplace = True)
    nobel.born_in.replace({'US': 'USA', 'United States': 'USA', 'U.S.': 'USA', 'United Kingdom': 'UK'}, inplace = True)
    #droping NaN and reindexing
    nobel.dropna(subset = ['born_in'],inplace=True)
    nobel.reset_index(inplace = True, drop = True)
    return nobel
#adding new columns
def stage3():
    nobel = stage2()
    #to calculate age when a laureate received the Nobel Prize.
    nobel['date_of_birth'] = pd.to_datetime(nobel['date_of_birth'])
    nobel['year_born'] = nobel['date_of_birth'].dt.year
    nobel['age_of_winning'] = nobel['year'] - nobel['year_born']

    #year of brith vs age of winning
    #print(nobel['year_born'].to_list(), nobel['age_of_winning'].to_list(), sep='\n')

    return nobel

#pie chart
def stage4():
    nobel = stage3()
    #to calculate the number of laureates from each country
    freq = nobel.born_in.value_counts().to_dict()

    #<25 falling into 'other country" category
    for i, c in enumerate(nobel.born_in):
        if freq[c] < 25:
            nobel.iloc[i,0] = 'Other countries'
    nobel['born_in'] = nobel['born_in'].apply(lambda x: 'Other countries' if nobel['born_in'].value_counts()[x] < 25 else x)
    #plotting pie chart 'Nobel laureates countries of origin'
    plt.figure(figsize=(12, 12))
    explode = [0, 0, 0, 0.08, 0.08, 0.08, 0.08, 0.08, 0.08]
    colors = ['blue', 'orange', 'red', 'yellow', 'green', 'pink', 'brown', 'cyan', 'purple']
    values = nobel.born_in.value_counts()

    plt.pie(nobel.born_in.value_counts(),explode = explode,  colors = colors,labels = values.index,autopct=lambda pct: f'{pct:.2f}%\n({values.sum()*pct/100:.0f})')
    plt.show()

#bar plot
def stage5():
    nobel = stage3()
    #dropping all the rows where the category column does not contain any values
    to_delete = nobel['category'][nobel.category == ""]
    nobel.drop(to_delete.index, axis = 0,inplace=True)
    nobel.reset_index(inplace = True, drop = True)

    #plotting figure 'The total count of male and female Nobel Prize winners by categories'
    plt.figure(figsize=(10, 10))

    female  = nobel[nobel.gender == 'female'].groupby('category').agg({'category' : 'count'})
    male  = nobel[nobel.gender == 'male'].groupby('category').agg({'category' : 'count'})

    xaxis = np.arange(len(male.index))
    plt.bar(xaxis - 0.2,male.category.tolist(), width=0.4, label = 'Males',color = 'blue')
    plt.bar(xaxis + 0.2,female.category.tolist(), width=0.4, label = 'Females',color = 'crimson')
    plt.xticks(xaxis, male.index)
    plt.xlabel('Category', fontsize=14)
    plt.ylabel('Nobel Laureates Count', fontsize=14)
    plt.title('The total count of male and female Nobel Prize winners by categories', fontsize=20)
    plt.legend()
    plt.show()
    return nobel

#box plot
def stage6():
    nobel = stage5()
    #plotting a figure 'Distribution of Ages by Category'
    plt.figure(figsize=(10, 10))
    data = []
    for i in nobel.category.unique():
        data_sub = nobel['age_of_winning'][nobel.category == i]
        data.append(data_sub)

    #adding all categories data at the end
    data.append(nobel['age_of_winning'])
    labels = nobel.category.unique().tolist()
    labels.append('All categories')
    print(nobel.category)

    plt.xlabel('Category', fontsize=14)
    plt.ylabel('Age of Obtaining the Nobel Prize', fontsize=14)
    plt.title('Distribution of Ages by Category', fontsize=20)
    plt.boxplot(data, labels = labels,showmeans=True)
    plt.show()


#stage1()
#stage2()
#stage3()
#stage4()
#stage5()
stage6()
