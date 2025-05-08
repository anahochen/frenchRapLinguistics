#%% md
# Script Python pour récupérer les paroles d'une chanson
# ======================================================
# Un grand merci à Bigishdata 
# *(https://bigishdata.com/2016/09/27/getting-song-lyrics-from-geniuss-api-scraping/comment-page-1/#comment-929)*
#%%
import requests

# Remarque : à partir de mai 2017, l'hôte est sous HTTPS. Donc base_url a changé. 
base_url = "https://api.genius.com"
headers = {'Authorization': 'Bearer oX0OPhdhU3uI4IVri0j5RPs2Nzc6w4sf5YzSXXs3nC3E-BhKQ-SLI331xUBCyD3B'}




# On fait une recherche pour avoir la bonne chanson du bon artiste
# (il se peut que ce ne soit pas la seule chanson avec ce titre !)
search_url = base_url + "/search"
song_title = "Nés sous la même étoile"
artist_name = "IAM"
# le paramètre de recherche à passer après /search?
data = {'q': song_title}
# et le GET qui va retourner un objet en JSON
response = requests.get(search_url, data=data, headers=headers).json()
print(response["meta"])

# Genius retourne un résultat (hit) par artiste sur une liste
for hit in response["response"]["hits"]:
  if hit["result"]["primary_artist"]["name"] == artist_name:
    song_info = hit
    break
if song_info !=None:
  print("song_info retrieved")
  pass
#%% md
# La requête a abouti (_code 200_). On peut regarder sa valeur. Nous avons les données du morceau.
# Gardons l'identifiant de la chanson pour plus tard ! 
#%%
song_path = song_info["result"]["api_path"]
song_id = song_info["result"]["id"]
song_url = song_info["result"]["url"]
#%% md
# ## C'est l'heure de récupérer les paroles
#%%
from bs4 import BeautifulSoup
# retourne les informations en JSON de la page avec les paroles
page = requests.get(song_url)
# objet BeautifulSoup pour parsing
html = BeautifulSoup(page.text, "html.parser")
# on enlève tous les mots script !
[h.extract() for h in html('script')]
# on trouve la balise div (dont la classe est lyrics)
lyrics = html.find("div", class_="lyrics").get_text()
# Pour les besoins du script, on va enlever les mots entre crochets
import re
lyrics = re.sub(r'\[.*\]','\n',lyrics)
# Suppression des retours à la ligne
# lyrics_sans = re.sub(r'\n'," ",lyrics)
print(lyrics)
# print(lyrics_sans)
#%% md
# Récupération de paroles de Genius.com
# =====================================
# On va transformer notre code en fonction. Notre (courte) étude s'étendre sur quelques chansons.
#%% md
# ### Paramètres
# **Entrées :** 
# .. titre : nom de la chanson
# .. artiste : nom de l'artiste
# 
# **Sorties :**
# .. paroles (str) : paroles de la chanson
#%%
def donne_moi_les_paroles(titre, artiste):
    import requests
    base_url = "https://api.genius.com"
    headers = {'Authorization': 'Bearer oX0OPhdhU3uI4IVri0j5RPs2Nzc6w4sf5YzSXXs3nC3E-BhKQ-SLI331xUBCyD3B'}
    search_url = base_url + "/search"
    song_title = titre
    artist_name = artiste
    data = {'q': song_title}
    response = requests.get(search_url, data=data, headers=headers).json()

    for hit in response["response"]["hits"]:
      if hit["result"]["primary_artist"]["name"] == artist_name:
        song_info = hit
        break
    if song_info !=None:
      #print("ID de chanson retrouvée")
      pass

    song_path = song_info["result"]["api_path"]
    song_id = song_info["result"]["id"]
    song_url = song_info["result"]["url"]

    from bs4 import BeautifulSoup
    page = requests.get(song_url)
    html = BeautifulSoup(page.text, "html.parser")
    [h.extract() for h in html('script')]
    lyrics = html.find("div", class_="lyrics").get_text()

   # Pour les besoins du script, on va enlever les mots entre crochets
    import re
    lyrics = re.sub(r'\[.*\]',' ',lyrics)
    # Suppression des retours à la ligne
    # lyrics_sans = re.sub(r'\n'," ",lyrics)
    print(lyrics)
    # print(lyrics_sans)

    return lyrics
#%% md
# C'est l'heure d'extraire les paroles !
#%%
donne_moi_les_paroles("Nés sous la même étoile", "IAM")
#%% md
# La première partie de ce notebook consistait à faire du _scraping_ sur des paroles. La deuxième partie consistera à traiter les paroles ainsi extraites, pour les convertir en tableau de données.
#%% md
# # C'est l'heure du Bag of words
#%% md
# La tokenisation de paroles consiste à repérer les mots (donc reconnaître les caractères d'espace et de ponctuation), ensuite regrouper les mots à racine similaire (les variantes de nombre ou de genre, les conjugaisons...) pour éviter les redondances, rassembler aussi les synonymes, puis comptabiliser la fréquence d'apparition de ces mots (pondération). 
# 
# Dans ce tableau de données, en plus du poids du "token" (mot), il faudra qu'on pense aussi à qualifier chaque mot : catégorie lexicale (POS avec NLTK) ? niveau de registre ? origine éthymologique ? La clé est de réduire la dimensionalité de cette future table de données, et, étant donné la richesse de la langue française, la tâche peut être dure. 
# 
# Notre but étant d'évaluer la complexité des paroles d'un artiste donné, nous nous intéreserons par la suite à la définition d'une fonction pour qualifier le niveau de chaque chanson, en prenant les paramètres que nous aurons calculé pour chaque token. 
#%% md
# ** Nota : **
# Dans le du rap (et de la musique en général) c'est que le corps du texte a une structure différente à celle de la prose. Les genres lyriques cherchent la musicalité, donnée par la métrique de la ligne, la rhyme ainsi que l'utilisation de ressources de styles (telles que l'allitération). Ce sont des paramètes qu'il faudra calculer par document (paroles) afin de qualifier la chanson. 
#%% md
# ** Commençons par le commencement**
#%% md
# Je ne vais pas balancer les paroles directement comme un bourrin, commençons par tester avec les premier 280 caractères des "Nés sous la même étoile" d'IAM. 
#%% raw
# donne_moi_les_paroles("Nés sous la même étoile", "IAM")
#%% md
# J'aurais pu aussi essayer avec "Ma Benz" de Suprême NTM. 
#%% raw
# donne_moi_les_paroles("Ma Benz", "Suprême NTM")
#%% md
# **Première conclusion** : Il vaudra mieux commencer par des artistes plus... lyriques. 
#%% md
# ### A la découverte de NLTK
#%% md
# Assez de bidouille, il est temps de s'attaquer au traitement de langage naturel en soi, avec le package NLTK dont j'ai tant entendu parler. Ainsi, j'ai fait la première chose que nous les auto-didactes faisons : chercher un tutoriel sur Google. Je tombe sur ce lien : https://code.tutsplus.com/fr/tutorials/introducing-the-natural-language-toolkit-nltk--cms-28620. NLTK est déjà installé sur mon environnement Anaconda, et j'ai actuellement la version 3.2.4. Pour que NLTK fonctionne correctement, il faut télécharger un corpus de texte, qui contient des mots. 
#%% md
# **Nota** : Le monde du NLTK est très développé en anglais, moins en français. Heureusement, j'ai croisé le travail de Jean-Philippe Fauconnier (http://fauconnier.github.io/), chercheur spécialisé dans le domaine du NLP et Machine Learning, actuellement chez Apple. Sur son GitHub, il a mis les liens vers Wacky (http://wacky.sslmit.unibo.it/doku.php?id=corpora), une sort de wiki où des corpus de différentes langues sont disponibles pour utilisation. Avoir un corpus permet à la machine d'avoir une référence lingüistique. 
#%% md
# Mon premier souci est de décomposer les phrases en mots. Normalement, on utiliserait les "stop words", mais en français il y a beaucoup plus de contractions qu'en anglais. D'après des échanges sur Stack Overflow, la solution Tree Tagger, avec Tree Tagger Wrapper, fonctionne bien avec le français. Il faut tout d'abord télécharger Tree Wrapper (http://www.cis.uni-muenchen.de/~schmid/tools/TreeTagger/), l'installer en local et paramétrer les langues souhaitées. J'ai mis tous les fichiers dont j'avais besoin dans le même répertoire que ce Notebook. 
# 
# Dans la fenêtre Terminal, j'ai navigué dans le répertoire du projet, et lancé le script pour installer Tree Tagger. Comme je suis sur OSX, Finder avait décompressé automatiquement le .tar, et donc l'installation ne s'est pas bien passée (merci aux indices ici http://www.cis.uni-muenchen.de/~schmid/tools/TreeTagger/installation-hints.txt). J'ai transféré le .tar et j'ai eu le message de succès suivant :
#%% raw
# # TreeTagger version for Mac OS-X installed.
# French parameter file installed.
# usage: mv [-f | -i | -n] [-v] source target
#        mv [-f | -i | -n] [-v] source ... directory
# Path variables modified in tagging scripts.
# 
# You might want to add /Users/anahochen/AnacondaProjects/cmd and /Users/anahochen/AnacondaProjects/bin to the PATH variable so that you do not need to specify the full path to run the tagging scripts.
#%% md
# Il faut penser à exécuter la commande de test depuis le terminal depuis le répertoire où se trouve le projet (pwd + cd). Le fichier de paramétrage en français doit se situer dans le répertoire lib et se nomme french.par
#%% raw
# echo -e "Ceci\nest\nun\ntrès\ncourt\ntexte\nà\nétiqueter\n."  |bin/tree-tagger -token -lemma -quiet lib/french.par
#%% raw
# Ceci	    PRO:DEM	    ceci
# est	        VER:pres    être
# un	        DET:ART	    un
# très	    ADV	        très
# court	    ADJ	        court
# texte	    NOM	        texte
# à	        PRP	        à
# étiqueter   VER:infi	étiqueter
# .	SENT	.
# 
#%% md
# Le blog de Fabien Poulard contient très bonnes ressources et explications (http://fabienpoulard.info/post/2011/01/09/Python-et-Tree-Tagger).
#%% md
# Pour installer un package, je lance la commande depuis la fenêtre Terminal (pip install TreeTaggerWrapper)
#%% md
# Première étape, créer un objet TreeTagger (français !)  et lui donner une chaîne à _tagger_ : 
#%%
import pprint
import treetaggerwrapper
# Construction et configuration du wrapper
tagger = treetaggerwrapper.TreeTagger(TAGLANG='fr', TAGDIR="TreeTagger/", TAGINENC='utf-8',TAGOUTENC='utf-8')
# Utilisation
tags = tagger.TagText(donne_moi_les_paroles("Ma Benz", "Suprême NTM"))
print(tags)
tags = tagger.tag_text("This is a very short text to tag.")
pprint.pprint(tags)
#%% md
# 
#%%
