# Smart Bookmarks
python project to suggest relevant folders while creating a bookmark using machine learning .
The Url and title of the existing bookmarks are used to train a classifier according to which the new bookmarks are assigned a folder.
The predictions are sorted according to relevance to the bookmark, the user can either select one of the predictions or mention a different folder.

# Usage

Run SmartBookmarks.py

```
python SmartBookmark.py
```

Selects the default bookmarks file which can be found at :

```
~/.config/google-chrome/Default/Bookmarks
```
  
To select some other bookmarks file 
```
python SmartBookmark.py --custom-file
```


## Todo
* develope a real time learning system where the system learns after adding each new bookmark
* do not flatten nested folders
* chrome extension

