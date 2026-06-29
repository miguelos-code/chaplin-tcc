import sqlite3
import re

def convert_sqlite_to_mysql_zerado(sqlite_db_path, mysql_sql_path):
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
                
            # Skip INSERT statements for tasks related tables to make it "zerado e sem nenhuma tarefa"
            if line.startswith('INSERT INTO "tasks_task"'):
                continue
            if line.startswith('INSERT INTO "tasks_taskevidence"'):
                continue
            if line.startswith('INSERT INTO "tasks_message"'):
                continue
            if line.startswith('INSERT INTO "tasks_notification"'):
                continue
                
            # Replace AUTOINCREMENT with AUTO_INCREMENT
            line = line.replace('AUTOINCREMENT', 'AUTO_INCREMENT')
            
            def replace_quotes(match):
                return '`' + match.group(1) + '`'
            
            # This regex replaces double quotes around table/column names with backticks
            line = re.sub(r'"([^"]+)"', replace_quotes, line)
            
            f.write(line + "\n")
            
        f.write("\nCOMMIT;\n")
        f.write("SET FOREIGN_KEY_CHECKS = 1;\n")
    
    conn.close()

if __name__ == '__main__':
    convert_sqlite_to_mysql_zerado('db.sqlite3', 'chaplin_mysql_dump_zerado.sql')
    print("Conversão concluída. Arquivo chaplin_mysql_dump_zerado.sql gerado com sucesso.")
