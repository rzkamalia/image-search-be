import os
import psycopg2
import weaviate

class Database():
    def __init__(self, collection_name: str) -> None:
        # connect to weaviate database
        self.client = weaviate.connect_to_local(
            host = "0.0.0.0",
            port = 8080,
            grpc_port = 50051,
        )

        self.collection_name = collection_name

        # connect to postgres database
        self.conn = psycopg2.connect(
            dbname = "postgres",
            user = "postgres",
            password = "suju",
            host = "localhost"
        )

        self.log_table_name = "search_image_logs"

    def creating_collection(self) -> None:
        '''
            create weaviate collection.
        '''

        self.client.collections.create(
            self.collection_name,
            vectorizer_config = weaviate.classes.config.Configure.Vectorizer.img2vec_neural(image_fields = ["image"]),
            vector_index_config = weaviate.classes.config.Configure.VectorIndex.hnsw(),
            properties = [
                weaviate.classes.config.Property(name = "image", data_type = weaviate.classes.config.DataType.BLOB),
                weaviate.classes.config.Property(name = "filename", data_type = weaviate.classes.config.DataType.TEXT),
            ]
        )
        print("The schema has been created.")

    def insert_base64_to_collection(self, base64_imgs_path: str) -> None:
        '''
            insert base64 to weaviate collection.
        '''

        collection = self.client.collections.get(self.collection_name)
        with collection.batch.dynamic() as batch:
            for filename in os.listdir(base64_imgs_path):
                if filename.endswith('.b64'):
                    with open(os.path.join(base64_imgs_path, filename), 'r') as file:
                        base64_encoding = file.read().replace("\n", "").replace(" ", "")
                    image_file = filename.replace(".b64", "")
                
                    data_properties = {
                        "image": base64_encoding,
                        "filename": image_file,
                    }

                    batch.add_object(data_properties)

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

        collection = self.client.collections.get(self.collection_name)
        return collection.query.near_image(
            near_image = base64_encoding,
            return_properties = ["filename"],
            limit = 4
        )
        