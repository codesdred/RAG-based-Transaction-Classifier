import mysql.connector
from mysql.connector import Error
import pandas as pd
import yaml

class DBManager:
    def __init__(self):
        self.config = {
            'host': 'localhost',
            'user': 'root',
            'password': 'sanju2004',
            'database': 'transaction_handler'
        }

    def get_connection(self):
        try:
            return mysql.connector.connect(**self.config)
        except Error as e:
            print(f"❌ DB Error: {e}")
            return None

    def get_knowledge_base(self):
        """
        Fetches data for the Vector Index.
        Returns: List of {merchant, label, explanation}
        """
        conn = self.get_connection()
        cursor = conn.cursor(dictionary=True)
        
        # FIX: Added 'explanation' to GROUP BY to satisfy MySQL only_full_group_by mode
        query = """
        SELECT merchant, category as label, explanation 
        FROM transactions 
        GROUP BY merchant, category, explanation
        """
        
        cursor.execute(query)
        rows = cursor.fetchall()
        conn.close()
        return rows

    def get_all_labels(self):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT DISTINCT category FROM transactions")
        rows = cursor.fetchall()
        conn.close()
        return [r[0] for r in rows]

    def save_transaction(self, data):
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Insert Transaction
        query = """
        INSERT INTO transactions (merchant, amount, txn_date, category, explanation, status)
        VALUES (%s, %s, %s, %s, %s, %s)
        """
        cursor.execute(query, (
            data['merchant'], data['amount'], data['date'], 
            data['label'], data['explanation'], data['status']
        ))
        
        # Ensure Category exists in Master List (for YAML sync)
        cursor.execute("INSERT IGNORE INTO categories (name) VALUES (%s)", (data['label'],))
        
        conn.commit()
        conn.close()
        self.sync_yaml()

    def update_category(self, txn_id, new_label):
        """
        Updates a label and performs GARBAGE COLLECTION on unused labels.
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # 1. Get Old Label
        cursor.execute("SELECT category FROM transactions WHERE id = %s", (txn_id,))
        old_label = cursor.fetchone()[0]
        
        # 2. Update Transaction
        cursor.execute("UPDATE transactions SET category = %s, status='User-Edited' WHERE id = %s", (new_label, txn_id))
        
        # 3. Add New Label to Master List
        cursor.execute("INSERT IGNORE INTO categories (name) VALUES (%s)", (new_label,))
        
        # 4. GARBAGE COLLECTION: Check if Old Label is now empty
        cursor.execute("SELECT COUNT(*) FROM transactions WHERE category = %s", (old_label,))
        count = cursor.fetchone()[0]
        
        if count == 0:
            print(f"🧹 Cleaning up unused label: {old_label}")
            cursor.execute("DELETE FROM categories WHERE name = %s", (old_label,))
            
        conn.commit()
        conn.close()
        self.sync_yaml()

    def sync_yaml(self):
        labels = self.get_all_labels()
        try:
            with open("config.yaml", "w") as f:
                yaml.dump({"active_labels": labels}, f)
        except: pass

    def get_ledger_data(self):
        conn = self.get_connection()
        df = pd.read_sql("SELECT id, txn_date as Date, merchant as Merchant, amount as Amount, category as Label, explanation as Explanation FROM transactions ORDER BY id DESC", conn)
        conn.close()
        return df