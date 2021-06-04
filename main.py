# python script running on rasberry pi

# pseudocode
# take a picture from connected camera
# send image to Google Cloud API to detect cars and bounding box
# detect if bounding box overlaps with another box from that area
# if bounding box overlap is greater than 40%
# then there is a car parked in that parking spot and therefore it is not available
# respond from http request wether or not spot 1 2 of 3 are available
# if there is an available spot
# send my phone number a text saying which spots are available

# Author: A fellow Apt 11 squad member from the planet Quelte Quan

import json
import cv2
from google.cloud import vision


GOOGLE_APPLICATION_CREDENTIALS="AIzaSyBGfgyOqOKU-4K7PVDUhakBPtOIVLitF4c"
img_url = "https://i.imgur.com/K1fTnnx.jpg"
img_path = "./demo_photo.jpg"

def localize_objects(path):
    """Localize objects in the local image.

    Args:
    path: The path to the local file.
    """
    client = vision.ImageAnnotatorClient()

    with open(path, 'rb') as image_file:
        content = image_file.read()
    image = vision.Image(content=content)

    objects = client.object_localization(
        image=image).localized_object_annotations

    print('Number of objects found: {}'.format(len(objects)))
    for object_ in objects:
        print('\n{} (confidence: {})'.format(object_.name, object_.score))
        print('Normalized bounding polygon vertices: ')
        for vertex in object_.bounding_poly.normalized_vertices:
            print(' - ({}, {})'.format(vertex.x, vertex.y))
    
def draw_object_bounding_boxes(response_json):
    img = cv2.imread(img_path)
    height, width, channels = img.shape 
    result = img.copy()

    cars_found = filter(lambda object: object['name'] == 'Car', response_json['responses'][0]['localizedObjectAnnotations'])
    for index, car in enumerate(cars_found):
        corner1_dict = car['boundingPoly']['normalizedVertices'][0]
        corner2_dict = car['boundingPoly']['normalizedVertices'][2]
        corner1 = (int(corner1_dict['x']*width), int(corner1_dict['y']*height))
        corner2 = (int(corner2_dict['x']*width), int(corner2_dict['y']*height))
        
        cv2.rectangle(result, corner1, corner2, (0, 0, 255), 2)

        parking_spots = [((0.31, 0.45), (0.36, 0.49))]
        for pk_index, parking_spot in enumerate(parking_spots):
            pk_spot_corner1 = (int(parking_spot[0][0]*width), int(parking_spot[0][1]*height))
            pk_spot_corner2 = (int(parking_spot[1][0]*width), int(parking_spot[1][1]*height))

            cv2.rectangle(result, pk_spot_corner1, pk_spot_corner2, (255, 0, 0), 2)
            dy = min(pk_spot_corner2[1], corner2[1]) - max(pk_spot_corner1[1], corner1[1])
            dx = min(pk_spot_corner2[0], corner2[0]) - max(pk_spot_corner1[0], corner1[0])
            if dy < 0 or dx < 0:
                continue
            intersecting_area = dx * dy
            pk_spot_dx = pk_spot_corner2[0] - pk_spot_corner1[0]
            pk_spot_dy = pk_spot_corner2[1] - pk_spot_corner1[1]
            pk_spot_area = pk_spot_dx*pk_spot_dy
            percent_coverage = intersecting_area / pk_spot_area
            print(f'percentage coverage = {percent_coverage }')
            if percent_coverage > 0.8:
                print(f"parking spot {pk_index + 1} is occupied")

    
    cv2.imwrite("result.jpg",result) 
    cv2.imshow("bounding_box", result)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

if __name__ == "__main__":
    # localize_objects("./demo_photo.jpg")
    json_file = open('response.json',)
    response_json = json.load(json_file)
    draw_object_bounding_boxes(response_json)

