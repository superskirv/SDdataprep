# SDdataprep
About:
This does not create the initial datasets. This simply looks into a specified folder and pulls up the images and text files of the same name. If the text file does not exist you can create it when you click save. You can also save your changes to a different directory keeping your origonal data unmodified. I would still back it up.

Latest Version can be found on my github.
https://github.com/superskirv/SDdataprep

Dependancies:
pip install Pillow

Usage:
python dataprep.py

Run python scripts without console window by changing script type to "*.pyw"

Lingering issues:
-Sometimes glitches out in folders with 1 or 2 images. (I think I fixed that)
-Issues with multiple image file types.
-Can not overwrite images, Im not sure what the issue is, but I think I am locking the file and its not unlocking it. Will look into it later.
-Need to add scroll bars to the cells/tags portion of the window. Making window larger fixes it for now.
ChatGPT lost them when I made a bunch of other changes, and I knew I could get them back later. I just havent gotten around to it.

Features to Add:
(Most likely to get done if I dont get lazy.)
-Night Mode, make it darker.
-Want to make the cells/tags columns change size dynamically, or at least user selected.
-Make it possible to add/delete a specific tag from across all files.
-Autocomplete tags while typing, using a very simple way.
-Import ImageMagick into the project and use that to modify images/file types/sizes/etc

Dream Sheet:
(I doubt I will be able to accomplish by myself.)
-And options for user options to select which colors they want specific tags to be.
-Add option to create initial tags for all images using danbooru.
-Drag and Drop functionality to cell tags.
-Dynamically sized cell/tag list, no longer on a grid, just shoving them in untill they have to wrap around the given work space.
