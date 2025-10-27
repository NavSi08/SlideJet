## 🚀 SlideJet

**SlideJet** is a lightweight tool that transforms PowerPoint presentations into interactive web apps using [Streamlit](https://streamlit.io). It converts your slides into a slideshow, complete with speaker notes that can be translated in several languages. SlideJet also brings an option to convert the slideshow in a PDF file for further use like doing notes. **SlideJet** is an ideal tool for teaching, workshops, training materials, and documentation.

SlideJet consists of two components:

1. **SlideJet-Convert**: A Streamlit application that runs locally and converts PowerPoint presentations (including speaker notes) into web-ready graphics and note files.
2. **SlideJet-Present**: A Streamlit application to present the converted slides in a user-friendly web format. Presentations can be deployed online via platforms like Streamlit Community Cloud.

[**See an working example by clicking here**](https://slidejet-outline.streamlit.app/)

---

### ✨ Features

- Convert PowerPoint slides and notes into web-optimized figures and data.
- Display slides directly in a Streamlit app.
- Show speaker notes alongside each slide.
- Speaker notes can be translated in different languages.
- Slides with speaker notes can be transfered in PDF for user download.

---

### 💻 Requirements

To run **SlideJet-Convert**, you need the following installed locally (on **Windows**):

- [Python](https://www.python.org/downloads/),
- [Microsoft PowerPoint](https://www.microsoft.com/microsoft-365/powerpoint),
- Python packages: `streamlit`, `pywin32`, `Pillow`, and `deep-translator`,
- Download **SlideJet_convert.py** and **SlideJet_present_template.py** in a folder of your choice,
- [For online deployment/sharing a GitHub account is recommended].
  
---

### ⚙️ Installation and running the app

If not already on your computer: Please install Python (e.g., through a distribution like Anaconda, or by downloading from www.python.org)

Download the Python files **SlideJet_convert.py** and **SlideJet_present_template.py** on a folder on your local computer

Open a **Command Prompt** and run the following command:

```bash
pip install streamlit
```

Then you add the required Python libraries with the command: pip install …
 (https://docs.streamlit.io/get-started/installation)
 
 ```bash
pip install pywin32
```

(this should include pythoncom and win32com)

 ```bash
pip install Pillow
```

(this should include PIL)

 ```bash
pip install deep-translator
```

Then start the app with the command window from the folder where SlideJet_convert.py is saved with:

```bash
streamlit run SlideJet_convert.py
```

### 📺 Getting Started

A short tutorial and video guide (link coming soon) will walk you through the full process.
With a decent internet connection, the entire setup takes just a few minutes. Subsequent transfering of Powerpoint presentation in web applications is just a matter of seconds.

The Presentation [**SlideJet - Overview**](https://slidejet-outline.streamlit.app/) introduces the app and provide further guidance on use.

<img src="FIGS/SlideJet_Logo_Wide_small.png" alt="SlideJet Logo" width="300">
