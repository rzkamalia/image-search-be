import os
import psycopg2
import weaviate

class Database():
    def __init__(self, collection_name: str) -> None:
        # connect to weaviate database
        self.client = weaviate.Client("http://34.101.187.84:8080")

        self.collection_name = collection_name

        # connect to postgres database
        self.conn = psycopg2.connect(
            dbname = "postgres_suju",
            user = "postgres",
            password = "suju",
            host = "34.101.187.84",
            port = 5432
        )

        self.log_table_name = "search_image_logs"

    def creating_collection(self) -> None:
        '''
            create weaviate collection.
        '''

        try:
            self.client.schema.get(self.collection_name)
            print(f"Collection '{self.collection_name}' already exists.")
        except weaviate.exceptions.UnexpectedStatusCodeException:
            schema = {
                "class": self.collection_name,
                "properties": [
                    {
                        "name": "image",
                        "dataType": ["blob"],
                    },
                    {
                        "name": "filename",
                        "dataType": ["text"],
                    },
                ],
                "vectorizer": "img2vec-neural",
                "vectorIndexType": "hnsw",
                "moduleConfig": {
                    "img2vec-neural": {
                        "imageFields": [
                            "image"
                        ]
                    }
                }
            }
            self.client.schema.create_class(schema)
            print(f"The schema for collection '{self.collection_name}' has been created.")

    def insert_base64_to_collection(self, base64_imgs_path: str) -> None:
        '''
            insert base64 to weaviate collection.
        '''

        with self.client.batch(batch_size = 100) as batch:
            for filename in os.listdir(base64_imgs_path):
                if filename.endswith('.b64'):
                    with open(os.path.join(base64_imgs_path, filename), 'r') as file:
                        base64_encoding = file.read().replace("\n", "").replace(" ", "")
                    image_file = filename.replace(".b64", "")
                
                    data_properties = {
                        "image": base64_encoding,
                        "filename": image_file,
                    }

                    batch.add_data_object(data_properties, self.collection_name)

        print("The objects have been uploaded to Weaviate.")
    
    def create_log_table(self) -> None:
        '''
            create log table in postgres.
        '''

        with self.conn.cursor() as cur:
            cur.execute(f"""
            CREATE TABLE IF NOT EXISTS {self.log_table_name} (
                id SERIAL PRIMARY KEY,
                timestamp TIMESTAMP,
                image_name TEXT,
                results TEXT[]
            )
            """)
            self.conn.commit()

    def insert_log(self, datetime: str, filename: str, results: list) -> None:
        '''
            insert log to table in postgres.
        '''

        with self.conn.cursor() as cur:
            cur.execute(
                f"INSERT INTO {self.log_table_name} (timestamp, image_name, results) VALUES (%s, %s, %s)",
                (datetime, filename, results)
            )
            self.conn.commit()

    def query_image(self, base64_encoding: str):
        '''
            search image given a base64 query.
        '''

        result = self.client.query.get(self.collection_name, "filename").with_near_image(
            {"image": base64_encoding}, encode = False   # False because the image is already base64-encoded
            ).with_limit(4).do()
        print(result)
        return result["data"]["Get"][self.collection_name]