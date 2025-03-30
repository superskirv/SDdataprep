# SDdataprep
<hr>
About:<br>
Complete redesign. I plan to add the tiles back at some point, as well as adding other featues I enjoyed. However until then please make do with this limited format.<br>

<br>This is designed to help you create/modify/sort tags for stable diffusion training. This does not create the initial datasets. This simply looks into a specified folder and pulls up the images and text files of the same name. It also looks into all text files in the folder and generates a list of tags sorted based on frequency. You can add multiple tags at once, it will automatically separate them based on the commas. It will also checks for duplicate tags before adding them, though if there is a small difference in wording it will miss it. If the text file does not exist you can create it when you click save.<br>

<br>Features:<br>
-Add multiple tags manually(separated by comma)<br>
-Remove multiple selected tags.<br>
-Remembers last selected tags on new images<br>
-Convert images to png<br>
-Resize images to a max side of 1536, rounding the other side to nearest 64.<br>
-List tags from all image txt files.<br>
-Reorder tags manually by moving them up or down(single, or as groups)<br>
-Auto saves when tags added or removed.<br>
-Tag List, and Global Tag lists.<br>
-Search(a single tag only) in dropdown after typing.<br>

<br>Tested on Linux.<br>

<br>Dependencies:<br>
(Installed automatically when you run the script.)<br>
pillow<br>
natsort<br>

<br>Usage:<br>
python dataprep.py<br>

<br>Run python scripts without console window(on windows) by changing script type to "*.pyw"<br>

<br>Known Issues:<br>
-Images are strectch/squished to the nearest 64th pixel when shrink is applied.<br>
-Deleted images will cause errors. Re-Open the same directory to fix.<br>

<br>Planned Features:<br>
(Most likely to get done if I dont get lazy.)<br>
-Add configuration json file<br>
-Add image size configurations.<br>
-Add Undo/Redo Buttons.<br>
-Add Reload buttons.<br>
-View all images of a specific tag(s).<br>
-add/delete a specific tag from across all files.<br>
-Autocomplete tags while typing.<br>
-Autocomplete last tag, if adding multiple tags.<br>
-Add resize image to specified size(not just 1536 or 64 rounding)<br>
-Add convert image to specified format(not just png)<br>
-Add some more basic image editing(stretching, canvas size, crop)<br>
-Retreive more tags from image metadata on click<br>

<br>Dream Sheet:<br>
(I doubt I will, or be able to accomplish by myself.)<br>
-Have a input/reference directory set, to load images from directory but save in a output folder, then only modify the output directory files. Allowing reverting to reference/input directory on click.<br>
-And options for user options to select which colors they want specific tags to be.<br>
-Add option to create initial tags for image(s), using clip interrogators.<br>
