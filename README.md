# SDdataprep
About:<br>
This does not create the initial datasets. This simply looks into a specified folder and pulls up the images and text files of the same name. If the text file does not exist you can create it when you click save. You can also save your changes to a different directory keeping your origonal data unmodified. I would still back it up.<br>

Dependancies:<br>
pip install Pillow<br>

Usage:<br>
python dataprep.py<br>

Run python scripts without console window by changing script type to "*.pyw"<br>

Lingering issues:<br>
-Sometimes glitches out in folders with 1 or 2 images. (I think I fixed that)<br>
-Issues with multiple image file types.<br>
-Can not overwrite images, Im not sure what the issue is, but I think I am locking the file and its not unlocking it. Will look into it later.<br>
-Need to add scroll bars to the cells/tags portion of the window. Making window larger fixes it for now.<br>
ChatGPT lost them when I made a bunch of other changes, and I knew I could get them back later. I just havent gotten around to it.<br>

Features to Add:<br>
(Most likely to get done if I dont get lazy.)<br>
-Night Mode, make it darker.<br>
-Want to make the cells/tags columns change size dynamically, or at least user selected.<br>
-Make it possible to add/delete a specific tag from across all files.<br>
-Autocomplete tags while typing, using a very simple way.<br>
-Import ImageMagick into the project and use that to modify images/file types/sizes/etc<br>

Dream Sheet:<br>
(I doubt I will be able to accomplish by myself.)<br>
-And options for user options to select which colors they want specific tags to be.<br>
-Add option to create initial tags for all images using danbooru.<br>
-Drag and Drop functionality to cell tags.<br>
-Dynamically sized cell/tag list, no longer on a grid, just shoving them in untill they have to wrap around the given work space.<br>
