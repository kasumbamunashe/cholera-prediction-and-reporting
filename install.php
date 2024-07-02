import psycopg2
from psycopg2 import sql
import bcrypt

# PostgreSQL connection parameters
conn_params = {
    'host': 'localhost',
    'dbname': 'kadoma_cholera',
    'user': 'postgres',
    'password': 'Munashe056'
}

# Create a table if it doesn't exist
def create_admins_table(conn):
    with conn.cursor() as cursor:
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS admins (
            id SERIAL PRIMARY KEY,
            username VARCHAR(255) NOT NULL,
            password VARCHAR(255) NOT NULL,
            email VARCHAR(255) NOT NULL UNIQUE
        )
        """)
        conn.commit()

# Insert a super admin account with hashed password
def insert_super_admin(conn, username, password, email):
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    with conn.cursor() as cursor:
        cursor.execute("""
        INSERT INTO admins (username, password, email)
        VALUES (%s, %s, %s)
        """, (username, hashed_password, email))
        conn.commit()

# Main function to connect and run the script
def main():
    try:
        # Connect to the PostgreSQL database
        conn = psycopg2.connect(**conn_params)

        # Create the admins table if it doesn't exist
        create_admins_table(conn)

        # Insert a super admin account
        username = 'jimmy'
        password = 'jimmy'
        email = 'munashekasumba@gmail.com'
        insert_super_admin(conn, username, password, email)

        print("Super admin account created successfully!")

    except psycopg2.Error as e:
        print(f"Error connecting to PostgreSQL: {e}")

    finally:
        # Close the database connection
        if conn:
            conn.close()

if __name__ == "__main__":
    main()
