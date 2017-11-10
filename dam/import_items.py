from lib import *

"""
try:
    import_girl('jsons/chicas.json.pt')
    #import_girl('girl.json.pt')
except ImporterException as err:
    print err.value
"""
"""
try:
    import_category('category_images.json')
except ImporterException as err:
    print err.value
"""
"""
try:
    import_serie('jsons/serie.json.pt')
    #import_serie('serie.json.pt')
except ImporterException as err:
    print err.value
"""
"""
try:
    import_movie('jsons/movie.json.pt')
    #import_movie('movie.json.pt')
except ImporterException as err:
    print err.value
"""
"""
try:
    #import_episode('jsons/episode.json.pt')
    import_episode('jsons/episode.json', True)
except ImporterException as err:
    print err.value
"""


girls_list = Girl.objects.all()
for girl in girls_list:
    try:
        #enqueue_girl(girl, "Virginia",'es')
        enqueue_girl(girl, "Virginia")
    except EnqueuerException as err:
        print err.value


movies_list = Movie.objects.all()
for movie in movies_list:
    try:
        #enqueue_movie(movie, "Virginia", 'es')
        enqueue_movie(movie, "Virginia")
    except EnqueuerException as err:
        print err.value


serie_list = Serie.objects.all()
for serie in serie_list:
    try:
        #enqueue_serie(serie, "Virginia", 'es')
        enqueue_serie(serie, "Virginia")
    except EnqueuerException as err:
        print err.value


episode_list = Episode.objects.all()
for episode in episode_list:
    try:
        #enqueue_episode(episode, "Virginia", 'es')
        enqueue_episode(episode, "Virginia")
    except EnqueuerException as err:
        print err.value


"""
# Publicar Serie con todos los episodios
asset_id = 'S00115'
try:
    asset = Asset.objects.get(asset_id=asset_id)
except ObjectDoesNotExist:
    print "Asset ID %s no existe" % asset_id

try:
    serie = Serie.objects.get(asset=asset)
except ObjectDoesNotExist:
    print "Serie con asset ID %s no existe" % asset_id

try:
    enqueue_serie(serie, "Virginia", "es")
except EnqueuerException as err:
    print err.value

episodes = Episode.objects.filter(serie=serie)
for episode in episodes:
    try:
        enqueue_episode(episode, "Virginia", 'es')
    except EnqueuerException as err:
        print err.value
"""

"""
category_list = Category.objects.all()
for category in category_list:
    try:
        enqueue_category(category, "Virginia", 'es')
        #enqueue_category(category)
    except EnqueuerException as err:
        print err.value
"""


"""
slider_list = Slider.objects.all()
for slider in slider_list:
    try:
        enqueue_slider(slider, ENDPOINT, 'es')
        #enqueue_slider(slider)
    except EnqueuerException as err:
        print err.value
"""


"""
block_list = Block.objects.all()
for block in block_list:
    try:
        enqueue_block(block, "Virginia")
    except EnqueuerException as err:
        print err.value
"""

"""
for item in PublishQueue.objects.filter(status='E'):
    item.status  = 'Q'
    item.message = ''
    item.save()
"""
"""
for item in PublishQueue.objects.all():
    item.status  = 'Q'
    item.message = ''
    item.save()
"""

#q = Movie.objects.filter(year=0).annotate(Count('runtime'))
#print q.runtime__count
#print Movie.objects.filter(year=0).distinct('original_title')
#print Movie.objects.filter(year=0).values_list('runtime', flat=True).distinct().count()
#movies = Movie.objects.filter(year=0)


#asset = Asset.obje
#girl = Girl.objects.get(asset=)

"""
images = Image.objects.all()
for image in images:
    if image.portrait:
        image.portrait  = "%s.jpg" % image.name
    if image.landscape:
        image.landscape = "%s.jpg" % image.name
    image.save()
"""


"""
categories = Category.objects.all()
for cat in categories:
    image = Image.objects.get(name=cat.category_id)
    enqueue_image(image)
"""


"""
girls = Girl.objects.all()
for girl in girls:
    image = Image.objects.get(name=girl.asset.asset_id)
    enqueue_image(image)
"""

"""
categories = Category.objects.all()
for cat in categories:
    image = Image.objects.get(name=cat.category_id)
    image.landscape.name = image.landscape.name.replace("portrait", "landscape")
    image.save()
"""



"""
dir = "cawas/static/images/landscape"
for file in os.listdir(dir):
    if file.startswith("G0"):
        asset_id = file.split(".")[0]
        try:
            image = Image.objects.get(name=asset_id)
            image.landscape.name = file
            image.save()
        except ObjectDoesNotExist:
            print asset_id
"""


"""
landscape_path = Setting.objects.get(code="image_repository_path_landscape").value
portrait_path  = Setting.objects.get(code="image_repository_path_portrait").value
assets = Asset.objects.all()
for asset in assets:
    try:
        image = Image.objects.get(name=asset.asset_id)
        if image.portrait.name != '':
            image.portrait.name = portrait_path + asset.asset_id + ".jpg"
            image.save()
        if image.landscape.name != '':
            image.landscape.name = landscape_path + asset.asset_id + ".jpg"
            image.save()
    except ObjectDoesNotExist:
        print asset.asset_id
"""


"""
### Asignar categorias de los episodios a las serie
series = Serie.objects.all()
for serie in series:
    categories = []
    episodes = Episode.objects.filter(serie=serie)
    for episode in episodes:
        for cat in episode.category.all():
            if cat not in categories:
                categories.append(cat)
    print "####### %s #######" % serie.original_title
    for category in categories:
        print category.original_name
#        serie.category.add(category)
"""
"""
assets_ids = [""]

for aid in assets_ids:
    try:
        asset = Asset.objects.get(asset_id=aid)
        enqueue_asset(asset, "Virginia", "es")
    except:
        print "ID %s no existe" % aid
"""
