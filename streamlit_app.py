import streamlit as st
import re
from streamlit.proto.Markdown_pb2 import Markdown
import regex
import pandas as pd
import numpy as np
import emoji
import plotly.express as px
from collections import Counter
import nltk 
from nltk.tokenize import word_tokenize
from nltk.probability import FreqDist
import datetime
import matplotlib.pyplot as plt
import seaborn as sns
from os import path
from PIL import Image
from wordcloud import WordCloud, STOPWORDS
from io import StringIO
from pathlib import Path
import io
import random
from collections import Counter
from PIL import Image,ImageDraw,ImageFont
from utils.util import startsWithDateAndTimeAndroid, startsWithDateAndTimeios, FindAuthor, getDataPointAndroid, getDataPointios, dateconv, split_count
from utils.cons import stopwords
st.set_page_config(layout="wide",page_title='Whatsapp Analyzer', page_icon=':green_book')



# #Menü gizleme
# st.markdown(""" <style>
# #MainMenu {visibility: hidden;}
# footer {visibility: hidden;}
# </style> """, unsafe_allow_html=True)

# st.markdown(
#     """
#     <style>
#     .reportview-container {
#         background: url("https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcRnhVrmQTYihPFpkrTplb0m4veDf8RQm5c13g&usqp=CAU")
#     }
#    .sidebar .sidebar-content {
#         background: url("https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcRnhVrmQTYihPFpkrTplb0m4veDf8RQm5c13g&usqp=CAU")
#     }
#     </style>
#     """,
#     unsafe_allow_html=True
# )


col1, col2, col3, col4, col5,col6,col7,col8,col9,col10,col11,col12 = st.columns([1,1,1,1,1,1,1,1,1,1,1,1])

with col12:
    increment = st.button('Beğen 👍')
    st.session_state.count = 0    
    if increment:
        st.session_state.count += 1
        metrics = open("metrics.txt", "w")
        metrics.write(str(st.session_state.count))


parsedData = []
device=''
st.title("Whatsapp Analyzer")
uploaded_file = st.file_uploader("Whatsapp konuşma metnini yükleyiniz (Sürükleyip bırakabilirsiniz)", type=['.txt'])

all_stopwords = stopwords()

if uploaded_file is not None:
    fp = io.TextIOWrapper(uploaded_file, encoding="utf-8")#open(file=str(uploaded_file.name,'r')) load_data(uploaded_file)
    device=''
    first=fp.readline()
    print(first)
    if '[' in first:
        device='ios'
    else:
        device="android"
    fp.readline() 
    messageBuffer = [] 
    date, time, author = None, None, None
    while True:
        line = fp.readline() 
        if not line: 
            break
        if device=="ios":
            line = line.strip()
            if startsWithDateAndTimeios(line):
                if len(messageBuffer) > 0:
                    parsedData.append([date, time, author, ' '.join(messageBuffer)])
                messageBuffer.clear()
                date, time, author, message = getDataPointios(line)
                messageBuffer.append(message)
            else:
                line= (line.encode('ascii', 'ignore')).decode("utf-8")
                if startsWithDateAndTimeios(line):
                    if len(messageBuffer) > 0:
                        parsedData.append([date, time, author, ' '.join(messageBuffer)])
                    messageBuffer.clear()
                    date, time, author, message = getDataPointios(line)
                    messageBuffer.append(message)
                else:
                    messageBuffer.append(line)
        else:
            line = line.strip()
            if startsWithDateAndTimeAndroid(line):
                if len(messageBuffer) > 0:
                    parsedData.append([date, time, author, ' '.join(messageBuffer)])
                messageBuffer.clear()
                date, time, author, message = getDataPointAndroid(line)
                messageBuffer.append(message)
            else:
                messageBuffer.append(line)

else:
    st.write('')

if device =='android':
        df = pd.DataFrame(parsedData, columns=['Tarih', 'Saat', 'Yazan', 'Mesaj'])
        df["Tarih"] = pd.to_datetime(df["Tarih"])
        df = df.dropna()
        df["Emoji"] = df["Mesaj"].apply(split_count)
        URLPATTERN = r'(https?://\S+)'
        df['Link Sayısı'] = df.Mesaj.apply(lambda x: re.findall(URLPATTERN, x)).str.len()
else:
        df = pd.DataFrame(parsedData, columns=['Tarih', 'Saat', 'Yazan', 'Mesaj']) # Initialising a pandas Dataframe.
        df = df.dropna()
        df["Tarih"] = df["Tarih"].apply(dateconv)
        df["Tarih"] = pd.to_datetime(df["Tarih"],format='%Y-%m-%d')
        df["Emoji"] = df["Mesaj"].apply(split_count)
        URLPATTERN = r'(https?://\S+)'
        df['Link Sayısı'] = df.Mesaj.apply(lambda x: re.findall(URLPATTERN, x)).str.len()
img_lst = []        
for i in df.Mesaj:
    if "grnt" in i or "görüntü" in i:
        img_lst.append(1)
    else:
        img_lst.append(0)
df["img"] = img_lst 
emoji_lst = []
for i in df.Mesaj:
    txt_i = emoji.demojize(i)
    emoji_lst.append(txt_i)
df["emoji"] = emoji_lst
emoji_lst3 = []
for i in df.Emoji:
    if i == []:
        emoji_lst3.append(0)
    else:
        emoji_lst3.append(1)
            
if uploaded_file is not None:
    df["emoji3"] = emoji_lst3

    df_ck = df.groupby('Tarih').agg({'emoji3' : 'sum'}).sort_values(by="emoji3",ascending=False).reset_index()
    df_en_ck = df[df.Tarih == df_ck.Tarih[0]].reset_index()
    df_en_ck = df_en_ck.drop(["Emoji","Link Sayısı","img","emoji","emoji3","index"],axis=1)
    df_en_ck.replace(df_en_ck.Mesaj[0],"GÖRSEL GÖNDERİLDİ 🖼️",inplace=True)
    #st.table(df_en_ck)


#st.markdown(df.Yazan.unique())
if uploaded_file is not None:
# line1_spacer1, line1_1, line1_spacer2 = st.columns((.1, 3.2, .1))
    link_messages= df[df['Link Sayısı']>0]
    deleted_messages=df[(df["Mesaj"] == " You deleted this message")| (df["Mesaj"] == " This message was deleted.")|(df["Mesaj"] == " You deleted this message.")]
    media_messages_df = df[(df['Mesaj'] == ' <Media omitted>')|(df['Mesaj'] == ' image omitted')|(df['Mesaj'] == ' video omitted')
                           |(df['Mesaj'] == ' sticker omitted')]
    messages_df = df.drop(media_messages_df.index)
    messages_df = messages_df.drop(deleted_messages.index)
    messages_df = messages_df.drop(link_messages.index)

    messages_df['Letter_Count'] = messages_df['Mesaj'].apply(lambda s : len(s))
    messages_df['Word_Count'] = messages_df['Mesaj'].apply(lambda s : len(s.split(' '))-1)
    messages_df["MessageCount"]=1

    messages_df["emojicount"]= df['Emoji'].str.len()
    gif1 = "https://media.giphy.com/media/JPh0EqSWeTP8eYxtyO/giphy.gif"
    gif2 = "https://media.giphy.com/media/WTXi9vPvMSNEL48v4o/giphy.gif"
    gif3 = "https://media.giphy.com/media/8kdQGAkiCBQXd1cZ2W/giphy.gif"
    gif4 = "https://media.giphy.com/media/29I0yXN4AQSGtR7IaX/giphy.gif"
    gif5 = "https://media.giphy.com/media/l3rR9t7iXV8oDKayFk/giphy.gif"
    #https://media.giphy.com/media/3o7WIEUNkMleM96wFO/giphy.gif
    
    gif6 = "https://media.giphy.com/media/KBDLn9GQFDpF3KsDFR/giphy.gif"
    gif7 = "https://media.giphy.com/media/5tLtEKu7sePSM/giphy.gif"
    gif8 = "https://media.giphy.com/media/QNAZKIao49m1MQ61fY/giphy.gif"
    gif9 = "https://media.giphy.com/media/pVb65VdiVSwLvvP52O/giphy.gif"
    gif10 = "https://media.giphy.com/media/62684ykT4QfsevRs9Q/giphy.gif"
    
    gif11 = "https://media.giphy.com/media/37tudDlY7a0w7qwqor/giphy.gif"
    gif12 = "https://media.giphy.com/media/SJ5soZsSN5pPSEXa2Q/giphy.gif"
    gif13 = "https://media.giphy.com/media/dCCrtnc5H8YgUKitoq/giphy.gif"
    gif14 = "https://media.giphy.com/media/3o7aCQ9abIk6OogiD6/giphy.gif"
    gif15 = "https://media.giphy.com/media/tZUAbVr9KvsWWbPnFM/giphy.gif"
    
    
    
    
    if len(messages_df.Yazan.drop_duplicates())>2:
        auth = messages_df.groupby('Yazan').agg({'MessageCount' : 'sum'}).sort_values(by="MessageCount",ascending=False).reset_index()

        st.subheader("Gruptaki Tipler")

        col1,col2,col3 = st.columns([1,1,1])

        with col1:
            st.markdown(f"**Mesaj Delisi : {auth.Yazan[0]}**")
            lst_gif1 = [gif1,gif2,gif3,gif4,gif5]
            st.image(random.choice(lst_gif1),width=300, caption="Grubun en aktif üyesidir. Mesajlaşmayı çok sever. Sabahlara kadar durmadan yazar, yazar, yazar...")
            yazan1 = messages_df[messages_df['Yazan'] == auth.Yazan[0]]
            text1 = " ".join(review for review in yazan1.Mesaj)
            wordcloud1 = WordCloud(stopwords=all_stopwords, background_color="white",width=800, height=400).generate(text1)
            yazan1_most = list(wordcloud1.words_.keys())
            img = Image.open("images/wp_not2.png")
            draw = ImageDraw.Draw(img)
            font = ImageFont.truetype("fonts/TitilliumWeb-Regular.ttf",size = 40, encoding='utf-8')
            baslik_font = ImageFont.truetype("fonts/Roboto-Regular.ttf",size = 30, encoding='utf-8')
            draw.text((20,70),auth.Yazan[0],font=baslik_font,fill=(150,50,150))
            draw.text((20,120),yazan1_most[0],font=baslik_font,fill=(0,0,0))
            width, height = img.size
            basewidth = 250
            wpercent = (basewidth/float(img.size[0]))
            hsize = int((float(img.size[1])*float(wpercent)))
            img2 = img.resize((basewidth,hsize), Image.ANTIALIAS)
            st.image(img2)
            auth = auth[auth.Yazan != auth.Yazan[0]]

            df = df.dropna()  
            auth2 = messages_df.groupby('Yazan').agg({'MessageCount' : 'sum','emojicount':'sum','Word_Count':'sum'}).sort_values(by="MessageCount",ascending=False).reset_index()
            auth2 = auth2.MessageCount[0].astype(str)
            st.metric("",auth2, delta='mesaj attı')

        with col2:
            st.markdown(f"**Ajan Takipçi : {auth.Yazan[round(len(auth.Yazan)/2)]}**") 
            lst_gif2 = [gif6,gif7,gif8,gif9,gif10]
            st.image(random.choice(lst_gif2),width=300,caption="Grubun orta direğidir. Bir gözü chat'te, diğer gözü kendi işlerindedir. İdeal kullanıcıdır.")
            yazan2 = messages_df[messages_df['Yazan'] == auth.Yazan[round(len(auth.Yazan)/2)]]
            text2 = " ".join(review for review in yazan2.Mesaj)
            wordcloud2 = WordCloud(stopwords=all_stopwords, background_color="white",width=800, height=400).generate(text2)
            yazan2_most = list(wordcloud2.words_.keys())
            img = Image.open("images/wp_not2.png")
            draw = ImageDraw.Draw(img)
            font = ImageFont.truetype("fonts/TitilliumWeb-Regular.ttf",size = 40, encoding='utf-8')
            baslik_font = ImageFont.truetype("fonts/Roboto-Regular.ttf",size = 30, encoding='utf-8')
            draw.text((20,70),auth.Yazan[round(len(auth.Yazan)/2)],font=baslik_font,fill=(150,50,150))
            draw.text((20,120),yazan2_most[0],font=baslik_font,fill=(0,0,0))
            width, height = img.size
            basewidth = 250
            wpercent = (basewidth/float(img.size[0]))
            hsize = int((float(img.size[1])*float(wpercent)))
            img2 = img.resize((basewidth,hsize), Image.ANTIALIAS)
            st.image(img2)
            df = df.dropna()  
            auth3 = messages_df.groupby('Yazan').agg({'MessageCount' : 'sum','emojicount':'sum','Word_Count':'sum'}).sort_values(by="emojicount",ascending=False).reset_index()
            auth3 = auth3.emojicount[round(len(auth.Yazan)/2)].astype(str)
            st.metric("",auth3, delta='emoji kullandı',delta_color='off')

        with col3:
            st.markdown(f"**Cool Çocuk : {auth.Yazan.iloc[-1]}**") 
            lst_gif3 = [gif11,gif12,gif13,gif14,gif15]
            st.image(random.choice(lst_gif3),width=300,caption="Grubun en havalı elemanıdır. Az ama öz konuşur. Genelde en sevdiği renk siyahtır.")
            yazan3 = messages_df[messages_df['Yazan'] == auth.Yazan.iloc[-1]]
            text3 = " ".join(review for review in yazan3.Mesaj)
            wordcloud3 = WordCloud(stopwords=STOPWORDS, background_color="white",width=800, height=400).generate(text3)
            yazan3_most = list(wordcloud3.words_.keys())
            img = Image.open("images/wp_not2.png")
            draw = ImageDraw.Draw(img)
            font = ImageFont.truetype("fonts/TitilliumWeb-Regular.ttf",size = 40, encoding='utf-8')
            baslik_font = ImageFont.truetype("fonts/Roboto-Regular.ttf",size = 30, encoding='utf-8')
            draw.text((20,70),auth.Yazan.iloc[-1],font=baslik_font,fill=(150,50,150))
            draw.text((20,120),yazan3_most[0],font=baslik_font,fill=(0,0,0))
            width, height = img.size
            basewidth = 250
            wpercent = (basewidth/float(img.size[0]))
            hsize = int((float(img.size[1])*float(wpercent)))
            img2 = img.resize((basewidth,hsize), Image.ANTIALIAS)
            st.image(img2)
            df = df.dropna()  
            auth4 = messages_df.groupby('Yazan').agg({'MessageCount' : 'sum','emojicount':'sum','Word_Count':'sum'}).sort_values(by="Word_Count",ascending=False).reset_index()
            auth4 = auth4.Word_Count.iloc[-1].astype(str)
            st.metric("",auth4, delta='kelime harcadı',delta_color='inverse')
    else:
        pass 
        




    link_messages= df[df['Link Sayısı']>0]
    deleted_messages=df[(df["Mesaj"] == " You deleted this message")| (df["Mesaj"] == " This message was deleted.")|
                        (df["Mesaj"] == " You deleted this message.")| (df["Mesaj"] == " Bu mesaj silindi")| (df["Mesaj"] == " Bu mesaj silindi.")]
    media_messages_df = df[(df['Mesaj'] == ' <Media omitted>')|(df['Mesaj'] == ' image omitted')|
                            (df['Mesaj'] == ' video omitted')|(df['Mesaj'] == ' sticker omitted')]
    messages_df = df.drop(media_messages_df.index)
    messages_df = messages_df.drop(deleted_messages.index)
    messages_df = messages_df.drop(link_messages.index)

    messages_df['Letter_Count'] = messages_df['Mesaj'].apply(lambda s : len(s))
    messages_df['Word_Count'] = messages_df['Mesaj'].apply(lambda s : len(s.split(' '))-1)
    messages_df["MessageCount"]=1

    messages_df["emojicount"]= df['Emoji'].str.len()

    l = messages_df.Yazan.unique()

    auth = messages_df.groupby("Yazan").sum()
    auth.reset_index(inplace=True)
    auth = auth.sort_values(by="MessageCount", ascending=False)
    link_messages= df[df['Link Sayısı']>0]
    deleted_messages=df[(df["Mesaj"] == " You deleted this message")| (df["Mesaj"] == " This message was deleted.")|
                        (df["Mesaj"] == " You deleted this message.")]
    media_messages_df = df[(df['Mesaj'] == ' <Media omitted>')|(df['Mesaj'] == ' image omitted')|
                            (df['Mesaj'] == ' video omitted')|(df['Mesaj'] == ' sticker omitted')]
    messages_df = df.drop(media_messages_df.index)
    messages_df = messages_df.drop(deleted_messages.index)
    messages_df = messages_df.drop(link_messages.index)

    messages_df['Letter_Count'] = messages_df['Mesaj'].apply(lambda s : len(s))
    messages_df['Word_Count'] = messages_df['Mesaj'].apply(lambda s : len(s.split(' '))-1)
    messages_df["MessageCount"]=1

    messages_df["emojicount"]= df['Emoji'].str.len()

    l = messages_df.Yazan.unique()

    auth = messages_df.groupby("Yazan").sum()
    auth.reset_index(inplace=True)
    auth = auth.sort_values(by="MessageCount", ascending=False)

    col1, col2, col3 = st.columns([4,1,4])

    with col1:
        st.header('Mesaj Atanlar')
        fig = px.bar(auth, y="Yazan", x="MessageCount", color='Yazan', orientation="h",
                    color_discrete_sequence=px.colors.sequential.Rainbow,
                    
                    )
        fig.update_layout(xaxis_title='Mesaj Sayısı',
                        yaxis_title='',paper_bgcolor='rgba(0,0,0,0)',
                        plot_bgcolor='rgba(0,0,0,0)')

        st.plotly_chart(fig, use_container_width=True)
        
    with col3:
        st.header('Emoji Kullanımı')
        auth = auth.sort_values(by="emojicount", ascending=False)
        fig = px.bar(auth, y="Yazan", x="emojicount", color='Yazan', orientation="h",
            color_discrete_sequence=px.colors.sequential.Turbo,
            
            )
        fig.update_layout(xaxis_title='Kullanılan Emoji Sayısı',
                        yaxis_title='',paper_bgcolor='rgba(0,0,0,0)',
                        plot_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig, use_container_width=True)

    st.markdown("""---""")
    user_list = ["Tüm Grup"]
    for x in df["Yazan"].drop_duplicates().tolist():
        user_list.append(x)
    option = st.selectbox(
     'Kişiye Özel İstatistikler',
     user_list)

    text = " ".join(review for review in messages_df.Mesaj)
    if option == "Tüm Grup":
        #mask = np.array(Image.open('images\whatsapp.jpg'))  
        wordcloud = WordCloud(stopwords=all_stopwords, background_color="white",width=800, height=350).generate(text)
        fig = plt.figure(figsize=(10,4))
        plt.imshow(wordcloud, interpolation='bilinear')
        plt.axis("off")
        st.subheader("Grupta En Çok Kullanılan Kelimeler")
        st.pyplot(fig)

        st.write("")
        st.write("")
        st.write("")
        st.caption("Etiket bulutu veya kelime bulutu, bir metin içinde yer alan kelimelerin bir bulut olarak görselleştirilmesiyle elde edilen görüntüdür. Sunum ve tanıtım görselleri için sıkıcı yazıları eğlenceli hale dönüştürmeye çalışır. Burada, grup ya da kişi özelinde en çok kullanılan kelimeleri görüyorsunuz. Kelimenin boyutu ne kadar büyükse kullanım sıklığı da o kadar fazladır. ")
        st.markdown("""---""")


    else:
        dummy_df = messages_df[messages_df['Yazan'] == option]
        text = " ".join(review for review in dummy_df.Mesaj)
        # Generate a word cloud image
        st.subheader(f"{option} İçin En Çok Kullanılan Kelimeler")
        wordcloud = WordCloud(stopwords=all_stopwords, background_color="white",width=800, height=350).generate(text)
        fig = plt.figure( figsize=(10,4))
        plt.imshow(wordcloud, interpolation='bilinear')
        plt.axis("off")
        st.pyplot(fig)
        st.markdown("""---""")

      
    col1, col2 = st.columns([1,1])
    if option != "Tüm Grup":
        messages_df = messages_df[messages_df["Yazan"] == option]
    else:
        pass

    with col1:
        total_emojis_list = list(set([a for b in messages_df.Emoji for a in b]))
        total_emojis = len(total_emojis_list)
        #st.write("Toplam Emoji",total_emojis)

        total_emojis_list = list([a for b in messages_df.Emoji for a in b])
        emoji_dict = dict(Counter(total_emojis_list))
        emoji_dict = sorted(emoji_dict.items(), key=lambda x: x[1], reverse=True)
        emoji_df = pd.DataFrame(emoji_dict, columns=['emoji', 'count'])
        import plotly.express as px
        fig = px.pie(emoji_df, values='count', names='emoji', title="Emoji Dağılımı")
        fig.update_traces(textposition='inside', textinfo='percent+label')
        fig.update_layout(title={'font': {'size': 30}, 'text': f'<b>{option} İçin Emoji Dağılımı</b>'},paper_bgcolor='rgba(0,0,0,0)',
                        plot_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig, use_container_width=True)
        st.write("")
        st.caption('Yazışırken en çok hangi emojilerin kullanıldığını gösterir. Sağ tarafta yer alan emojilere tıkladığınızda, tıkladığınız emojinin grafikten kaldırıldığını göreceksiniz. Aynı emojiye tekrar tıklayarak grafiğinize ekleyebilirsiniz.')
        st.write("")
      
    with col2:
        
        def f(i):
            l = ["Pazartesi", "Salı", "Çarşamba", "Perşembe", "Cuma", "Cumartesi", "Pazar"]
            return l[i]
        day_df=pd.DataFrame(messages_df["Mesaj"])
        day_df['day_of_date'] = messages_df['Tarih'].dt.weekday
        day_df['day_of_date'] = day_df["day_of_date"].apply(f)
        day_df["messagecount"] = 1
        day = day_df.groupby("day_of_date").sum()
        day.reset_index(inplace=True)

        fig = px.line_polar(day, r='messagecount', theta='day_of_date', line_close=True)
        fig.update_traces(fill='toself')
        fig.update_layout(
          polar=dict(
          radialaxis=dict(
            visible=True,
          )),
        showlegend=False,
        title={'font': {'size': 30}, 'text': f'<b>{option} Hangi Günler Daha Aktif?</b>'},paper_bgcolor='rgba(0,0,0,0)',
                        plot_bgcolor='rgba(0,0,0,0)'
      )
        st.write("")
        st.plotly_chart(fig, use_container_width=True)
        
        st.caption('Whatsapp konuşmanızı günler özelinde kıyaslamanıza yardımcı olur. Grafik üstünde dilediğiniz günü ve saati seçerek detaylı kıyaslama yapabilirsiniz. Grafiğe iki kere tıkladığınızda normal haline geri dönecektir.')
        st.write("")
       

else:
    st.title("Whatsapp Analyzer Nedir?")
    st.markdown("""Sevgilinizin en çok kullandığı kelimeyi merak mı ediyorsunuz? İş arkadaşlarınızın sürekli attığı ":joy:" emojisinden bıktınız ve ne kadar çok kullandıklarını göstermek mi istiyorsunuz?""", unsafe_allow_html=True)
    st.markdown("""Whatsapp Analyzer ile bunların hepsi mümkün!""")
    st.markdown("""Adından da anlaşılacağı üzere, Whatsapp Analyzer, sevgiliniz, (iş) arkadaşlarınız ya da aileniz ile oluşturduğunuz Whatsapp gruplarının detaylı analizini sizler için gerçekleştiren bir uygulamadır.
                """)
    st.markdown("""
    Uygulamayı aşağıdaki adımları takip ederek kolaylıkla çalıştırabilirsiniz:

    1. Analiz etmek istediğiniz Whatsapp konuşmasına giderek konuşmayı dışarı aktarın
    2. Aktardığınız metin dosyasını (*Grup Adı*.**txt**) yukarıdaki gri alana tıklayarak açın (sürükleyip bırakabilirsiniz)
    3. Arkanıza yaslanın ve sizler için hazırladığımız detaylı analizin tadını çıkarın! :sparkles:
    
    ---""", unsafe_allow_html=True)
    
    st.markdown("""
    En iyi deneyimi elde etmek için uygulamayı bilgisayar üzerinden denemenizi tavsiye ederiz.
    
    ---

    Whatsapp konuşmanızı nasıl dışarı aktaracağınızı öğrenmek için aşağıdaki giflere göz atabilirsiniz :point_down:

    """,unsafe_allow_html=True)
    st.title('Sıkça Sorulan Sorular')
    st.subheader('Whatsapp Konuşmamı Nasıl Dışarı Aktarabilirim?')
    st.markdown("""WhatsApp sohbetini dışa aktarma, iOS veya Android cihazınızdan kolayca yapılabilir. 
              Talimatları görmek için aşağıdaki gifleri kontrol ediniz. Dışa aktarırken, Medyayı Dahil Etme (Without Media) 
              seçeneğini belirlediğinizden emin olun. Son olarak konuşma metninizi kendinize e-posta yoluyla veya kendinize en
              uygun yöntem ile gönderebilirsiniz.""")

    st.markdown("""<b>Android için:</b> Bizim için gerekli olan dosya '.txt' uzantılı metin dosyasıdır. Birden fazla dosyanın dışa aktarılması durumunda kalanları görmezden gelebilirsiniz.""", unsafe_allow_html=True)
    st.markdown("""<b>IPhone için:</b> Konuşma metniniz .zip dosyası olarak dışa aktarılacaktır. Metin dosyasına (.txt) ulaşabilmek için sıkıştırılmış dosyayı açmanız gerekir.""", unsafe_allow_html=True)
    st.markdown("")
    row5_1, row5_space, row5_2, row5_space2, row5_3 = st.columns((1,1,1,1,1))
    with row5_1:
        st.write('')
    with row5_space:
        st.image("images/chat-export-android.gif", caption="Android 9, WhatsApp 2.20.123", use_column_width=True)
    with row5_2:
        st.write('')
    with row5_space2: 
        st.image("images/chat-export-ios.gif", caption="iOS 12, WhatsApp 2.20.31", use_column_width=True)
    with row5_3:
        st.write('')

    st.markdown("---")

    st.subheader('Whatsapp Konuşma Verilerim Herhangi Bir Şekilde Saklanıyor Mu?')
    st.markdown("""<b>Hayır!</b>""", unsafe_allow_html=True)
    st.markdown("""'Whatsapp Analyzer' <a href="https://streamlit.io/">Streamlit </a>altyapısı ile çalışan bir uygulamadır. Streamlit'in sunduğu <i>st.file_uploader</i> 
              aracını kullanarak bir dosya yüklediğinizde, veriler tarayıcı (Google Chrome, Mozilla Firefox) aracılığı ile
              Streamlit arka ucuna kopyalanır ve Python belleğindeki bir BytesIO arabelleğinde (yani disk değil RAM) kullanılır. Verileriniz
              Streamlit uygulaması yeniden çalışana kadar RAM'de kalacaktır.""", unsafe_allow_html=True)
    st.markdown("""<b>Dosyalar bellekte depolandığından, artık gerekmeyecekleri anda hemen silinirler.</b>""", unsafe_allow_html=True)
    st.markdown("""Bu, Streamlit'in aşağıdaki durumlarda bir dosyayı bellekten kaldıracağı anlamına gelir:""")
    st.markdown("""1) Kullanıcı orijinal dosyanın yerine başka bir dosya yüklediğinde """)
    st.markdown("""2) Kullanıcı yüklediği dosyayı temizlediğinde""")
    st.markdown("""3) Kullanıcı dosyayı yüklediği tarayıcı sekmesini kapattığında""")
    st.markdown("""Daha fazla bilgi için <a href="https://docs.streamlit.io/knowledge-base/using-streamlit/where-file-uploader-store-when-deleted">Streamlit sayfasını</a> ziyaret edebilirsiniz.""", unsafe_allow_html=True)

    st.markdown("---")

    st.markdown('Whatsapp Analyzer açık kaynak kodlu bir projedir. Proje kodu hakkında detaylı bilgi için <a href="https://github.com/dogudogru/whatsapp_analyzer"> Github sayfasını </a> ziyaret edebilirsiniz.  ', unsafe_allow_html=True)


    st.markdown(" ")
    st.subheader("Proje Geliştiricileri")
    st.markdown(" ")

    col1, col2, col3, col4, col5,col6,col7 = st.columns([1,1,1,1,1,1,1])

    with col1:
            st.markdown("<b><i>Doğukan Doğru</i></b>", unsafe_allow_html=True)
            st.markdown("[![Foo](data:image/png;base64,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)](https://www.linkedin.com/in/doğukandoğru/)")
            st.markdown("[![Foo](data:image/png;base64,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)](https://github.com/dogudogru)")

    with col4:
            st.markdown("<b><i>Mert Türkyılmaz</i></b>", unsafe_allow_html=True)
            st.markdown("[![Foo](data:image/png;base64,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)](https://www.linkedin.com/in/mertturkyilmaz/)")
            st.markdown("[![Foo](data:image/png;base64,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)](https://github.com/mertturkyilmaz)")
    with col7:
            st.markdown("<b><i>Sarper Yılmaz</i></b>", unsafe_allow_html=True)
            st.markdown("[![Foo](data:image/png;base64,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)](https://www.linkedin.com/in/sarperyilmaz/)")
            st.markdown("[![Foo](data:image/png;base64,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)](https://github.com/sarperyilmaz)")
    

