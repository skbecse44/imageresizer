
from django.http import HttpResponse
from django.shortcuts import render,redirect
from django.views.decorators.csrf import csrf_exempt
from django.core.files.storage import FileSystemStorage,Storage
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.core.files import File

import contextlib
import requests
from io import BytesIO
import cv2
import os
import numpy as np
from PIL import Image,ImageGrab
import urllib
import re
from django.utils.crypto import get_random_string

ROOT_PROJECT='/Projects/imageresizer'

def get_unique_file_name(filename):

    return FileSystemStorage().get_available_name(filename)
def build_fs_url(filename):

    return FileSystemStorage().url(filename)

def index(req):
   


    return render(req,template_name='index.html')


@csrf_exempt
def image_resizer_upload(req):

    if req.method=="GET":

        url=req.get_full_path()
        parsed=urllib.parse.urlparse(url)
        url_parm=urllib.parse.parse_qs(parsed.query)

        if len(url_parm)==1:

            file_url=url_parm['url'][0]


            if validate_url(str(file_url)):
                try :

                    data_resp=requests.get(file_url,stream=True)
                except:
                    
                    return render(req,template_name='index.html',context={
                                 'image_resizer':True,
                                'form_url':'image-resizer',
                                  'error_message':'Could not read image data...'
                                  })
                  

                if not data_resp.status_code==200:
                    return render(req,template_name='index.html',context={
                                 'image_resizer':True,
                                'form_url':'image-resizer',
                                  'error_message':'Image may not be found...'
                                  }) 
                    
                content_type=data_resp.headers['content-type']
                ct_items=content_type.split('/')
                if content_type:
                    if ct_items[0] in ['image','application']:
                        if ct_items[1] in ['png','jpg','jpeg','tiff']:
                             data_bytes=BytesIO(data_resp.content)
                             file_name='data/image-resizer-online-com.'+ct_items[1]
                             path=save_from_url(file_url,file_name)
                             fileurl=build_url(path)

                             return redirect('image-resizer/action?url='+fileurl)

                            
                                   

                                                        

                        else:
                            return render(req,template_name='index.html',context={
                                 'image_resizer':True,
                                'form_url':'image-resizer',
                                  'error_message':'Unsupported image format...'
                                  })   

                        
                    else:
                        return render(req,template_name='index.html',context={
                                 'image_resizer':True,
                                'form_url':'image-resizer',
                                  'error_message':'Unsupported image format...'
                                  })  
            else:
                return render(req,template_name='index.html',context={
                                 'image_resizer':True,
                                'form_url':'image-resizer',
                                  'error_message':'Unsupported url or Malformed Url...'
                                  }) 






        
        else:
           if req.META['QUERY_STRING']:
               return redirect('/image-resizer')
           else:
             return render(req,template_name='index.html',context={
            'image_resizer':True,
            'form_url':'image-resizer'
              })    
                   

           

       


    else:
        data_file=req.FILES.get("choose-file")
        data_uri=req.POST.get("data-uri")
       


        if data_file or data_uri:
            if data_file:
                file_type=data_file.content_type
                ft_a=file_type.split('/')

                if ft_a[0]=='image' or ft_a[1]=='application':

                    if ft_a[1] in ['png','jpeg','jpg','tiff']:

                        fs = FileSystemStorage()
                        file_name='data/image-resizer-online-com.'+ft_a[1]
                        file = fs.save(file_name, data_file)
                        fileurl = build_url(fs.url(file))


                        return redirect('image-resizer/action?url='+fileurl)
                    else:
                        return render(req,template_name='index.html',context={
                                 'image_resizer':True,
                                'form_url':'image-resizer',
                                  'error_message':'Unsupported image format...'
                                  }) 
                else:
                    return render(req,template_name='index.html',context={
                                 'image_resizer':True,
                                'form_url':'image-resizer',
                                  'error_message':'Unsupported image format...'
                                  })                       
            elif data_uri:

                if validate_url(data_uri):

                    try :
                        data_resp=requests.get(data_uri,stream=True)
                    except:
                        return render(req,template_name='index.html',context={
                          'image_resizer':True,
                           'form_url':'image-resizer',
                            'error_message':'Could not read data from url...'
            
                            })  

                    if not data_resp.status_code==200:

                        return render(req,template_name='index.html',context={
                          'image_resizer':True,
                           'form_url':'image-resizer',
                            'error_message':'Image not found...'
            
                            })  
                     
                    content_type=data_resp.headers['content-type']
                    ct_items=content_type.split('/')
                    if content_type:
                        if ct_items[0] in ['image','application']:
                            if ct_items[1] in ['png','jpg','jpeg','tiff']:


                                
                                file_name='data/image-resizer-online-com.'+ct_items[1]
                                path=save_from_url(data_uri,file_name)
                                fileurl= build_url(
                                           path
                                       )
                  
                                return redirect('image-resizer/action?url='+fileurl)
                            else:
                                return render(req,template_name='index.html',context={
                                 'image_resizer':True,
                                'form_url':'image-resizer',
                                  'error_message':'Unsupported image format...'
                                  })  

                        else:

                            return render(req,template_name='index.html',context={
                                 'image_resizer':True,
                                'form_url':'image-resizer',
                                  'error_message':'Unsupported image format...'
                                  }) 


                else:

                    return render(req,template_name='index.html',context={
                    'image_resizer':True,
                    'form_url':'image-resizer',
                    'error_message':'Unsupported url or Malformed Url...'
                     })   


        else:
             return render(req,template_name='index.html',context={
            'image_resizer':True,
            'form_url':'image-resizer',
            'error_message':'Please upload files to further process...'
            
              })   
                    









                

def build_url(file_url):
    host="http://localhost:8000"
    url=host+file_url

    return url

                        
                        

            

                           
                  
        

                





def create_data_dir():
    if not os.path('media/data/').exists():
        os.mkdirs('media/data/')

def create_files_dir():
    if not os.path('media/files/').exists():
        os.mkdirs('media/files/')        


@csrf_exempt
def image_resizer_download(req):

    if req.method=="POST":

        image_uri=req.POST.get('file-uri')
        width=req.POST.get('width')
        height=req.POST.get('height')
        resize_perc=req.POST.get('resize-perc')
        method=req.POST.get('method')
        if validate_url(image_uri):

            try :
                image_res=requests.get(image_uri,stream=True)
            except:
                return NotImplementedError('Invalid URL not implemeneted')    
            ct=image_res.headers["content-type"]
            ct_array=ct.split('/')

            if ct_array[0]=='image' or ct_array[0]=='applicaton':

                if ct_array[1] in ['png','jpg','jpeg','tiff','webp','bmp']:


                    if RepresentsInt(method) and int(method)>=1 and int(method)<=2:



                        if int(method)==1:


                            if RepresentsInt(width) and RepresentsInt(height):

                                    if int(width)>0 and int(height)>0:



                                        
                                        data= BytesIO(
                                        image_res.content
                                        )
                                        img=Image.open(data)
                                        o_width,o_height=img.size

                                        if int(width)<=o_width:
                                            if int(height)<=o_height:
                                                img_req =urllib.request.urlopen(image_uri)

                                                arr = np.asarray(bytearray(img_req.read()), dtype=np.uint8)
                                                img = cv2.imdecode(arr, -1) # 'Load it as it is'

                                                ri=cv2.resize(img, (int(width), int(height)), 
                                                interpolation = cv2.INTER_NEAREST)
                                                name=get_unique_file_name(
                                                    'download/resized_download.'+(ct_array[1].lower())
                                                )

                                                cv2.imwrite('media/'+name,ri)
                                                file_url=build_url(build_fs_url(name))
                                                data= BytesIO(
                                                urllib.request.urlopen(
                                                    file_url
                                                ).read()
                                                )

                                                im=Image.open(data)
                                                width, height = im.size
                                                mode=im.mode
                                                original_size=get_printable_size(float(image_res.headers['content-length']))
                                                f_type=ct_array[0]
                                                f_format=ct_array[1]
                                                file_info=FileInfo(
                                                original_size=original_size,
                                                width=width,
                                                height=height,
                                                mode=mode,
                                                f_type=f_type,
                                                f_format=f_format
                                                )


                                                return render(req,'index.html',context={
                                                'image_resizer_download':True,'file_info':file_info, 'file_url':file_url, })
                                                            
                                                


                                            else:

                                                data= BytesIO(
                                                urllib.request.urlopen(
                                                    image_uri
                                                ).read()
                                                )

                                                im=Image.open(data)
                                                width, height = im.size
                                                mode=im.mode
                                                original_size=get_printable_size(float(image_res.headers['content-length']))
                                                f_type=ct_array[0]
                                                f_format=ct_array[1]
                                                file_info=FileInfo(
                                                original_size=original_size,
                                                width=width,
                                                height=height,
                                                mode=mode,
                                                f_type=f_type,
                                                f_format=f_format
                                                )


                                                return render(req,'index.html',context={
                                                    'error_message':'Your height exceeds actual image bounds...',
                                                'image_resizer_upload':True,'file_info':file_info, 'file_url':image_uri, })
                                                        


                                        else:
                                            data= BytesIO(
                                            urllib.request.urlopen(
                                                image_uri
                                            ).read()
                                            )

                                            im=Image.open(data)
                                            width, height = im.size
                                            mode=im.mode
                                            original_size=get_printable_size(float(image_res.headers['content-length']))
                                            f_type=ct_array[0]
                                            f_format=ct_array[1]
                                            file_info=FileInfo(
                                            original_size=original_size,
                                            width=width,
                                            height=height,
                                            mode=mode,
                                            f_type=f_type,
                                            f_format=f_format
                                            )


                                            return render(req,'index.html',context={
                                                'error_message':'Your width exceeds actual image bounds...',
                                            'image_resizer_upload':True,'file_info':file_info, 'file_url':image_uri, })
                                                        
                                    else:
                                        raise NotImplementedError('nie')   
                            else:

                                raise NotImplementedError('nie')

                        else:


                            if RepresentsInt(resize_perc):

                                if int(resize_perc)>0 and int(resize_perc)<=100:


                                    r_p=int(resize_perc)
                                    data= BytesIO(
                                                image_res.content
                                                )
                                    img=Image.open(data)
                                    
                                    o_width,o_height=img.size

                                    r_width=o_width*(r_p/100)
                                    r_height=o_height*(r_p/100)
                                
                                if r_width<=o_width :
                                    if r_height<=o_height:


                                        img_req =urllib.request.urlopen(image_uri)

                                        arr = np.asarray(bytearray(img_req.read()), dtype=np.uint8)
                                        img = cv2.imdecode(arr, -1) # 'Load it as it is'

                                        ri=cv2.resize(img, (int(r_width), int(r_height)), 
                                        interpolation = cv2.INTER_NEAREST)
                                        name=get_unique_file_name(
                                            'download/resized_download.'+(ct_array[1].lower())
                                        )

                                        cv2.imwrite('media/'+name,ri)
                                        file_url=build_url(build_fs_url(name))
                                        data= BytesIO(
                                        urllib.request.urlopen(
                                            file_url
                                        ).read()
                                        )

                                        im=Image.open(data)
                                        width, height = im.size
                                        mode=im.mode
                                        original_size=get_printable_size(float(image_res.headers['content-length']))
                                        f_type=ct_array[0]
                                        f_format=ct_array[1]
                                        file_info=FileInfo(
                                        original_size=original_size,
                                        width=width,
                                        height=height,
                                        mode=mode,
                                        f_type=f_type,
                                        f_format=f_format
                                        )


                                        return render(req,'index.html',context={
                                        'image_resizer_download':True,'file_info':file_info, 'file_url':file_url, })
                                                    
                                    else:
                                    
                                        data= BytesIO(
                                        urllib.request.urlopen(
                                            image_uri
                                        ).read()
                                        )

                                        im=Image.open(data)
                                        width, height = im.size
                                        mode=im.mode
                                        original_size=get_printable_size(float(image_res.headers['content-length']))
                                        f_type=ct_array[0]
                                        f_format=ct_array[1]
                                        file_info=FileInfo(
                                        original_size=original_size,
                                        width=width,
                                        height=height,
                                        mode=mode,
                                        f_type=f_type,
                                        f_format=f_format
                                        )


                                        return render(req,'index.html',context={
                                            'error_message':'Your height exceeds actual image bounds...',
                                        'image_resizer_upload':True,'file_info':file_info, 'file_url':image_uri, })
                                             

                                else:

                                    data= BytesIO(
                                    urllib.request.urlopen(
                                        image_uri
                                    ).read()
                                    )

                                    im=Image.open(data)
                                    width, height = im.size
                                    mode=im.mode
                                    original_size=get_printable_size(float(image_res.headers['content-length']))
                                    f_type=ct_array[0]
                                    f_format=ct_array[1]
                                    file_info=FileInfo(
                                    original_size=original_size,
                                    width=width,
                                    height=height,
                                    mode=mode,
                                    f_type=f_type,
                                    f_format=f_format
                                    )


                                    return render(req,'index.html',context={
                                        'error_message':'Your width exceeds actual image bounds...',
                                    'image_resizer_upload':True,'file_info':file_info, 'file_url':image_uri, })
                                            
                
                else:
                    return redirect('/image-resizer?url='+image_uri)




            else:
                return redirect('/image-resizer?url='+image_uri)
    

        

        else:   
            return redirect('/image-resizer?url='+image_uri)
    
 

    else:

        url=req.get_full_path()
            

        parsed=urllib.parse.urlparse(url)
        url_parm=urllib.parse.parse_qs(parsed.query)


        



        if len(url_parm)==1:

            file_url=url_parm['url'][0]
            
            

            if validate_url(file_url):

                

        

                try :
                    image_res=requests.get(file_url,stream=True)
                except:
                    raise NotImplementedError('Invalid URL not implemeneted') 


                if image_res.status_code=='200':
                    raise NotImplementedError('file not found')

            
                        
                ct=image_res.headers["content-type"]
                ct_array=ct.split('/')


                if ct_array[0]=='image' or ct_array[0]=='applicaton':

                    if ct_array[1] in ['png','jpg','jpeg','tiff','webp','bmp']:

                        path=urllib.parse.urlparse(file_url).path

                                
                        if path:
                            if FileSystemStorage().exists(ROOT_PROJECT+path):

                                data= BytesIO(
                                image_res.content)
                                    

                                im=Image.open(data)
                                width, height = im.size
                                mode=im.mode
                                original_size=get_printable_size(float(image_res.headers['content-length']))
                                f_type=ct_array[0]
                                f_format=ct_array[1]
                                file_info=FileInfo(
                                original_size=original_size,
                                width=width,
                                height=height,
                                mode=mode,
                                f_type=f_type,
                                f_format=f_format
                                    )
                                

                                return render(req,'index.html',context={
                                'image_resizer_upload':True,
                                'file_info':file_info,
                                'file_url':file_url,
                                'form_url':'image-resizer/action?url='+file_url

                                })  
                                
                            else:


                                return redirect('/image-resizer?url='+file_url)

                    else:

                        return redirect('/image-resizer?url='+file_url)
                
                else:
                    return redirect('/image-resizer?url='+file_url)



            else:



                return render(req,template_name='index.html',context={
                                 'image_resizer':True,
                                'form_url':'image-resizer',
                                  'error_message':'Unsupported url or Malformed Url...'
                                  }) 
                                  
            

def RepresentsInt(s):
    try: 
        int(s)
        return True
    except ValueError:
        return False   




def validate_url(url):
    regex = re.compile(
        r'^(?:http|ftp)s?://' # http:// or https://
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|' #domain...
        r'localhost|' #localhost...
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})' # ...or ip
        r'(?::\d+)?' # optional port
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)   

    return (re.match(regex, url) is not None)   



       
    

class FileInfo :


    def __init__(self,original_size,width,height,f_type,f_format,mode,reduced_size=None,):
        self.reduced_size=reduced_size
        self.original_size=original_size
        self.width=width
        self.height=height
        self.type=f_type
        self.format=f_format
        self.mode=mode





def get_printable_size(byte_size):
    """
    A bit is the smallest unit, it's either 0 or 1
    1 byte = 1 octet = 8 bits
    1 kB = 1 kilobyte = 1000 bytes = 10^3 bytes
    1 KiB = 1 kibibyte = 1024 bytes = 2^10 bytes
    1 KB = 1 kibibyte OR kilobyte ~= 1024 bytes ~= 2^10 bytes (it usually means 1024 bytes but sometimes it's 1000... ask the sysadmin ;) )
    1 kb = 1 kilobits = 1000 bits (this notation should not be used, as it is very confusing)
    1 ko = 1 kilooctet = 1000 octets = 1000 bytes = 1 kB
    Also Kb seems to be a mix of KB and kb, again it depends on context.
    In linux, a byte (B) is composed by a sequence of bits (b). One byte has 256 possible values.
    More info : http://www.linfo.org/byte.html
    """
    BASE_SIZE = 1024.00
    MEASURE = ["B", "KB", "MB", "GB", "TB", "PB"]

    def _fix_size(size, size_index):
        if not size:
            return "0"
        elif size_index == 0:
            return str(size)
        else:
            return "{:.3f}".format(size)

    current_size = byte_size
    size_index = 0

    while current_size >= BASE_SIZE and len(MEASURE) != size_index:
        current_size = current_size / BASE_SIZE
        size_index = size_index + 1

    size = _fix_size(current_size, size_index)
    measure = MEASURE[size_index]
    return size + measure



def save_from_url(url,fn):
    with contextlib.closing(urllib.request.urlopen(url)) as response:
        with contextlib.closing(BytesIO(
            response.read()
        )) as file:
            file.seek(0)

            django_file = File(file, fn)

            return build_fs_url(FileSystemStorage().save(fn, django_file))
            
