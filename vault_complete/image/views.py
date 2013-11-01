import os
import string 
import random
import subprocess
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.http import HttpResponseForbidden
from django.http import HttpResponse
from django.http import HttpResponseRedirect

@login_required(login_url='/login/')
def account_view(request):
    if request.method == "POST":
        if 'delimage'  in request.POST:
            img = os.path.basename(request.POST['delimage'])[:-4]
            image = settings.MEDIA_ROOT + str(request.user.id) + "/decrypt/" + img
            if os.path.exists(image):
                os.remove(image)
    if not os.path.isdir(settings.MEDIA_ROOT + str(request.user.id)):
        return render(request, 'accounts/upload.html')
    files = [ x for x in os.listdir(settings.MEDIA_ROOT + str(request.user.id)) if not os.path.isdir(settings.MEDIA_ROOT + str(request.user.id) + "/" + x)  ]
    if not files:
        return render(request, 'accounts/upload.html')
    return render(request, 'accounts/login_page.html', {'files': files, 'media': settings.MEDIA_ROOT })

@login_required(login_url='/login/')
def del_img(request):
    img = os.path.basename(request.POST['delimage'])[:-4]
    image = settings.MEDIA_ROOT + str(request.user.id) + "/decrypt/" + img
    if os.path.exists(image):
        os.remove(image)
        return HttpResponseRedirect("/accounts/")
    return HttpResponse("Image Not Found")

@login_required(login_url='/login/')
def tag_img(request):
    img = os.path.basename(request.POST['imgsrc'])[:-1]
    image = settings.MEDIA_ROOT + str(request.user.id) + "/" + img
    tag = request.POST['tag']
    if os.path.exists(image):
        os.rename(image, settings.MEDIA_ROOT + str(request.user.id) + "/" + tag + "__" + img)
        return HttpResponse("Tagged.. yay..")
    return HttpResponse("Image not found.. Hmmm.. ")

@login_required(login_url='/login/')
def delete_img(request):
    img = os.path.basename(request.POST['imgsrc'])[:-1]
    image = settings.MEDIA_ROOT + str(request.user.id) + "/" + img
    print image
    if os.path.exists(image):
        os.remove(image)
        return HttpResponse("Image Deleted")
    return HttpResponseRedirect("Image not found")

@login_required(login_url='/login/')
def decrypt(request):
    img_present = None
    if request.method == "POST":
        pass_phrase = request.POST['epass']
        img = os.path.basename(request.POST['imgsrc']).rstrip('"')
        if pass_phrase and img:
            img_file = settings.MEDIA_ROOT + str(request.user.id) + "/" + img
            if os.path.exists(img_file):
                tmp_file = "/dev/shm/" + str(request.user.id) + "_" + "".join(random.choice(string.digits) for i in xrange(6))
                p = subprocess.Popen(["/usr/bin/steghide", "info", img_file, "-p", pass_phrase ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                (out, err) = p.communicate()
                print out
                if '__img' in out:
                    img_present = True
                    if not os.path.isdir(settings.MEDIA_ROOT + str(request.user.id) + "/decrypt/"):
                        os.makedirs(settings.MEDIA_ROOT + str(request.user.id) + "/decrypt/")
                    file_id = "".join(random.choice(string.digits) for i in xrange(6))
                    tmp_file = settings.MEDIA_ROOT + str(request.user.id) + "/decrypt/" "dimg_" + file_id
                p = subprocess.Popen(["/usr/bin/steghide", "extract", "-sf", img_file, "-p", pass_phrase, "-xf", tmp_file ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                (out, err) = p.communicate()
            if os.path.exists(tmp_file):
                if img_present:
                    return render(request, 'accounts/decrypt.html', {'data': "/media/" + str(request.user.id) + "/decrypt/" + "dimg_" + file_id })
                f = open(tmp_file)
                lines = f.read()
                f.close()
                os.remove(tmp_file)
                return render(request, 'accounts/decrypt.html', {'data': lines })
            return render(request, 'accounts/decrypt.html', {'data': 'Either passphrase is wrong or Image is not encrypted' })
    return render(request, 'accounts/decrypt.html', {'data': 'Only POST method is allowed here' })
        
    
@login_required(login_url='/login/')
def encrypt(request):
    if request.method == "POST":
        if request.FILES:
            pass_phrase = request.POST['epass']
            img = os.path.basename(request.POST['imgsrc']).rstrip('"')
            img_file = settings.MEDIA_ROOT + str(request.user.id) + "/" + img
            path = "/dev/shm/" + str(request.user.id) + "__img" + "".join(random.choice(string.digits) for i in xrange(6))
            save_enc_file(request.FILES['image_file'], path)
            p = subprocess.Popen(["/usr/bin/steghide", "embed", "-cf", img_file, "-ef", path, "-p", pass_phrase, "-e", "rijndael-192", "-z", "3" ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            (out, err) = p.communicate()
            os.remove(path)
            if 'short' in str(err):
                return HttpResponse("The cover file is too short..")
            return render(request, 'accounts/encrypt.html')
            
        pass_phrase = request.POST['epass']
        enc_text = request.POST['etext']
        img = os.path.basename(request.POST['imgsrc']).rstrip('"')
        if pass_phrase and enc_text and img:
            tmp_file = "/dev/shm/" + str(request.user.id) + "_" + "".join(random.choice(string.digits) for i in xrange(6))
            fd = open(tmp_file, 'w')
            fd.write(enc_text)
            fd.close()
            img_file = settings.MEDIA_ROOT + str(request.user.id) + "/" + img
            if os.path.exists(img_file):
                p = subprocess.Popen(["/usr/bin/steghide", "embed", "-cf", img_file, "-ef", tmp_file, "-p", pass_phrase, "-e", "rijndael-192", "-z", "3" ], stdout=subprocess.PIPE)
                out, err = p.communicate()
                os.remove(tmp_file)
                return render(request, 'accounts/encrypt.html')
    return render(request, 'accounts/decrypt.html', {'data': 'Only POST method is allowed here' })

@login_required(login_url='/login/')
def upload(request):
    if request.method == 'POST':
        save_file(request.FILES['image_file'], str(request.user.id))
        return HttpResponse("File succesfully Uploaded")
    return HttpResponseForbidden('allowed only via POST')

 
def save_file(file, path=''):
    ''' Little helper to save a file
    '''
    filename = file._get_name()
    if not os.path.isdir(settings.MEDIA_ROOT + path):
        os.makedirs(settings.MEDIA_ROOT + path)
    fd = open(settings.MEDIA_ROOT + str(path) + "/" + str(filename), 'wb')
    for chunk in file.chunks():
        fd.write(chunk)
    fd.close()
    return 0
    
def save_enc_file(file, path=''):
    ''' Little helper to save a file
    '''
    filename = file._get_name()
    fd = open(str(path), 'wb')
    for chunk in file.chunks():
        fd.write(chunk)
    fd.close()
    return 0
    
