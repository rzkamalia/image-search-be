# run this first, before run main.py

import os
import base64

from database import Database

COLLECTION_NAME = "ImageSearchApp"

class VectorizeExecutor():
    def __init__(self, soure_imgs_path: str, base64_imgs_path: str, collection_name: str) -> None:
        self.db = Database(collection_name = collection_name)
        
        self.soure_imgs_path = soure_imgs_path
        self.base64_imgs_path = base64_imgs_path

    def convert_image_to_base64(self):
        '''
            convert image to base64.
        '''

        os.makedirs(self.base64_imgs_path, exist_ok = True)
        
        for file_name in os.listdir(self.soure_imgs_path):
            if file_name.startswith('.') or not file_name.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp')):
                continue
            
            file_path = os.path.join(self.soure_imgs_path, file_name)
            
            if not os.path.isfile(file_path):
                continue
                        
            with open(file_path, "rb") as image_file:
                encoded_string = base64.b64encode(image_file.read()).decode('utf-8')
            
            # write the base64 string to a new file
            output_file = os.path.join(self.base64_imgs_path, f"{file_name}.b64")
            with open(output_file, "w") as base64_file:
                base64_file.write(encoded_string)
            
        print("The images have been converted to base64.")

    def main(self) -> None:
        '''
            main method for vectorize images, and store the result to weaviate collection.
        '''

        self.db.creating_collection()
        self.convert_image_to_base64()
        self.db.insert_base64_to_collection(self.base64_imgs_path)

vectorize = VectorizeExecutor(soure_imgs_path = "assets/imgs", base64_imgs_path = "assets/base64_imgs", collection_name = COLLECTION_NAME)
vectorize.main()