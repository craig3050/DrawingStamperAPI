from fastapi import FastAPI, UploadFile
from fastapi.responses import FileResponse
import secrets
import os
from PIL import Image, ImageDraw, ImageFont
import textwrap

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


def create_blank_stamp(filepath, stamp_type, optional_text):
    # Work out what words to use for the stamp
    if stamp_type == "A":
        text_for_stamp = "Insert stamp A words here"
    elif stamp_type == "B":
        text_for_stamp = "Insert stamp B words here"
    elif stamp_type == "C":
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
    full_drawing_file_path = f"{filepath}/Blank_Stamp.png"
    blank_stamp_copy.save(full_drawing_file_path)
    return blank_stamp_copy


def add_stamp_to_drawing(file_name, project_number, received_date, user_initials, initial_status):
    pass


@app.post("/uploadfiles/{stamp_type}/{project_number}/{received_date}/{user_initials}/{initial_status}/{optional_text}")
async def create_upload_files(files: list[UploadFile], stamp_type: str, project_number: str, received_date: str, user_initials: str, initial_status: str, optional_text: str):

    # Create a unique code for the folder where the files are kept
    unique_code = make_token()

    # Discard any filenames which are not PDFs
    files = [file for file in files if file.filename.endswith(".pdf")]

    # Create a directory and save the files
    for file in files:
            contents = await file.read()
            filepath = f"ReceivedFiles/{unique_code}"
            save_file(filepath, file.filename, contents)

    # Create the drawing stamp
    drawing_stamp = create_blank_stamp(filepath, stamp_type, optional_text)

    file_to_be_returned = f"ReceivedFiles/{unique_code}/{files[0].filename}"

    return FileResponse(file_to_be_returned)



