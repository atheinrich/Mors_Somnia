from PIL import Image
import os
import re

def combine_images(input_folder, output_file):
    images = {}
    image_names = sorted(os.listdir(input_folder))
    
    for image_name in image_names:
        image_path = os.path.join(input_folder, image_name)
        try:
            image = Image.open(image_path)
            match = re.match(r'(\w+)_(\d+)(\w+)_.*\.(png|jpg|jpeg)', image_name)
            if match:
                category, number, letter = match.groups()[:3]
                key = f"{category}_{number}"
                if key not in images:
                    images[key] = []
                images[key].append((letter, image))
            else:
                print(f"Skipping {image_name}: does not match expected pattern.")
        except Exception as e:
            print(f"Skipping {image_name}: {e}")

    if not images:
        print("No valid images found in the folder.")
        return

    max_width = max(image.size[0] for images_list in images.values() for _, image in images_list)
    total_height = sum(max(image.size[1] for _, image in images_list) for images_list in images.values())
    total_width = max(len(images_list) * max_width for images_list in images.values())
    
    combined_image = Image.new('RGBA', (total_width, total_height))
    
    current_y = 0
    for images_list in images.values():
        images_list.sort(key=lambda x: x[0])  # Sort by the letter to maintain order
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
    output_file = "0_combined_image.png"  # Change this to the desired output file name
    
    combine_images(input_folder, output_file)
