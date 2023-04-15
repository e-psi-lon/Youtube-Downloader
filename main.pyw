import shutil
import sys
import threading
import tkinter as tk
from tkinter import filedialog, messagebox
import os

if int(str(sys.version_info[0]) + str(sys.version_info[1])) == 311:
    try:
        import pygame
        import pygame_gui
        import requests
        from pytube import YouTube
        from moviepy.editor import VideoFileClip
    except Exception as e:
        if messagebox.askyesno('Error',
                               f'An error occurred: {e}\n All the required modules are not installed, do you want to '
                               f'install them? (This will take a few minutes)'):
            import subprocess
            messagebox.showinfo('Downloading', 'The download will start when you close this window. The program will '
                                               'restart once the download is complete.')
            subprocess.call(['pip', 'install', '-r', 'requirements.txt'])
            import pygame
            import pygame_gui
            import requests
            from pytube import YouTube
            from moviepy.editor import VideoFileClip
        else:
            exit()
    download_format = 'mp4'
    video_url = None
    path = '.'
    SCREENSIZE = (900, 550)
    pygame.init()
    window = pygame.display.set_mode(SCREENSIZE)
    pygame.display.set_caption('YouTube Downloader')
    pygame.display.set_icon(pygame.image.load('assets/icon.ico'))
    clock = pygame.time.Clock()
    window.fill((54, 57, 63))
    manager = pygame_gui.UIManager(SCREENSIZE, 'assets/theme.json')
    font = pygame.font.SysFont('Arial', 20)
    if not os.path.exists('./cache'):
        os.mkdir('./cache')


    def choose_directory():
        """Choose the directory"""
        global path
        root = tk.Tk()
        root.withdraw()
        path = filedialog.askdirectory(parent=root, initialdir='.', title='Please select a directory')
        root.destroy()


    def start_download():
        """Download the video"""
        global path, url_entry, download_format, progress, progress_
        progress = pygame_gui.elements.UIProgressBar(relative_rect=pygame.Rect(650, 150, 200, 30), manager=manager)
        root = tk.Tk()
        root.withdraw()
        try:
            progress.set_current_progress(0)
            relative = progress_.relative_rect
            progress_.kill()
            window.fill((54, 57, 63), pygame.Rect(relative.left, relative.top, relative.width, relative.height))
            progress_ = pygame_gui.elements.UILabel(
                relative_rect=pygame.Rect(relative.left, relative.top, relative.width, relative.height),
                text='Downloading...', manager=manager)
            video = YouTube(url_entry.get_text(),
                            on_progress_callback=lambda stream, chunk, bytes_remaining: progress.set_current_progress(
                                (bytes_remaining / video.length) * 100))
            file = video.streams.filter(progressive=True, file_extension='mp4').order_by('resolution').desc().first()
            if download_format != 'mp4':
                file.download('./cache')
                video_ = VideoFileClip(f'./cache/{video.title}.mp4')
                progress.set_current_progress(0)
                relative = progress_.relative_rect
                progress_.kill()
                window.fill((54, 57, 63), pygame.Rect(relative.left, relative.top, relative.width, relative.height))
                progress_ = pygame_gui.elements.UILabel(
                    relative_rect=pygame.Rect(relative.left, relative.top, relative.width, relative.height),
                    text='Converting...', manager=manager)
                video_.write_videofile(f'{path}/{video.title}.{download_format}', codec='libx264', audio_codec='aac',
                                       temp_audiofile='./cache/temp.m4a', remove_temp=True, fps=30, threads=4,
                                       logger='bar')
                os.remove(f'./cache/{video.title}.mp4')
            else:
                file.download(path)
            if messagebox.askyesno('Download finished',
                                   'The video has been downloaded, do you want to open the folder?'):
                os.startfile(path)
        except Exception as error:
            messagebox.showerror('Error', f'An error occurred: {error}')
            relative = progress_.relative_rect
            progress_.kill()
            window.fill((54, 57, 63), pygame.Rect(relative.left, relative.top, relative.width, relative.height))
            progress_ = pygame_gui.elements.UILabel(
                relative_rect=pygame.Rect(relative.left, relative.top, relative.width, relative.height),
                text='Download failed', manager=manager)
        root.destroy()


    def preview_launch():
        """Get some info of the video"""
        global preview_elem, url_entry, titre, duration_, description
        root = tk.Tk()
        root.withdraw()
        if url_entry.get_text() == '':
            title = 'No video provided'
            final = 'No video provided'
            desc = 'No video provided'
            pygame.image.load('assets/youtube.png')
        else:
            try:
                video = YouTube(url_entry.get_text())
                title = video.title
                duration = video.length
                if duration >= 60:
                    if duration >= 3600:
                        hour = int(duration / 3600)
                        duration = duration - 3600 * hour
                        minutes = int(duration / 60)
                        duration = duration - 60 * minutes
                        sec = duration
                        final = f'{hour}h {minutes}min {sec}s'
                    else:
                        minutes = int(duration / 60)
                        duration = duration - 60 * minutes
                        sec = duration
                        final = f'{minutes}min {sec}s'
                else:
                    final = f'{duration}s'
                with open('cache/thumbnail.png', 'wb') as f:
                    shutil.copyfileobj(requests.get(video.thumbnail_url, stream=True).raw, f)
                image = pygame.image.load('cache/thumbnail.png')
                relative = preview_elem.relative_rect
                preview_elem.kill()
                window.fill((54, 57, 63), pygame.Rect(relative.left, relative.top, relative.width, relative.height))
                preview_elem = pygame_gui.elements.UIImage(
                    relative_rect=pygame.Rect(relative.left, relative.top, relative.width, relative.height),
                    image_surface=image, manager=manager)
                os.remove('cache/thumbnail.png')
                desc = video.description
            except Exception as error:
                title = 'Error'
                final = 'Error'
                desc = 'Error'
                image = pygame.image.load('assets/youtube.png')
                relative = preview_elem.relative_rect
                preview_elem.kill()
                window.fill((54, 57, 63), pygame.Rect(relative.left, relative.top, relative.width, relative.height))
                preview_elem = pygame_gui.elements.UIImage(
                    relative_rect=pygame.Rect(relative.left, relative.top, relative.width, relative.height),
                    image_surface=image, manager=manager)
                messagebox.showerror('Error', f'An error occurred: {error}')
        relative = titre.relative_rect
        titre.kill()
        window.fill((54, 57, 63), pygame.Rect(relative.left, relative.top, relative.width, relative.height))
        titre = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(relative.left, relative.top, relative.width, relative.height), text=title,
            manager=manager)
        relative = duration_.relative_rect
        duration_.kill()
        window.fill((54, 57, 63), pygame.Rect(relative.left, relative.top, relative.width, relative.height))
        duration_ = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(relative.left, relative.top, relative.width, relative.height), text=final,
            manager=manager)
        relative = description.relative_rect
        description.kill()
        window.fill((54, 57, 63), pygame.Rect(relative.left, relative.top, relative.width, relative.height))
        description = pygame_gui.elements.UITextBox(
            relative_rect=pygame.Rect(relative.left, relative.top, relative.width, relative.height), html_text=desc,
            manager=manager)


    url_entry = pygame_gui.elements.UITextEntryLine(relative_rect=pygame.Rect(50, 50, 800, 30), manager=manager)
    url_entry.set_text('https://www.youtube.com/watch?v=dQw4w9WgXcQ')
    preview_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect(50, 100, 120, 30), text='Preview',
                                                  manager=manager)
    download_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect(200, 100, 120, 30), text='Download',
                                                   manager=manager)
    directory_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect(350, 100, 120, 30), text='Directory',
                                                    manager=manager)
    menu = pygame_gui.elements.UIDropDownMenu(relative_rect=pygame.Rect(500, 100, 120, 30), manager=manager,
                                              options_list=['MP4', 'AVI', 'MOV'], starting_option='MP4')
    titre_ = pygame_gui.elements.UILabel(relative_rect=pygame.Rect(30, 150, 300, 30), text='Video title:',
                                         manager=manager)
    titre = pygame_gui.elements.UILabel(relative_rect=pygame.Rect(35, 175, 500, 30), text='', manager=manager)
    duration__ = pygame_gui.elements.UILabel(relative_rect=pygame.Rect(30, 200, 300, 30), text='Video duration:',
                                             manager=manager)
    duration_ = pygame_gui.elements.UILabel(relative_rect=pygame.Rect(35, 225, 500, 30), text='', manager=manager)
    description_ = pygame_gui.elements.UILabel(relative_rect=pygame.Rect(30, 250, 300, 30), text='Video description:',
                                               manager=manager)
    description = pygame_gui.elements.UITextBox(html_text='', relative_rect=pygame.Rect(35, 300, 450, 200),
                                                manager=manager)
    preview_ = pygame_gui.elements.UILabel(relative_rect=pygame.Rect(550, 200, 300, 30), text='Video thumbnail:',
                                           manager=manager)
    preview_elem = pygame_gui.elements.UIImage(relative_rect=pygame.Rect(550, 250, 300, 200),
                                               image_surface=pygame.image.load('assets/youtube.png'), manager=manager)
    progress_ = pygame_gui.elements.UILabel(relative_rect=pygame.Rect(650, 125, 300, 30), text='', manager=manager)
    progress = None
    is_running = True
    while is_running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                is_running = False
            elif event.type == pygame_gui.UI_BUTTON_PRESSED:
                if event.ui_element == preview_button:
                    window.fill((54, 57, 63), pygame.Rect(-280, 250, 800, 30))
                    preview_launch()
                elif event.ui_element == download_button:
                    if messagebox.askyesno('Download',
                                           'The download will start The window may freeze, do you want to continue?'):
                        download_thread = threading.Thread(target=start_download)
                        download_thread.start()
                    window.fill((54, 57, 63), pygame.Rect(-280, 250, 800, 30))
                elif event.ui_element == directory_button:
                    choose_directory()
            elif event.type == pygame_gui.UI_DROP_DOWN_MENU_CHANGED:
                if event.ui_element == menu:
                    if event.text == 'MP4':
                        download_format = 'mp4'
                    elif event.text == 'AVI':
                        download_format = 'avi'
                    elif event.text == 'MOV':
                        download_format = 'mov'
                    window.fill((54, 57, 63), pygame.Rect(500, 100, 400, 100))
            elif event.type == pygame.MOUSEBUTTONDOWN:
                window.fill((54, 57, 63), pygame.Rect(500, 100, 400, 100))
            manager.process_events(event)
        manager.update(clock.tick(60) / 1000.0)
        manager.draw_ui(window)
        pygame.display.update()
    pygame.quit()
else:
    messagebox.showerror('Error',
                         f'This program requires Python 3.11 to run (you are using Python {str(sys.version_info[0])}.'
                         f'{str(sys.version_info[1])})')
