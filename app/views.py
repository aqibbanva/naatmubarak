from django.shortcuts import render,HttpResponse
from django.core.paginator import Paginator
from .models import *
import os
import yt_dlp
from django.http import FileResponse
from django.conf import settings
from django.shortcuts import render, get_object_or_404
import threading
import time
import shutil
import uuid

# Create your views here.

def home(request):
    query = request.GET.get('q', '')  # Search query
    naat_list = NaatVideo.objects.filter(title__icontains=query) if query else NaatVideo.objects.all()
    
    paginator = Paginator(naat_list, 20)  # 20 records per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'app/home.html', {'naat_list': page_obj})


def download_page(request, naat_id):
    naat = get_object_or_404(NaatVideo, id=naat_id)
    return render(request, "app/download.html", {"title": naat.title, "naat_id": naat.id})

def delete_file_later(file_path, delay=10):
    """Delete file after a delay"""
    import time
    time.sleep(delay)
    if os.path.exists(file_path):
        os.remove(file_path)


def download_audio(request, naat_id):
    naat = get_object_or_404(NaatVideo, id=naat_id)
    video_url = naat.video_link

    output_path = os.path.join(settings.MEDIA_ROOT, "downloads")
    if not os.path.exists(output_path):
        os.makedirs(output_path)

    # ✅ Generate a unique file name for each download
    unique_id = str(uuid.uuid4())[:8]  # Short unique ID
    output_file = os.path.join(output_path, f"{unique_id}.%(ext)s")

    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': output_file,
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(video_url, download=True)
        downloaded_file = ydl.prepare_filename(info)
        downloaded_file = downloaded_file.replace('.webm', '.mp3').replace('.m4a', '.mp3')

    if os.path.exists(downloaded_file):
        # ✅ Rename the file to a unique name before sending it
        final_file = os.path.join(output_path, f"Naat_{unique_id}.mp3")
        shutil.move(downloaded_file, final_file)

        # ✅ Delete file automatically after 10 second
        threading.Thread(target=delete_file_later, args=(final_file, 10)).start()

        # ✅ Fix response headers
        response = FileResponse(open(final_file, 'rb'), as_attachment=True, filename=f"Naat_{unique_id}.mp3")
        response["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
        response["Pragma"] = "no-cache"
        response["Expires"] = "0"
        response["Access-Control-Expose-Headers"] = "Content-Disposition"

        return response

    return HttpResponse("Download failed!", status=500)




# def download_audio(request, naat_id):
#     naat = get_object_or_404(NaatVideo, id=naat_id)
#     video_url = naat.video_link

#     output_path = os.path.join(settings.MEDIA_ROOT, "downloads")
#     if not os.path.exists(output_path):
#         os.makedirs(output_path)

#     output_file = os.path.join(output_path, "%(title)s.%(ext)s")

#     ydl_opts = {
#         'format': 'bestaudio/best',
#         'outtmpl': output_file,
#         'postprocessors': [{
#             'key': 'FFmpegExtractAudio',
#             'preferredcodec': 'mp3',
#             'preferredquality': '192',
#         }],
#     }

#     with yt_dlp.YoutubeDL(ydl_opts) as ydl:
#         info = ydl.extract_info(video_url, download=True)
#         downloaded_file = ydl.prepare_filename(info)
#         downloaded_file = downloaded_file.replace('.webm', '.mp3').replace('.m4a', '.mp3')

#     if os.path.exists(downloaded_file):
#         # ✅ Delete file after 2 minutes
#         threading.Thread(target=delete_file_later, args=(downloaded_file, 120)).start()
        
#         # ✅ Fix response headers
#         response = FileResponse(open(downloaded_file, 'rb'), as_attachment=True, filename=os.path.basename(downloaded_file))
#         response["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
#         response["Pragma"] = "no-cache"
#         response["Expires"] = "0"
#         response["Access-Control-Expose-Headers"] = "Content-Disposition"
        
#         return response

#     return HttpResponse("Download failed!", status=500)





# def download_audio(request, naat_id):
#     naat = get_object_or_404(NaatVideo, id=naat_id)
#     video_url = naat.video_link

#     output_path = os.path.join(settings.MEDIA_ROOT, "downloads")
#     if not os.path.exists(output_path):
#         os.makedirs(output_path)

#     # Generate dynamic file name
#     ydl_opts = {
#         'format': 'bestaudio/best',
#         'outtmpl': os.path.join(output_path, '%(title)s.%(ext)s'),
#         'postprocessors': [{
#             'key': 'FFmpegExtractAudio',
#             'preferredcodec': 'mp3',
#             'preferredquality': '192',
#         }],
#     }

#     with yt_dlp.YoutubeDL(ydl_opts) as ydl:
#         info = ydl.extract_info(video_url, download=True)
#         title = info.get('title', 'audio')  
#         downloaded_file = os.path.join(output_path, f"{title}.mp3")

#     if os.path.exists(downloaded_file):
#         threading.Thread(target=delete_file_later, args=(downloaded_file, 120)).start()
        
#         # **Response headers fix**
#         response = FileResponse(open(downloaded_file, 'rb'), as_attachment=True)
#         response['Content-Disposition'] = f'attachment; filename="{title}.mp3"'
#         response['Content-Type'] = 'audio/mpeg'  # Ensure correct content type
#         response['Access-Control-Allow-Origin'] = '*'  # Allow CORS for AJAX
#         return response
#     else:
#         return HttpResponse("Download failed!", status=500)
    

def search_naats(request):
    query = request.GET.get('q', '').strip().lower()
    naats = NaatVideo.objects.all()

    if query:
        naats = [naat for naat in naats if any(query in tag for tag in naat.get_tags())]

    return render(request, 'app/search_results.html', {'naats': naats, 'query': query})
