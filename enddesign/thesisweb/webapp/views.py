from django.shortcuts import render,HttpResponse,redirect

from webapp.models import Userlogin,Table
db = Table

#注册用户
def login(request):
    if request.method == "POST":
        # 获取用户通过POST提交过来的数据
        usm = request.POST.get('username')
        pwd = request.POST.get('password')
        if Userlogin.objects.filter(username=usm):
            User=Userlogin.objects.get(username=usm).username
            password = Userlogin.objects.get(username=usm).password
            if pwd==password:
                name=Userlogin.objects.get(username=usm).name
                with open("user_name.txt", "w", encoding="utf-8") as f:
                    f.write(User)
                with open("login_name.txt", "w", encoding="utf-8") as v:
                    v.write(name)
                return redirect('/index/')
            else:
                msg="密码错误"
        else:
            msg="用户名不存在"
    return render(request,"user.html",locals())

def register(request):
    if request.method=="POST":
        new_usr=request.POST.get("new_username")
        name=request.POST.get("name")
        telephone=request.POST.get("telephone")
        email=request.POST.get("email")
        new_paw=request.POST.get("new_password")
        if Userlogin.objects.filter(username=new_usr):
            msg = "用户名已存在"
        elif Userlogin.objects.filter(telephone=telephone):
            msg="电话号码已注册"
        elif Userlogin.objects.filter(email=email):
            msg="邮箱已注册"
        else:
            Userlogin.objects.create(username=new_usr,name= name,telephone=telephone,
                                      email=email,password=new_paw)
            return redirect('/')

    return render(request,"register.html",locals())



def index(request):
    with open("user_name.txt", "r", encoding="utf-8") as f:
        data = f.read()
    if request.method=="POST":
        queryname = request.POST.get('queryname')
        if db.objects.filter(username=data,queryname=queryname):
            list = db.objects.filter(username=data,queryname=queryname).order_by('-number').first()
            msg =list.title
        else:
            msg = "没有下载此类论文"
    return render(request,"index.html",locals())

def about(request):
    with open("user_name.txt", "r", encoding="utf-8") as f:
        data = f.read()
    username=data
    thesisnum=db.objects.filter(username=username).count()
    Name=Userlogin.objects.get(username=username).name
    Password=Userlogin.objects.get(username=username).password
    Email = Userlogin.objects.get(username=username).email
    Telephone = Userlogin.objects.get(username=username).telephone
    # return render(request, "about.html", {"datelist": thesisnum})
    return render(request,"about.html",{"datelist":thesisnum,"Name":Name,
                                       "Telephone":Telephone,"Password":Password,
                                       "Email":Email,"Username":username})

def Contact(request):
    with open("user_name.txt", "r", encoding="utf-8") as f:
        data = f.read()
    datelist =db.objects.filter(username = data)
    return render(request,"Contact.html",{"datelist":datelist})

def Del(request):
    uid=request.GET.get("uid")
    db.objects.filter(id=uid).delete()
    return redirect("/Contact/")

def edit(request):
    uid = request.GET.get("uid")  ##根据用户id进行查找更新
    user_data = db.objects.get(id=uid)
    if request.method == "GET":
        return render(request, "edit.html", {"user_data": user_data})
    title = request.POST.get("title")

    website = request.POST.get("website")
    subjects = request.POST.get("subjects")
    abkey=request.POST.get("abkey")
    db.objects.filter(id=uid).update(title=title, website=website,
                                           subjects=subjects,abkey=abkey)
    return redirect("/Contact/")  ###结果重定向
