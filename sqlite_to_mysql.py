import sqlite3
import re

def convert_sqlite_to_mysql(sqlite_db_path, mysql_sql_path):
    conn = sqlite3.connect(sqlite_db_path)
    
    with open(mysql_sql_path, 'w', encoding='utf-8') as f:
        f.write("SET FOREIGN_KEY_CHECKS = 0;\n")
        f.write("START TRANSACTION;\n\n")
        
        for line in conn.iterdump():
            # Ignore sqlite internal tables
            if 'sqlite_sequence' in line:
                continue
            
            # Replace PRAGMA
            if line.startswith('PRAGMA'):
                continue
                
            # Replace BEGIN TRANSACTION and COMMIT
            if line.startswith('BEGIN TRANSACTION'):
                continue
            if line == 'COMMIT;':
                continue
                
            # Replace AUTOINCREMENT with AUTO_INCREMENT
            line = line.replace('AUTOINCREMENT', 'AUTO_INCREMENT')
            
            # Replace double quotes for identifiers with backticks
            # A simple regex to replace "name" with `name`
            # Be careful with data that might have quotes, but in dump it's usually values are in single quotes, identifiers in double quotes
            # Actually, sqlite's iterdump uses double quotes for table and column names.
            def replace_quotes(match):
                return '`' + match.group(1) + '`'
            
            line = re.sub(r'"([^"]+)"', replace_quotes, line)
            
            f.write(line + "\n")
            
        f.write("\nCOMMIT;\n")
        f.write("SET FOREIGN_KEY_CHECKS = 1;\n")
    
    conn.close()

if __name__ == '__main__':
    convert_sqlite_to_mysql('db.sqlite3', 'chaplin_mysql_dump.sql')
    print("Conversão concluída. Arquivo chaplin_mysql_dump.sql gerado com sucesso.")
