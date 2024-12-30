###########################################################################################################################
#
#
#
###########################################################################################################################

###########################################################################################################################
# Imports
from PIL import Image
import os

###########################################################################################################################
# Definitions
def combine_images(input_folder, output_file):
    images = {}
    image_names = sorted(os.listdir(input_folder))
    
    for image_name in image_names:
        image_path = os.path.join(input_folder, image_name)
        try:
            image = Image.open(image_path)
            prefix = image_name[0]
            if prefix not in images:
                images[prefix] = []
            images[prefix].append(image)
        except:
            print(f"Skipping {image_path} as it cannot be identified.")

    if not images:
        print("No valid images found in the folder.")
        return

    max_width = max(image.size[0] for images_list in images.values() for image in images_list)
    total_height = sum(max(image.size[1] for image in images_list) for images_list in images.values())
    total_width = max(len(images_list) * max_width for images_list in images.values())
    
    combined_image = Image.new('RGBA', (total_width, total_height))
    
    current_y = 0
    for images_list in images.values():
        row_height = max(image.size[1] for image in images_list)
        current_x = 0
        for image in images_list:
            combined_image.paste(image, (current_x, current_y))
            current_x += max_width
        current_y += row_height

    combined_image.save(output_file)
    print(f"Combined {sum(len(v) for v in images.values())} images into {output_file}")

###########################################################################################################################
# Global
if __name__ == "__main__":
    script_dir = os.path.dirname(os.path.realpath(__file__))
    input_folder = script_dir
    output_file = "combined_image.png"  # Change this to the desired output file name
    
    combine_images(input_folder, output_file)

###########################################################################################################################