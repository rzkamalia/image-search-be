import os
import psycopg2
import weaviate

class Database():
    def __init__(self, collection_name: str) -> None:
        # connect to weaviate database
        self.client = weaviate.Client("http://34.101.224.203:8080")

        self.collection_name = collection_name

        # connect to postgres database
        self.conn = psycopg2.connect(
            dbname = "postgres_suju",
            user = "postgres",
            password = "suju",
            host = "34.101.224.203",
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
                "vectorIndexType": "hnsw"
            }
            self.client.schema.create_class(schema)
            print(f"The schema for collection '{self.collection_name}' has been created.")

    def insert_base64_to_collection(self, base64_imgs_path: str) -> None:
        '''
            insert base64 to weaviate collection.
        '''

        collection = self.client.schema.get(self.collection_name)
        with collection.batch as batch:
            for filename in os.listdir(base64_imgs_path):
                if filename.endswith('.b64'):
                    with open(os.path.join(base64_imgs_path, filename), 'r') as file:
                        base64_encoding = file.read().replace("\n", "").replace(" ", "")
                    image_file = filename.replace(".b64", "")
                
                    data_properties = {
                        "image": base64_encoding,
                        "filename": image_file,
                    }

                    batch.add_data_object(data_properties)

        print("The objects have been uploaded to Weaviate.")
    
    def create_log_table(self) -> None:
        '''
            cretae log table in postgres.
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
                "INSERT INTO search_image_logs (timestamp, image_name, results) VALUES (%s, %s, %s)",
                (datetime, filename, results)
            )
            self.conn.commit()

    def query_image(self, base64_encoding: str):
        '''
            search image given a base64 query.
        '''

        collection = self.client.schema.get(self.collection_name)
        return collection.query.near_image(
            near_image = base64_encoding,
            return_properties = ["filename"],
            limit = 4
        )
        