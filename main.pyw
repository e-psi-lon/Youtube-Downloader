import shutil
import sys
import threading
import tkinter as tk
from tkinter import filedialog, messagebox
import ctypes
import os

if not int(str(sys.version_info[0]) + str(sys.version_info[1])) == 311:
    messagebox.showerror('Error',
                         f'This program requires Python 3.11 to run (you are using Python {str(sys.version_info[0])}.'
                         f'{str(sys.version_info[1])})')
    exit()

try:
    import pygame
    import pygame_gui
    import requests
    from pytube import YouTube
    from moviepy.editor import VideoFileClip
    from proglog import ProgressBarLogger
except Exception as e:
    if messagebox.askyesno('Error',
                           f'An error occurred: {e}\n All the required modules are not installed, do you want to '
                           f'install them? (This will take a few minutes)'):
        import subprocess

        messagebox.showinfo('Downloading', 'The download will start when you close this window. The program will '
                                           'restart once the download is complete.')
        subprocess.call(['python', '-m', 'pip', 'install', '--upgrade', 'pip'])
        subprocess.call(['pip', 'install', '-r', 'requirements.txt'])
        import pygame
        import pygame_gui
        import requests
        from pytube import YouTube
        from moviepy.editor import VideoFileClip
        from proglog import ProgressBarLogger
    else:
        exit()


class Logger(ProgressBarLogger):
    def __init__(self, ui, input_video: VideoFileClip, init_state=None, bars=None, ignored_bars=None,
                 logged_bars='all', min_time_interval=0, ignore_bars_under=0):
        super().__init__(init_state, bars, ignored_bars, logged_bars, min_time_interval,
                         ignore_bars_under)
        self.ui = ui
        self.video = input_video
        self.progress_bar = 0

    def callback(self, message=None):
        bars = dict(self.bars)
        if len(bars) == 0:
            if self.ui.progress_.text != 'Starting conversion...':
                self.ui.progress_.change_text('Starting conversion...')
        elif len(list(bars.keys())) == 1 and bars['chunk']["index"] != -1:
            if self.ui.progress_.text != 'Converting chunks...':
                self.ui.progress_.change_text('Converting chunks...')
            self.progress_bar = (bars['chunk']['index'] / bars['chunk']['total']) * 100
            self.ui.progress.set_current_progress(self.progress_bar)
        elif len(list(bars.keys())) == 2 and bars['t']["index"] != -1:
            if self.ui.progress_.text != 'Finalizing conversion...':
                self.ui.progress_.change_text('Finalizing conversion...')
                self.ui.progress.set_current_progress(0)
            self.progress_bar = (bars['t']['index'] / bars['t']['total']) * 100
            self.ui.progress.set_current_progress(self.progress_bar)


class CustomUILabel(pygame_gui.elements.UILabel):
    def __init__(self, window: pygame.Surface, background_color: tuple[int, int, int], *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.window = window
        self.background_color = background_color

    def change_text(self, text: str):
        relative = self.relative_rect
        self.window.fill(self.background_color,
                         pygame.Rect(relative.left, relative.top, relative.width, relative.height))
        self.text = text
        self.rebuild()


class CustomUIImage(pygame_gui.elements.UIImage):
    def __init__(self, window: pygame.Surface, background_color: tuple[int, int, int], *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.window = window
        self.background_color = background_color

    def change_image(self, image: pygame.Surface | pygame.SurfaceType):
        relative = self.relative_rect
        self.window.fill(self.background_color,
                         pygame.Rect(relative.left, relative.top, relative.width, relative.height))
        self.image = image
        self.rebuild()


class YoutubeDownloader:
    def __init__(self):
        self.download_format = 'mp4'
        self.video_url = None
        self.path = '.'
        self.SCREENSIZE = (900, 550)
        self.COLOR = (54, 57, 63)
        pygame.init()
        self.window = pygame.display.set_mode(self.SCREENSIZE)
        pygame.display.set_caption('YouTube Downloader')
        pygame.display.set_icon(pygame.image.load('assets/icon.png'))
        self.clock = pygame.time.Clock()
        self.window.fill(self.COLOR)
        self.manager = pygame_gui.UIManager(self.SCREENSIZE, 'assets/theme.json')
        self.font = pygame.font.SysFont('Arial', 20)

        if not os.path.exists('./cache'):
            os.mkdir('./cache')
        self.url_entry = pygame_gui.elements.UITextEntryLine(relative_rect=pygame.Rect(50, 50, 800, 30),
                                                             manager=self.manager)
        self.url_entry.set_text('https://www.youtube.com/watch?v=dQw4w9WgXcQ')
        self.preview_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect(50, 100, 120, 30), text='Preview',
                                                           manager=self.manager)
        self.download_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect(200, 100, 120, 30),
                                                            text='Download',
                                                            manager=self.manager)
        self.directory_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect(350, 100, 120, 30),
                                                             text='Directory',
                                                             manager=self.manager)
        self.menu = pygame_gui.elements.UIDropDownMenu(relative_rect=pygame.Rect(500, 100, 120, 30),
                                                       manager=self.manager,
                                                       options_list=['MP4', 'AVI', 'MOV', 'MP3', 'OGG'],
                                                       starting_option='MP4')

        self.connect = pygame_gui.elements.UIButton(relative_rect=pygame.Rect(650, 100, 120, 30), text='Connect',
                                                    manager=self.manager)

        self.titre_ = CustomUILabel(window=self.window, background_color=self.COLOR,
                                    relative_rect=pygame.Rect(30, 150, 300, 30),
                                    text='Video title:',
                                    manager=self.manager)
        self.titre = CustomUILabel(window=self.window, background_color=self.COLOR,
                                   relative_rect=pygame.Rect(35, 175, 500, 30), text='',
                                   manager=self.manager)
        self.duration__ = CustomUILabel(window=self.window, background_color=self.COLOR,
                                        relative_rect=pygame.Rect(30, 200, 300, 30),
                                        text='Video duration:',
                                        manager=self.manager)
        self.duration_ = CustomUILabel(window=self.window, background_color=self.COLOR,
                                       relative_rect=pygame.Rect(35, 225, 500, 30), text='',
                                       manager=self.manager)
        self.description_ = CustomUILabel(window=self.window, background_color=self.COLOR,
                                          relative_rect=pygame.Rect(30, 250, 300, 30),
                                          text='Video description:',
                                          manager=self.manager)
        self.description = pygame_gui.elements.UITextBox(html_text='', relative_rect=pygame.Rect(35, 300, 450, 200),
                                                         manager=self.manager)
        self.preview_ = CustomUILabel(window=self.window, background_color=self.COLOR,
                                      relative_rect=pygame.Rect(550, 200, 300, 30),
                                      text='Video thumbnail:',
                                      manager=self.manager)
        self.preview_elem = CustomUIImage(window=self.window, background_color=self.COLOR,
                                          relative_rect=pygame.Rect(550, 250, 300, 200),
                                          image_surface=pygame.image.load('assets/youtube.png'), manager=self.manager)
        self.progress_ = CustomUILabel(window=self.window, background_color=self.COLOR,
                                       relative_rect=pygame.Rect(650, 125, 300, 30),
                                       text='Progress',
                                       manager=self.manager)
        self.progress = pygame_gui.elements.UIProgressBar(relative_rect=pygame.Rect(650, 150, 200, 30),
                                                          manager=self.manager,
                                                          visible=False)
        is_running = True
        while is_running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    is_running = False
                elif event.type == pygame_gui.UI_BUTTON_PRESSED:
                    if event.ui_element == self.preview_button:
                        self.window.fill(self.COLOR, pygame.Rect(-280, 250, 800, 30))
                        self.preview_launch()
                    elif event.ui_element == self.download_button:
                        if messagebox.askyesno('Download',
                                               'The download will start The window may freeze, '
                                               'do you want to continue?'):
                            download_thread = threading.Thread(target=self.start_download)
                            download_thread.start()
                        self.window.fill(self.COLOR, pygame.Rect(-280, 250, 800, 30))
                    elif event.ui_element == self.directory_button:
                        self.choose_directory()
                    elif event.ui_element == self.connect:
                        # On affiche une popup pour se connecter à son compte google
                        response = messagebox.askyesnocancel("Connect to your google account",
                                                             "Do you want to keep your account connected?",
                                                             default=messagebox.YES)
                        if response is None:
                            continue
                        if response:
                            YouTube('https://www.youtube.com/watch?v=dQw4w9WgXcQ', use_oauth=True,
                                    allow_oauth_cache=True)
                        else:
                            YouTube('https://www.youtube.com/watch?v=dQw4w9WgXcQ', use_oauth=True,
                                    allow_oauth_cache=False)

                elif event.type == pygame_gui.UI_DROP_DOWN_MENU_CHANGED:
                    if event.ui_element == self.menu:
                        match event.text:
                            case 'MP4':
                                self.download_format = 'mp4'
                            case 'AVI':
                                self.download_format = 'avi'
                            case 'MOV':
                                self.download_format = 'mov'
                            case 'OGG':
                                self.download_format = 'ogg'
                            case _:
                                pass
                        self.window.fill(self.COLOR, pygame.Rect(500, 100, 400, 150))
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    self.window.fill(self.COLOR, pygame.Rect(500, 100, 400, 150))
                self.manager.process_events(event)
            self.manager.update(self.clock.tick(60) / 1000.0)
            self.manager.draw_ui(self.window)
            pygame.display.update()
        pygame.quit()

    def choose_directory(self):
        """Choose the directory"""
        root = tk.Tk()
        root.withdraw()
        self.path = filedialog.askdirectory(parent=root, initialdir='.', title='Please select a directory')
        root.destroy()

    def start_download(self):
        """Download the video"""
        root = tk.Tk()
        root.withdraw()
        try:
            self.progress.visible = True
            self.progress.set_current_progress(0)
            self.progress_.change_text('Downloading...')
            video = YouTube(self.url_entry.get_text(),
                            on_progress_callback=lambda stream, _, bytes_remaining: self.progress.set_current_progress(
                                100 - (bytes_remaining / stream.filesize * 100)))
            file = video.streams.filter(progressive=True, file_extension='mp4').order_by('resolution').desc().first()
            if self.download_format in ['mp3', 'ogg']:
                file.download("./cache")
                video_ = VideoFileClip(f"./cache/{video.title}.mp4")
                self.progress.set_current_progress(0)
                self.progress_.change_text("Converting...")
                logger = Logger(self, video_)
                video_.audio.write_audiofile(f'{self.path}/{video.title}.{self.download_format}',
                                             codec=file.audio_codec,
                                             logger=logger, fps=30)
                return
            elif self.download_format in ['mov', 'avi']:
                file.download('./cache')
                video_ = VideoFileClip(f'./cache/{video.title}.mp4')
                self.progress.set_current_progress(0)
                self.progress_.change_text('Converting...')
                logger = Logger(self, video_)
                video_.write_videofile(f'{self.path}/{video.title}.{self.download_format}', codec=file.video_codec,
                                       audio_codec=file.audio_codec,
                                       temp_audiofile='./cache/temp.m4a', remove_temp=True, fps=30, threads=4,
                                       logger=logger)
                os.remove(f'./cache/{video.title}.mp4')
            else:
                file.download(self.path)
            root = tk.Tk()
            root.withdraw()
            if messagebox.askyesno('Download finished',
                                   'The video has been downloaded, do you want to open the folder?'):
                os.startfile(self.path)
            self.progress.set_current_progress(0)
            self.progress.visible = False
            self.window.fill(self.COLOR, pygame.Rect(self.progress.relative_rect.left, self.progress.relative_rect.top,
                                                     self.progress.relative_rect.width,
                                                     self.progress.relative_rect.height))
            self.progress_.change_text('Download finished')
        except Exception as error:
            messagebox.showerror('Error', f'An error occurred: {error}')
            self.progress.set_current_progress(0)
            self.progress_.change_text('Download failed')
        root.destroy()

    def preview_launch(self):
        """Get some info of the video"""
        root = tk.Tk()
        root.withdraw()
        if self.url_entry.get_text() == '':
            title = 'No video provided'
            final = 'No video provided'
            desc = 'No video provided'
            pygame.image.load('assets/youtube.png')
        else:
            try:
                video = YouTube(self.url_entry.get_text())
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
                # On redimensionne l'image sans la rogner
                if image.get_width() > 300 or image.get_height() > 200:
                    image = pygame.transform.smoothscale(image, (300, 200))
                self.preview_elem.change_image(image)
                os.remove('cache/thumbnail.png')
                desc = video.description
            except Exception as error:
                title = 'Error'
                final = 'Error'
                desc = 'Error'
                image = pygame.image.load('assets/youtube.png')
                self.preview_elem.change_image(image)
                messagebox.showerror('Error', f'An error occurred: {error}')
        self.titre.change_text(title)
        self.duration_.change_text(final)
        try:
            self.description.set_text(str(desc))
        except Exception as error:
            messagebox.showerror('Error', f'An error occurred: {error} (but the program will continue)')


if __name__ == '__main__':
    if os.name == 'nt':
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID('YouTube Downloader')
    else:
        pass
    YoutubeDownloader()
