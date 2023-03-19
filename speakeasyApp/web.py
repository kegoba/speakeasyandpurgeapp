
def Webpost_video(request):
    if request.method == 'POST':
        video = VideoForm(request.POST, request.FILES)
        if video.is_valid():
            video.save()
            return redirect('/showvideo')
    return render(request, 'post_video.html')

#Post_video   Post_article


def Webdisplay_video(request):
    video = Video.objects.all()
    context = {
        'video': video,
    }
    return render(request, 'show_video.html', {"video": video})


def Webdelete_video(request, id):
    video_method = Video.objects.get(id=id)
    data = video_method.video.delete()
    if data is None:
        return redirect('/showvideo')
    return render(request, 'show_video.html')


def Webpost_article(request):
    if request.method == 'POST':
        title = request.POST['title']
        content = request.POST['content']
        data = Article(title=title, content=content)
        data.save()
        return redirect('/showarticle')
    return render(request, 'post_article.html')


def Webdisplay_article(request):
    posts = Article.objects.all()
    context = {
        'articles': posts,
    }
    return render(request, 'show_article.html', context)


def WebDelete_article(request, id):
    article = Article.objects.filter(id=id)
    article.delete()
    return render(request, 'show_article.html')


def Webedith_article(request, id):
    qry = Article.objects.get(id=id)
    print(qry.content, " and", qry.title)
    return render(request, "edith_article.html", {"title": qry.title, "content": qry.content})


def Webupdate_articleweb(request, id):
    qry = Article.objects.get(id=id)
    if request.method == "POST":
        title = request.POST['title']
        content = request.POST['content']
        qry.title = title
        qry.content = content
        qry.save()
        posts = Article.objects.all()
        context = {
            'articles': posts,
        }
    return render(request, 'show_article.html', context)
