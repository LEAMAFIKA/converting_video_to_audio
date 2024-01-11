import os
from kivy.clock import Clock
from kivy.lang import Builder
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.gridlayout import GridLayout
from kivy.uix.filechooser import FileChooserListView
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivymd.app import MDApp
from kivymd.uix.button import MDRaisedButton
from kivymd.uix.textfield import MDTextField

from moviepy.editor import VideoFileClip

from kivy.core.window import Window
from kivy.uix.slider import Slider
from kivy.core.audio import SoundLoader
from kivy.utils import get_color_from_hex

# Define the Kivy language string (KV) for the app layout
KV = '''
BoxLayout:
    orientation: 'vertical'

    MDTopAppBar:
        title: "Convert Video to Audio"
        md_bg_color: app.theme_cls.primary_color


    VideoToAudioConverter:
        id: video_converter

'''

# Define the main widget, VideoToAudioConverter, which is a GridLayout
class VideoToAudioConverter(GridLayout):
    def __init__(self, **kwargs):
        super(VideoToAudioConverter, self).__init__(cols=1, spacing=15, padding=[10, 30, 10, 10])

        self.audio = None  # Sound object for audio playback
        self.audio_position = 0

        # Create an MDTextField for displaying the selected video path
        self.video_path_label = MDTextField(hint_text="Selected video", mode="rectangle", readonly=True)
        self.add_widget(self.video_path_label)

        # my grid button
        my_grid_button = GridLayout(cols=2, spacing=25, padding=10)

        # Create a button for choosing a file, bind it to the choose_file method
        self.choose_file_button = Button(
            text='Choose File',
            size_hint=(None, None),  # Set size_hint to (None, None) to disable automatic size calculation
            size=(350, 100),  # Set the desired size of the button
            background_color=(0.5, 0, 0.5, 1),
        )
        self.choose_file_button.bind(on_release=self.choose_file)
        my_grid_button.add_widget(self.choose_file_button)

        # Create a button for converting video to audio, bind it to the convert_video_to_audio method
        self.convert_button = Button(
            text='Convert to Audio',
            size_hint=(None, None),  # Set size_hint to (None, None) to disable automatic size calculation
            size=(350, 100),  # Set the desired size of the button
            background_color=(0, 0, 1, 1)
        )
        self.convert_button.bind(on_release=self.convert_video_to_audio)
        my_grid_button.add_widget(self.convert_button)

        self.add_widget(my_grid_button)

        # my grid slider play_button
        my_grid_play = GridLayout(cols=2, spacing=25, padding=10)

        # Create a Slider for controlling the audio playback position
        self.audio_slider = Slider(min=0, max=1, value=0, step=0.01, value_track=True,
                                   value_track_color=[0.5, 0, 0.5, 1])
        # self.audio_slider.value_track_color = get_color_from_hex('#000000')  # Set track color to blue
        self.audio_slider.bind(value=self.set_audio_position)
        self.add_widget(self.audio_slider)

        # Create a Play button for starting the audio playback
        self.play_button = Button(
            text='Play',
            size_hint=(None, None),
            size=(350, 100),
            background_color=(0, 1, 0, 1)
        )
        self.play_button.bind(on_release=self.play_audio)
        my_grid_play.add_widget((self.play_button))

        # Create a Stop button for stopping the audio playback
        self.stop_button = Button(
            text='Stop',
            size_hint=(None, None),
            size=(350, 100),
            background_color=(1, 0, 0, 1)
        )
        self.stop_button.bind(on_release=self.stop_audio)
        # self.add_widget(self.stop_button)
        my_grid_play.add_widget(self.stop_button)
        self.add_widget(my_grid_play)

        # Create a label for displaying the conversion status
        self.status_label = Label(text='', halign='center', valign='middle')
        self.add_widget(self.status_label)

    # Method to convert video to audio
    def convert_video_to_audio(self, instance):
        if hasattr(self, 'video_path') and self.video_path:
            video_clip = VideoFileClip(self.video_path)
            audio_folder_path = os.path.dirname(self.video_path)
            self.audio_output_path = os.path.join(audio_folder_path, 'output_audio.mp3')
            audio_clip = video_clip.audio
            audio_clip.write_audiofile(self.audio_output_path, codec="mp3")
            audio_clip.close()
            self.status_label.text = f'Conversion successful! Audio saved at:\n{self.audio_output_path}'
            self.status_label.color = (0, 1, 0, 1)  # Set the color to green

        else:
            self.status_label.text = 'Please select a video file.'
            self.status_label.color = (1, 0, 0, 1)  # Set the color to red

    # Method to handle file chooser button press
    def choose_file(self, *args):
        # Create a FileChooserListView and bind the file_selected method to the selection event
        file_chooser = FileChooserListView(filters=['*.mp4'])
        file_chooser.bind(selection=self.file_selected)

        # Create a Popup to display the FileChooserListView
        self.popup = Popup(title='Choose a File', content=file_chooser, size_hint=(None, None), size=(600, 600))
        self.popup.open()

    # Method to handle file selection in the FileChooserListView
    def file_selected(self, chooser, selection):
        if selection:
            file_path = selection[0]
            self.video_path_label.text = f'Selected video: {file_path}'
            self.video_path = file_path
            # close the popup
            self.popup.dismiss()

    # Method to play the audio
    def play_audio(self, instance):
        if hasattr(self, 'audio_output_path') and self.audio_output_path:
            self.audio = SoundLoader.load(self.audio_output_path)
            if self.audio:
                self.audio.play()
                Clock.schedule_interval(self.update_audio_position,
                                        0.1)  # Schedule callback to update the audio position every 0.1 seconds

    # Method to stop the audio
    def stop_audio(self, instance):
        if self.audio:
            self.audio.stop()

    def update_audio_position(self, dt):
        if self.audio and self.audio.state == 'play':
            self.audio_position += 0.1  # Update the current audio position by 0.1 seconds
            audio_length = self.audio.length
            self.audio_slider.value = self.audio_position / audio_length

    # Method to set the audio playback position
    def set_audio_position(self, instance, value):
        if self.audio:
            audio_position = value * self.audio.length
            self.audio.seek(audio_position)


# Define the main app class
class VideoToAudioConverterApp(MDApp):
    def build(self):
        # Set the app theme style and window size
        self.theme_cls.theme_style = "Light"  # or "dark"
        Window.size = (400, 400)
        # Initialize pygame mixer for audio playback

        # Load the app layout from the Kivy language string
        return Builder.load_string(KV)


# Run the app
if __name__ == '__main__':
    VideoToAudioConverterApp().run()()