# SDdataprep
About:<br>
This does not create the initial datasets. This simply looks into a specified folder and pulls up the images and text files of the same name. It also looks into all text files in the folder and generates a list of tags and sorts them based on frequency. You can add multiple tags at once, it will automatically separate them based on the commas. It will also checks for duplicate tags before adding them, though if there is a small difference in wording it will miss it. If the text file does not exist you can create it when you click save. You can also save your changes to a different directory keeping your original data unmodified. I would still back it up.<br>

Dependencies:<br>
pip install Pillow<br>

Usage:<br>
python dataprep.py<br>

Run python scripts without console window by changing script type to "*.pyw"<br>

Known Issues:<br>
-Sometimes glitches out in folders with 1 or 2 images. (I think I fixed that)<br>
-Issues with multiple image file types.<br>
-Need to add scroll bars to the cells/tags portion of the window. Making window larger fixes it for now.<br>
-Text files, such as the ones A1111 make, with multiple lines and tags, cause issues with the first and last tags on the 2nd or higher line. I dont know why yet.
(Temp fix is to right click those cells and modify the text, change case, and it will act normal after that.)

Planned Features:<br>
(Most likely to get done if I dont get lazy.)<br>
-Want to make the cells/tags columns change size dynamically, or at least user selected.<br>
-Make it possible to add/delete a specific tag from across all files.<br>
-Autocomplete tags while typing.<br>
-Add some sort of basic image editing(stretching, canvas size, crop)

Dream Sheet:<br>
(I doubt I will be able to accomplish by myself.)<br>
-And options for user options to select which colors they want specific tags to be.<br>
-Add option to create initial tags for all images using danbooru.<br>
-Drag and Drop functionality to cell tags.<br>
-Dynamically sized cell/tag list, no longer on a grid, just shoving them in until they have to wrap around the given work space.<br>
