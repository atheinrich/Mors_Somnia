from PIL import Image 
import os
import re

def combine_images(input_folder, output_file):
    images = {}
    image_names = os.listdir(input_folder)

    # Parse image names and extract relevant info
    parsed_images = []
    for image_name in image_names:
        match = re.match(r'(\w+)_(\d+)_(\w+)_.*\.(png|jpg|jpeg)', image_name)
        if match:
            category, number, letter = match.groups()[:3]
            number = int(number)  # Convert to integer for correct sorting
            parsed_images.append((category, number, letter, image_name))
        else:
            print(f"Skipping {image_name}: does not match expected pattern.")
    
    # Sort images by the first letter of category, then by number, then by letter
    parsed_images.sort(key=lambda x: (x[0], x[1], x[2]))

    # Load images and organize them into rows by the numeric part
    for category, number, letter, image_name in parsed_images:
        image_path = os.path.join(input_folder, image_name)
        try:
            image = Image.open(image_path)
            key = f"{category}_{number}"
            if key not in images:
                images[key] = []
            images[key].append((letter, image))
        except Exception as e:
            print(f"Skipping {image_name}: {e}")

    if not images:
        print("No valid images found in the folder.")
        return

    # Calculate the size of the combined image
    max_width = max(image.size[0] for images_list in images.values() for _, image in images_list)
    total_height = sum(max(image.size[1] for _, image in images_list) for images_list in images.values())
    total_width = max(len(images_list) * max_width for images_list in images.values())
    
    combined_image = Image.new('RGBA', (total_width, total_height))
    
    # Combine the images into a single output image
    current_y = 0
    for images_list in images.values():
        row_height = max(image.size[1] for _, image in images_list)
        current_x = 0
        for _, image in images_list:
            combined_image.paste(image, (current_x, current_y))
            current_x += max_width
        current_y += row_height

    combined_image.save(output_file)
    print(f"Combined {sum(len(v) for v in images.values())} images into {output_file}")

if __name__ == "__main__":
    script_dir = os.path.dirname(os.path.realpath(__file__))
    input_folder = script_dir
    output_file = "0_tileset_ent.png"
    
    combine_images(input_folder, output_file)
