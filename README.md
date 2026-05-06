Since everyone on the internet is an obtuse, unhelpful nerd, here's a script that will extract all the different audio tracks from an MKV file.

You need to have ffmpeg installed. I use WSL on my Windows machine for this, so it's a bash script.

I was utilizing this for OBS capture. You need to enable all the channels in the output section of settings. And you map your inputs via the Audio Mixer in the main pane, there's a gear icon beneath it. You map each audio source to a channel. FYI the default is track 1, so for best results map everything to 1 and each individual track to a dedicated number, ie microphone to 2, desktop audio to 3, etc

The windows exe is published under releases.

