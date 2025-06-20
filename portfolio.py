import pandas as pd
import chromadb
import uuid


class Portfolio:
    def __init__(self, file_path=r"D:\Development_Content\MACHINE_LEARNING\Cold_Email_Generator\app\resource\portfolio.csv"):
        self.file_path = file_path
        self.data = pd.read_csv(file_path)
        self.chroma_client = chromadb.PersistentClient('vectorstore')
        self.collection = self.chroma_client.get_or_create_collection(name="portfolio")

    def load_portfolio(self):
        if not self.collection.count():
            for _, row in self.data.iterrows():
                self.collection.add(documents=row["Tech Stacks"],
                                    metadatas={"links": row["Links"]},
                                    ids=[str(uuid.uuid4())])

    def query_links(self, skills):

        if not skills:
            return []
        return self.collection.query(query_texts=skills, n_results=2).get('metadatas', [])