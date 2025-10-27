import os
import tempfile
import shutil
import json
import yaml
import streamlit as st
import pythoncom
import win32com.client
from PIL import Image
from pathlib import Path
import re

# SlideJet_convert is a tool to turn PowerPoint presentations in Streamlit Slideshows
#
# Execute this script with Streamlit on your local computer
#
# SlideJet_convert guides you through the process of converting your presentations


# --- Functions ---------------------------------------------------------------

def clear_old_files(folder_path):
    """Deletes all files in the folder before writing new ones."""
    if os.path.exists(folder_path):
        shutil.rmtree(folder_path)  # Delete everything inside the folder
    os.makedirs(folder_path)        # Recreate the folder

def convert_ppt_to_images_using_powerpoint(ppt_path, image_dir):
    """Uses PowerPoint COM automation to export full slides as images"""
    pythoncom.CoInitialize()
    powerpoint = win32com.client.Dispatch("PowerPoint.Application")
    powerpoint.Visible = 1          # Run PowerPoint in the background
    
    # Open the presentation
    presentation = powerpoint.Presentations.Open(ppt_path, WithWindow=False)
    
    # Ensure output directory exists and clear old images
    clear_old_files(image_dir)
    slide_data = []
    slide_count = presentation.Slides.Count
    for i in range(1, slide_count + 1):
        slide_filename = f"slide_{i}.png"
        slide_path = os.path.join(image_dir, slide_filename)
        try:
            presentation.Slides(i).Export(slide_path, "PNG")
            
            # Extract notes
            notes = "No notes"
            if presentation.Slides(i).NotesPage.Shapes.Count > 1:
                notes_shape = presentation.Slides(i).NotesPage.Shapes.Placeholders(2)
                if notes_shape.TextFrame.HasText:
                    notes = notes_shape.TextFrame.TextRange.Text.strip()
            
            # Store only relative path for the JSON
            slide_data.append({"image": f"images/{slide_filename}", "notes": notes})
        except Exception as e:
            st.error(f"Error exporting slide {i}: {e}")
    presentation.Close()
    #powerpoint.Quit()
    pythoncom.CoUninitialize()
    return slide_data

def save_slide_data_json(slide_data, json_file):
    """Saves slide images and notes in a structured JSON format for Streamlit slideshow."""
    with open(json_file, "w") as f:
        json.dump(slide_data, f, indent=4)

def save_yaml_config(yaml_output_path, slides_subfolder, header_text, subheader_text, mode, yaml_repo_path=None):
    if mode == "Local use":
        presentation_folder = slides_subfolder
    else:  # Online use (Streamlit Cloud)
        if yaml_repo_path is None:
            raise ValueError("For online use, 'yaml_repo_path' must be provided.")
        
        # Construct path inside the repo
        presentation_folder = os.path.join(yaml_repo_path, slides_subfolder).replace("\\", "/")

    config = {
        "presentation_folder": presentation_folder,
        "header_text": header_text,
        "subheader_text": subheader_text
    }

    with open(yaml_output_path, "w") as f:
        yaml.dump(config, f, default_flow_style=False, sort_keys=False)


def emit_present_script(
    yaml_file: str | Path,
    template_source: str | Path | None = None,
    template_name: str = "SlideJet_present_template.py",
    multipage: bool = False,
    app_id: str = "app_01",
    yaml_repo_path: str | None = None,   # repo-root–relative dir for ONLINE use
) -> Path:
    """
    Emit a presenter script next to the YAML.

    - If yaml_repo_path is given (Online use), the presenter will reference:
        f"{yaml_repo_path}/{<yaml_basename>}"
      which matches Streamlit Cloud's CWD = repo root.
    - Otherwise (Local use), it references a path relative to the presenter file.
    - If multipage=True, the st.set_page_config(...) line is commented out.
    - app_id is injected for namespacing (expects __APP_ID__ placeholder or literal APP_ID).
    """
    yaml_path = Path(yaml_file).resolve()
    yaml_dir  = yaml_path.parent
    yaml_stem = yaml_path.stem

    # Derive a clean base name WITHOUT trailing 'SJconfig' (case-insensitive, optional -,_,.)
    base_name = re.sub(r'(?i)[\-\_\.]?SJconfig$', '', yaml_stem).strip() or yaml_stem

    # Presenter goes next to the YAML
    target_dir = yaml_dir
    target_dir.mkdir(parents=True, exist_ok=True)

    # Load template text
    if template_source:
        tpl_text = Path(template_source).read_text(encoding="utf-8")
    else:
        tpl_text = (Path(__file__).parent / template_name).read_text(encoding="utf-8")

    # Compute YAML path to inject
    yaml_basename = yaml_path.name
    if yaml_repo_path:
        repo_rel_dir = Path(yaml_repo_path.strip("/\\")).as_posix()
        injected_yaml = f"{repo_rel_dir}/{yaml_basename}"
    else:
        # Local use: relative to presenter location
        injected_yaml = Path(os.path.relpath(yaml_path, start=target_dir)).as_posix()

    # --- Token replacements (simple)
    out_text = tpl_text
    out_text = out_text.replace("__SLIDEJET_YAML__", injected_yaml)
    out_text = out_text.replace("__IN_MULTIPAGE__", "True" if multipage else "False")
    out_text = out_text.replace("__PAGE_TITLE__", base_name.replace("_", " "))
    out_text = out_text.replace("__APP_ID__", app_id)

    # --- Robust fallbacks (if template lacks placeholders)
    # YAML_PATH = "..."
    out_text = re.sub(r'(YAML_PATH\s*=\s*)(["\']).*?\2', rf'\1"{injected_yaml}"', out_text)
    # IN_MULTIPAGE = True/False
    out_text = re.sub(r'(IN_MULTIPAGE\s*=\s*)(True|False)', rf'\1{"True" if multipage else "False"}', out_text)
    # APP_ID = "..."
    out_text = re.sub(r'(APP_ID\s*=\s*)(["\']).*?\2', rf'\1"{app_id}"', out_text)

    # --- If multipage, comment out st.set_page_config(...) line
    if multipage:
        out_text = re.sub(
            r'^\s*st\.set_page_config\([^\n]*\)\s*$',
            lambda m: f'# {m.group(0)}',
            out_text,
            flags=re.MULTILINE
        )

    # Write presenter: <BASE>_SJpresent.py
    present_name = f"{base_name}_SJpresent.py"
    out_file = target_dir / present_name
    out_file.write_text(out_text, encoding="utf-8")
    return out_file

# --- Application -------------------------------------------------------------

# Header and title
st.set_page_config(
    page_title="SlideJet - Convert",
    page_icon="🚀",
)

st.title("🚀 SlideJet-Convert")
st.header("PowerPoint to Streamlit-Ready Slideshow", divider= "green")

st.markdown(""" 
    ***SlideJet*** allows you to transfer a ***Powerpoint*** presentation with speaker notes into a ***Streamlit slideshow***. The transfer is done with the :green[***SlideJet-Convert***] tool.
    
    SlideJet works with any Powerpoint file.
    
    Subsequently, you can select and upload your presentation. Then, you can define the paths and folder name where :green[***SlideJet-Convert***] will save the data for the slideshow presentation.
    
    ***SlideJet*** works with running ***Powerpoint*** in the background to convert your slides. :red[**Now**] it's a good moment to safe your open presentations in case of unexpected troubles with Powerpoint.
        """)

st.subheader('First step: Upload the presentation file', divider = 'green')
# File upload section
uploaded_file = st.file_uploader("Upload a PowerPoint file", type=["pptx"])


if uploaded_file:
    
    # --- Step: Define Paths 
    st.subheader('Next step: Define paths', divider = 'green')
    st.markdown("""
    #### Local path - Place to save SlideJet data on your device - 
    
    ***SlideJet-***:green[***Convert***] will generate slideshow data that can be seen with the ***SlideJet-***:blue[***Present***] app. For this, ***SlideJet-***:green[***Convert***] transfers your PowerPoint presentation into images (= your slides) and a JSON file (= your speaker notes). It also prepares a _presentation-specific_ ***SlideJet-***:blue[***Present***] script (= the app) together with a ***YAML-file*** that contains the configuration data for this app.
    
    In conclusion, the following files are generate:
    - (1) a ***SlideJet-***:blue[***Present***] script = a file with the ending :grey[**FILENAME**]**_SJpresent.py**
    - (2) a ***YAML-file*** configuration dataset = a file with the ending :grey[**FILENAME**]**_SJconfig.yaml**
    - (3) a folder, usually named **SJ_Data**, with
       - (3a) a subfolder with the presentation slides as *.png images,
       - (3b) the speaker notes as JSON-file.
    
    The **SJ_Data** folder can contain subfolders to accomodate several presentations with their respective data.
    
    A general and recommended folder structure looks like 
    """
    )
    
    tree = """
    📁 project_root/                          # e.g., local copy of your GitHub repo
    └── 📁 SlideJet_Presentations/            # folder in the repo for presentations
        ├── 📁 SJ_Data/                       # folder containing SlideJet data
        │   └── 📁 [PRESENTATION_NAME]/       # individual folder for a presentation
        │       ├── 📁 images/                # (3a) folder with exported slides
        │       │   ├── slide_1.png           # image file of the slides
        │       │   ├── slide_2.png
        │       │   └── slide_n.png
        │       └── slide_data.json           # (3b) JSON with speaker notes
        ├── [PRESENTATION_NAME]_SJpresent.py  # (1) SlideJet_present app 
        └── [PRESENTATION_NAME]_SJconfig.yaml # (2) YAML config. data for (1)
    """.strip("\n")
        
    st.code(tree, language="text")
    
    st.markdown("""   
    ***Enter the local path***
    - As default, the folder where your ***SlideJet-***:green[***Convert***] app is placed is considered as project_root.
    - If you intent to deploy the ***SlideJet-***:blue[***Present***] app through GitHub, it is recommended to consider the local copy of the respective GitHub repository as project_root.
    
    Enter now your local path to ***SlideJet*** presentations. In the example above this path would be ***project_root/SlideJet_Presentations***.
    """)
    # Extract filename (without extension)
    pptx_filename = os.path.splitext(uploaded_file.name)[0].replace(" ", "_")

    # SlideJet_present folder (YAML will be saved here)
    default_folder = os.path.join(os.getcwd(), "SlideJet_Presentations")
    
    present_folder = st.text_input(
        "Enter local path in the text field below:",
        value=default_folder
    )

    st.markdown("""
    #### Information for online deployment
    ***SlideJet-***:blue[***Present***] is typically placed in an online repository (e.g., **GitHub**) from where the Streamlit slideshow is deployed. Accordingly, the ***SlideJet-***:blue[***Present***] app is started from the root level (**GitHub repository** respectively the ***project_root***), and the YAML file needs specific informations to find the presentation from the ***project_root***.
    """
    )
    
    deployment_mode = st.radio("Deployment Mode",["Online use (Streamlit Cloud)", "Local use"], index=0)
    
    if deployment_mode == "Online use (Streamlit Cloud)":
        st.markdown("""
        Further information for the ***Online use (Streamlit Cloud)*** option
        
        Consider that an :violet[**USER_X**] operates an :blue[**REPOSITORY_A**] on **GitHub.com**. Within this repository (= ***project_root***), the user defines a folder where all SlideJet presentations will be saved. This folder is named :orange[**SlideJet_Presentations**]. The structure would look like following:
        
        ***GitHub.com***/:violet[***USER_X***]/:blue[***Repository_A/***]:orange[SlideJet_presentations/]
        
        The relative  path from the repository would be :orange[**SlideJet_presentations**]
        
        Now, define the relative path from the repository to the YAML file in the text field below (:green[or simply confirm the presetting]):
        """)
    
    if deployment_mode == "Online use (Streamlit Cloud)":
        yaml_repo_path = st.text_input(
            "Enter the relative path",
            value="SlideJet_Presentations"
        )
    
    st.markdown("""
    #### Relative path to the presentation data
    ***SlideJet-***:blue[***Present***] access the data from a folder that is typically named **SJ_Data**. Within **SJ_Data**, each individual presentation can be saved in a subfolder. Subsequently, you can define the relative path, whereas the :green[presetting] considering [PRESENTATION_NAME] as subfolder is :green[generally suitable]:
    """
    )
    
    with st.expander("Click here to show an example and further explanation"):
        st.markdown("""
        ***Further information for the relative path***
        
        Consider the ***SlideJet-***:blue[***Present***] script and the **YAML-file** are placed in a folder ***SlideJet_presentations***.

        Inside this folder, the ***image/slides*** (as *.png graphics) and the **JSON-file** (speaker notes) can be saved in subfolders. Generally, the main subfolder is named **SJ_Data** and contains subfolders for the different presentations like _Presentation01_, _Presentation02_, and so on.
        
        The relative path to presentation data is used in the **YAML-file** to allow ***SlideJet-***:blue[***Present***] to identify the data that are required for the Streamlit slideshow.
        """)
    
    # Slides folder (relative to SlideJet_present folder)
    slides_subfolder = st.text_input(
        "Relative path where the slides will be saved (from YAML location). Eventually modify the :green[presetting].",
        value=os.path.join("SJ_DATA", pptx_filename).replace("\\", "/")
    )
    
    # Compute the absolute output directory
    slides_absolute_path = os.path.join(present_folder, slides_subfolder)
    
    # --- Step: PRESENTATION HEADERS
    st.subheader('SlideJet-Present header information', divider = 'green')
    st.markdown("""
    ***SlideJet-***:blue[***Present***] is an interactive Streamlit app that shows your presentation with notes as a slideshow. Subsequently, you can define the header and subheader for your specific ***SlideJet-***:blue[***Present***] Streamlit app. This information is safed in the YAML-file.
    """
    )
    
    default_header = f"{pptx_filename}"
    default_subheader = "Interactive Slideshow"
    header_text = st.text_input("Enter header text (main title)", value=default_header)
    subheader_text = st.text_input("Enter subheader text (subtitle or description)", value=default_subheader)

    # Define output folders dynamically
    OUTPUT_DIR = slides_absolute_path
    IMAGE_DIR = os.path.join(OUTPUT_DIR, "images")
    JSON_FILE = os.path.join(OUTPUT_DIR, "slide_data.json")

    # --- Final Step: Convert
    st.subheader('Final step: Convert the slideshow', divider = 'green')
    st.markdown("""
    SlideJet can already create the ***SlideJet-***:blue[***Present***] file that represents the Streamlit SlideShow. :red[Make sure] that the template file **SlideJet_present_template.py** is present in the folder from where you run this script. Also, please check if your presentation will be part of an multipage app - in that case, the ***SlideJet-***:blue[***Present***] app will be without a separate page title.
    
    Use the subsequent checkboxes to proceed. 
    """)
    make_presenter = st.checkbox("***SlideJet-***:blue[***Present***] file next to the YAML", value=True)
    multipage_true = st.checkbox("The SlideJet presentation will be part of an multipage app", value=False)

    app_id = "app_01"
    if multipage_true:
        app_id = st.text_input("Multipage app_id (used for namespacing state etc.)", value="app_01")
    
    col1, col2, col3 = st.columns((1,1,1))
    with col2:
        start_convert = st.button(":rainbow[**Convert PPT(X) to SlideJet**]")
        
    if start_convert:
        # Save uploaded file to a unique temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pptx") as tmp_file:
            tmp_file.write(uploaded_file.getbuffer())
            temp_ppt_path = tmp_file.name

        # Convert PPT slides to images using PowerPoint automation and extract notes
        slide_data = convert_ppt_to_images_using_powerpoint(temp_ppt_path, IMAGE_DIR)

        # Save slide data JSON for Streamlit slideshow
        save_slide_data_json(slide_data, JSON_FILE)

        if slide_data:
            st.success(f"Slides and notes successfully saved in `{OUTPUT_DIR}`.")
            st.success(f"Slide data JSON saved in `{JSON_FILE}`.")
            
            # Write YAML file in parent folder
            yaml_file = os.path.join(present_folder, f"{pptx_filename}_SJconfig.yaml")
            # Compute correct relative path from script dir to output dir
            #slides_relative_path = os.path.relpath(OUTPUT_DIR, script_dir).replace("\\", "/")
            if deployment_mode == "Online use (Streamlit Cloud)":
                save_yaml_config(
                    yaml_output_path=yaml_file,
                    slides_subfolder=slides_subfolder,
                    header_text=header_text,
                    subheader_text=subheader_text,
                    mode=deployment_mode,
                    yaml_repo_path=yaml_repo_path
                )
            else:
                save_yaml_config(
                    yaml_output_path=yaml_file,
                    slides_subfolder=slides_subfolder,
                    header_text=header_text,
                    subheader_text=subheader_text,
                    mode=deployment_mode
                )

            st.success(f"YAML config for SlideJet_present saved as `{yaml_file}`.")
            
            
            
            try:
                if make_presenter:
                    # Option A: template file lives next to this converter script
                    template_path = Path(__file__).parent / "SlideJet_present_template.py"

                    out_present = emit_present_script(
                        yaml_file=yaml_file,
                        template_source=template_path,
                        multipage=multipage_true,
                        app_id=app_id,
                        yaml_repo_path=yaml_repo_path if deployment_mode == "Online use (Streamlit Cloud)" else None,
                    )
                    st.success(f"SlideJet_present script created in: `{out_present}`")

            except Exception as e:
                st.warning(f"Could not create presenter script automatically: {e}")

            
            
            
            st.markdown("""
            #### Next steps
            Now you will find the slides, the speaker notes (as *.json file), the SlideJet_presentation, and the YAML file in the generated folders - see messages above. The see and present the slides, use the generated ***SlideJet-***:blue[***Present***] app (contains *_SJpresent.py* in the filename). Run this file on your local computer from the command prompt (CMD) with 'streamlit run project_root ... YOUR_PRESENTATION_SJpresent.py'.
            """)
        
        # Delete temporary file
        os.remove(temp_ppt_path)

'---'
# Authors, institutions, and year
year = 2025 
authors = {
    "Thomas Reimann": [1],  # Author 1 belongs to Institution 1
    "Nils Wallenberg": [2], # Author 2 belongs to Institution 2
}
institutions = {
    1: "TU Dresden",
    2: "University of Gothenburg"
}
author_list = [f"{name}{''.join(f'<sup>{i}</sup>' for i in idxs)}" for name, idxs in authors.items()]
institution_text = " | ".join([f"<sup>{i}</sup> {inst}" for i, inst in institutions.items()])

# Render footer with authors, institutions, and license logo in a single line
columns_lic = st.columns((4,1,1))
with columns_lic[0]:
    st.markdown(f'Developed by {", ".join(author_list)} ({year}). <br> {institution_text}', unsafe_allow_html=True)
with columns_lic[1]:
    try:
        img_sj = Image.open("FIGS/SlideJet_Logo_Wide_small.png")
        st.image(img_sj)
    except FileNotFoundError:
        st.image("https://raw.githubusercontent.com/gw-inux/SlideJet/main/FIGS/SlideJet_Logo_Wide_small.png")
    
with columns_lic[2]:
    try:
        st.image(Image.open("FIGS/CC_BY-SA_icon.png"))
    except FileNotFoundError:
        st.image("https://raw.githubusercontent.com/gw-inux/SlideJet/main/FIGS/CC_BY-SA_icon.png")