from django.shortcuts import render
import pandas as pd
import pyarrow as pa

movies_data = pd.read_parquet("static/movie_db.parquet")
titles = movies_data['title']
titles_list = titles.to_list()
indices = pd.Series(movies_data.index, index=movies_data['title'])


def get_recommendations(idx,df,offset):
    sim_scores = list(enumerate(df[idx-offset]))
    sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)
    sim_scores = sim_scores[1:25]
    movie_indices = [i[0] for i in sim_scores]
    output = titles.iloc[movie_indices]
    output.reset_index(inplace=True, drop=True)
    return output


def main(request):
 
    if request.method == 'GET':
        return render(request, 'recommender/index.html', {})
    
    if request.method == 'POST':

        data = request.POST
        movie_name = data.get('movie_name').lower()
        global titles_list
        final_recommendations = []
        titles_list = [word.lower() for word in titles_list if word]

        if movie_name in titles_list:
            idx = titles_list.index(movie_name)
            offset = 0
            df = None
            if idx < 15000:
                df = pa.parquet.read_table('static/model_01.parquet').to_pandas()
                print("loaded model 1")
            elif idx > 15000 and idx < 30000:
                offset = 15000
                df = pa.parquet.read_table('static/model_02.parquet').to_pandas()
            elif idx > 30000:
                offset = 30000
                df = pa.parquet.read_table('static/model_03.parquet').to_pandas()

            if df is not None:
                final_recommendations.extend(get_recommendations(idx,df,offset).to_list())

        print("final recommendations: ",final_recommendations)
        if final_recommendations:
            return render(request, 'recommender/result.html',{'movie_details':final_recommendations,'search_name':movie_name,'empty':''})
        else:
            return render(request, 'recommender/result.html',{'movie_details':final_recommendations,'search_name':movie_name,'empty':'yes'})
