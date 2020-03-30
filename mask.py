import argparse
import cv2
import json
import sys

from pdf2image import convert_from_path 

ref_point = []
cropping = False
label_i = 0
label_step = 0

# Used to deactivate clic
def doNothing(event, x, y, flags, param):
    pass

# Catch mouse press - Draw marker on positions selected - Wait for user validation
def shape_selection(event, x, y, flags, param):
    global ref_point, cropping, label_i, label_step, data_to_extract, image

    if event == cv2.EVENT_LBUTTONDOWN:
        if label_step == 0:
            print('"start_x": {},'.format(x))
            print('"start_y": {},'.format(y))
            data_to_extract[labels[int(label_i)]] = {}
            data_to_extract[labels[label_i]]['start_x'] = x
            data_to_extract[labels[label_i]]['start_y'] = y

            ref_point = []
            ref_point.append((x, y))
            image = cv2.drawMarker(image, (x, y), (255, 0, 0), markerSize=10, thickness=1)
 
            label_step = 1
            return
        if label_step == 1:
            print('"end_x": {},'.format(x))
            print('"end_y": {},'.format(y))
            data_to_extract[labels[label_i]]['end_x'] = x
            data_to_extract[labels[label_i]]['end_y'] = y

            ref_point.append((x, y))

            label_step = 0
            image = cv2.drawMarker(image, (x, y), (255, 0, 0), markerSize=10, thickness=1)
            image = cv2.rectangle(image, ref_point[0], ref_point[1], (255, 0, 0), 1)

            start_y = data_to_extract[labels[label_i]]['start_y'] - 5
            end_y = data_to_extract[labels[label_i]]['end_y'] + 5
            start_x = data_to_extract[labels[label_i]]['start_x'] - 5
            end_x = data_to_extract[labels[label_i]]['end_x'] + 5
            
            crop_img = image[start_y:end_y, start_x:end_x]
            cv2.imshow('Selection', crop_img)
            cv2.setMouseCallback("image", doNothing)

            print('Valide : V - Recommencer : R')
            return

# Parse arguments
ap = argparse.ArgumentParser()
ap.add_argument("-p", "--pdf", required=False, help="Path to the PDF file")
ap.add_argument("-i", "--image", required=False, help="Path to the image")
ap.add_argument("-l", "--label", required=False, help="Path to the list of label")
args = vars(ap.parse_args())

print(args)

# PDF to jpg
if args['pdf'] is not None:
    filename = args['pdf']
    print('Converting {} to jpg'.format(filename))
    pages = convert_from_path(filename, 300, thread_count=4, grayscale=False)
    # Iterate through all the pages stored above 
    image_counter = 1
    jpg_page_name_list = []
    for page in pages:
        filenamejpg = filename + '_page' + str(image_counter) + ".jpg"
        print('Converting ' + str(filenamejpg) + '...')
        # Save the image of the page in system
        page.save(filenamejpg, 'JPEG')
        jpg_page_name_list.append(filenamejpg)
        # Increment the counter to update filename
        image_counter = image_counter + 1
    sys.exit()

# Load labels
f = open(args["label"], "r")
labels = f.read().split(',')

def ResizeWithAspectRatio(image, width=None, height=None, inter=cv2.INTER_AREA):
    dim = None
    (h, w) = image.shape[:2]

    if width is None and height is None:
        return image
    if width is None:
        r = height / float(h)
        dim = (int(w * r), height)
    else:
        r = width / float(w)
        dim = (width, int(h * r))

    return cv2.resize(image, dim, interpolation=inter)

# Load the image, clone it, and setup the mouse callback function
image = cv2.imread(args["image"])
# image = ResizeWithAspectRatio(image, height=1340)
cv2.namedWindow("image")
cv2.setMouseCallback("image", shape_selection)

# Load data extracted for current template if it exists
try:
    f = open(args["image"] + '_mask.json', "r")
    data_to_extract = json.loads(f.read())
    for key in data_to_extract:
        image = cv2.rectangle(image, (data_to_extract[key]['start_x'], data_to_extract[key]['start_y']), (data_to_extract[key]['end_x'], data_to_extract[key]['end_y']), (0, 255, 0), 1)
    print('data found : ', data_to_extract)
except:
    data_to_extract = {}

print('Current label = {}'.format(labels[0]))
current = image.copy()
init_image = image.copy()
while True:
    # Display the image and wait for a keypress
    cv2.imshow("image", image)
    key = cv2.waitKey(1) & 0xFF

    # If the 'r' key is pressed, reset the mask region
    if key == ord("r"):
        print('Retry for label ', labels[label_i])
        cv2.setMouseCallback("image", shape_selection)
        image = current.copy()

    # If the 'v' key is pressed validate selection and go to next label
    if key == ord("v"):
        if labels[label_i] not in data_to_extract:
            pass
        image = cv2.rectangle(image, ref_point[0], ref_point[1], (0, 255, 0), 1)
        if label_i == len(labels) - 1:
            with open(args['image'] + '_mask.json', 'w') as json_file:
                json.dump(data_to_extract, json_file, indent=4, sort_keys=True)
            break
        current = image.copy()
        label_i += 1
        cv2.setMouseCallback("image", shape_selection)
        print('Clic for label ', labels[label_i])

    # If the 's' key is pressed, print the current state of the extacted data
    if key == ord("s"):
        print(data_to_extract)

    # if the 'c' key is pressed, break from the loop
    if key == ord("c"):
        break

    # if the 'p' key is pressed, write the extracted mask in a json file
    if key == ord("p"):
        with open(args['image'] + '_mask.json', 'w') as json_file:
            json.dump(data_to_extract, json_file, indent=4, sort_keys=True)
        break

# Destroy all windows open
cv2.destroyAllWindows()
