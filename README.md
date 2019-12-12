# Project-Amalgam
A resource Standardization Utility with a Machine Learning backend for Relevance analysis and automated Skimming

The system aims to provide alternative formatting to study material such that distractions are minimized. In extension, a lot of internal analysis has been implemented to dictate how resources are organized by metrics such as Cosine Score and Jaccard Analysis. Ease of use is a key feature thus a lot of the resource compilation is intended to be drag and drop, Copy and Pasting and Direct Uploads. The style of development, use of modules and even the technologies used are all a reflection of the design philosophy that Amalgam is built on. I aim to make use of modules that already exist such as pdf.js and react.js to facilitate the breakdown of pdf documents to html and to automatically render the added resources without reloading the whole document. The end product will be a software that has a minimalistic design with no need for sessions to add to the convenience and to protect user data. It is a tool for the public and as such, all the code and documentation will be publicized. Options to publish compiled resources will be developed as add-ons once the system is refined and it satisfies the basic requirements set for it. For now, the main types of resources targeted are videos, audio(Just Featured), images, web pages and pdfs(Analyzed through backend Machine Learning algorithms).  Other formats like docx can be converted to these formats for addition to the system but support for them might be facilitated if the system catches on.

To run the demo, clone the repo. You may use the command:

```
git clone https://github.com/GitWahome/Project-Amalgam/edit/master
```

Afterwards, navigate to the project directory. You may wish to create a virtual environment within which to work but that is all up to you. Whether in a virtual env or your global environment, you will need to install several Packages to make the system work. I have generated a requirements.txt file which you can install from using the command:

```
pip3 install -r requirements.txt
```

After that, you should be able to launch the program by running the run.py file

```
python3 run.py
```

# Note, 
The project is still a work in progress so some modules may not yet be functional. I have also automated the process of db and model creation under the run.py file hence why it is sufficient to just run it. It will automatically generate a site.db file which will save all the data.

After that, launch the system in your browser at the url:

```
http://127.0.0.1:5000/

```

Play around with the features, and to see the demo live, you may follow the youtube link below:
