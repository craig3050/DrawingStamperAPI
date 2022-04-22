from fastapi import FastAPI, UploadFile
from fastapi.responses import FileResponse
import secrets
import os
from os.path import basename
from PIL import Image, ImageDraw, ImageFont
import textwrap
from pdf_annotate import PdfAnnotator, Location, Appearance
from datetime import date
import zipfile

app = FastAPI()

def save_file(filepath, filename, data):
    # Check whether the specified path exists or not
    isExist = os.path.exists(filepath)
    if not isExist:
        # Create a new directory because it does not exist
        os.makedirs(filepath)
        print("The new directory is created!")

    fullfilepath = f"{filepath}/{filename}"
    with open(fullfilepath, 'wb') as f:
        f.write(data)


def make_token():
    # Creates a cryptographically-secure, URL-safe string
    return secrets.token_urlsafe(16)


def create_blank_stamp(stamp_type, optional_text):
    # Work out what words to use for the stamp
    if stamp_type == "A":
        text_for_stamp = "The Consultant’s review of this document is for the purpose of ascertaining compliance with the Project MEP Design Responsibility as defined in the contract documents. The review is based solely on the information presented on these documents, any errors or omissions in this submission will remain with the Contractor for meeting all the requirements of the Contract Documents, including all CDP works."
    elif stamp_type == "B":
        text_for_stamp = "The Consultant's review of this document is for the purpose of ascertaining conformity with the basic concept, profile and general arrangement only. The review shall not be construed to mean that BDP accept the detail design inherent in the drawing, responsibility for which will remain with the Contractor. The Contractor is responsible for any errors or omissions in the drawing and for meeting all the requirements of the Contract Documents."
    else:
        text_for_stamp = optional_text

    # Create the drawing stamp with logo
    blank_stamp_path = "AncillaryFiles/Drawing_Stamp_Blank.png"
    blank_stamp = Image.open(blank_stamp_path)
    blank_stamp_copy = blank_stamp.copy()
    logo = "AncillaryFiles/BDP_Logo.png"
    with Image.open(logo) as image_to_convert:
        thumbnail_size = 400, 250
        image_to_convert.thumbnail(thumbnail_size)
    w, h = image_to_convert.size
    position_width = (500 / 2) - (w / 2)  # width of box is 500 pixels wide
    position_height = (250 / 2) - (h / 2)  # height of box is 250 pixels high
    position = int(1000 + position_width), int(25 + position_height)
    try:
        blank_stamp_copy.paste(image_to_convert, position, image_to_convert)
    except Exception as e:
        print(e)
        try:
            blank_stamp_copy.paste(image_to_convert, position)
        except Exception as e:
            print(e)

    # Add the text to the drawing stamp
    text_wrapped = textwrap.wrap(text_for_stamp, width=67)
    print(text_wrapped)
    text_spacing = 50
    starting_point = 1000
    for line in text_wrapped:
        draw = ImageDraw.Draw(blank_stamp_copy)
        font = ImageFont.truetype("micross.ttf", 46)
        # draw.text((x, y),"Sample Text",(r,g,b))
        draw.text((40, starting_point), line, (255, 0, 0), font=font)
        starting_point += text_spacing

    return blank_stamp_copy


def add_stamp_to_drawing(filepath, file_name, project_number, received_date, user_initials, initial_status):
    filepath_for_stamped_files = f"{filepath}/Stamped"
    # Check whether the specified path exists or not
    isExist = os.path.exists(filepath_for_stamped_files)
    if not isExist:
        # Create a new directory because it does not exist
        os.makedirs(filepath_for_stamped_files)
        print("The new directory is created!")

    today = date.today()
    today_date = today.strftime("%d/%m/%y")

    full_drawing_path = f"{filepath}/{file_name}"
    full_path_drawing_stamp = f"{filepath}/Blank_Stamp.png"
    a = PdfAnnotator(full_drawing_path)
    # Add the stamp to the drawing
    a.add_annotation(
        'image',
        Location(x1=50, y1=50, x2=400, y2=400, page=0),
        Appearance(image=full_path_drawing_stamp)
    )
    # Add Project Number
    a.add_annotation(
        'text',
        Location(x1=120, y1=320, x2=300, y2=332, page=0),
        Appearance(stroke_color=(1, 1, 1), stroke_width=5, content=project_number,
                   fill=(0.705, 0.094, 0.125, 1))
    )
    # Add Received Date
    a.add_annotation(
        'text',
        Location(x1=130, y1=305, x2=300, y2=317, page=0),
        Appearance(stroke_color=(1, 1, 1), stroke_width=5, content=received_date,
                   fill=(0.705, 0.094, 0.125, 1))
    )
    # Add User Initials
    a.add_annotation(
        'text',
        Location(x1=75, y1=276, x2=300, y2=288, page=0),
        Appearance(stroke_color=(1, 1, 1), stroke_width=5,
                   content=user_initials, fill=(0.705, 0.094, 0.125, 1))
    )
    # Add Initial Status
    a.add_annotation(
        'text',
        Location(x1=200, y1=276, x2=320, y2=288, page=0),
        Appearance(stroke_color=(1, 1, 1), stroke_width=5, content=f"Status {initial_status}",
                   fill=(0.705, 0.094, 0.125, 1))
    )
    # Add Today's Date
    a.add_annotation(
        'text',
        Location(x1=330, y1=276, x2=400, y2=288, page=0),
        Appearance(stroke_color=(1, 1, 1), stroke_width=5, content=today_date, fill=(0.705, 0.094, 0.125, 1))
    )

    # Put an X in the box noting the status
    if initial_status == "A":
        a.add_annotation(
            'text',
            Location(x1=117, y1=203, x2=300, y2=215, page=0),
            Appearance(stroke_color=(1, 1, 1), stroke_width=5,
                       content="X", fill=(0.705, 0.094, 0.125, 1))
        )
    if initial_status == "B":
        a.add_annotation(
            'text',
            Location(x1=117, y1=189, x2=300, y2=201, page=0),
            Appearance(stroke_color=(1, 1, 1), stroke_width=5,
                       content="X", fill=(0.705, 0.094, 0.125, 1))
        )
    if initial_status == "C":
        a.add_annotation(
            'text',
            Location(x1=117, y1=174, x2=300, y2=186, page=0),
            Appearance(stroke_color=(1, 1, 1), stroke_width=5,
                       content="X", fill=(0.705, 0.094, 0.125, 1))
        )

    # Write the resultant file
    a.write(f'{filepath_for_stamped_files}/{file_name}')

    return


def zip_the_stamped_files(filepath_main, filepath_stamped):
    zip_file_name = f"{filepath_main}/Stamped_Files.zip"
    with zipfile.ZipFile(zip_file_name, 'w') as zip_file:
        for file in os.listdir(filepath_stamped):
            print(file)
            #zip_file.write(f"{filepath_stamped}/{file}", compress_type=zipfile.ZIP_DEFLATED)
            zip_file.write(f"{filepath_stamped}/{file}", basename(f"{filepath_stamped}/{file}"))
    return f"{filepath_main}/Stamped_Files.zip"


@app.post("/uploadfiles/{stamp_type}/{project_number}/{received_date}/{user_initials}/{initial_status}/{optional_text}")
async def create_upload_files(files: list[UploadFile], stamp_type: str, project_number: str, received_date:
str, user_initials: str, initial_status: str, optional_text: str):

    # Create a unique code for the folder where the files are kept
    unique_code = make_token()

    # Discard any filenames which are not PDFs
    files = [file for file in files if file.filename.endswith(".pdf")]

    # Create a directory and save the files
    for file in files:
            contents = await file.read()
            filepath = f"ReceivedFiles/{unique_code}"
            save_file(filepath, file.filename, contents)

    # Create and save the drawing stamp
    drawing_stamp = create_blank_stamp(stamp_type, optional_text)
    full_drawing_file_path = f"{filepath}/Blank_Stamp.png"
    drawing_stamp.save(full_drawing_file_path)

    # Stamp the files
    for file in files:
        add_stamp_to_drawing(filepath, file.filename, project_number, received_date, user_initials, initial_status)

    # Return a zip of all the stamped drawings
    #file_to_be_returned = f"ReceivedFiles/{unique_code}/{files[0].filename}"
    file_to_be_returned = zip_the_stamped_files(filepath, f"{filepath }/Stamped")
    return FileResponse(file_to_be_returned)



