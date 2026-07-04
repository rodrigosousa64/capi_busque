import os
import sys

def normalize(text):
    return text.upper().strip().replace("Á", "A").replace("É", "E").replace("Í", "I").replace("Ó", "O").replace("Ú", "U").replace("Ç", "C").replace("Â", "A").replace("Ê", "E").replace("Õ", "O").replace("Ã", "A")

db_courses = []
with open(r"c:\Users\nawad\OneDrive\Desktop\MeusProjetos\capi_busque\scratch\db_courses.txt", "r", encoding="utf-8") as f:
    for line in f:
        line = line.strip()
        if not line: continue
        campus, name = line.split(" | ")
        db_courses.append((normalize(campus), normalize(name)))

user_courses = []
with open(r"c:\Users\nawad\OneDrive\Desktop\MeusProjetos\capi_busque\scratch\user_courses.txt", "r", encoding="utf-8") as f:
    for line in f:
        line = line.strip()
        if not line: continue
        parts = line.split("\t")
        if len(parts) >= 2:
            campus = parts[0].strip()
            # The name includes '001 - COURSE NAME (INFO)'
            course_info = parts[1].split("-", 1)[1].strip()
            # Split off the '('
            course_name = course_info.split("(")[0].strip()
            user_courses.append((campus, course_name, line))

missing = []
for uc_campus, uc_name, orig_line in user_courses:
    found = False
    norm_uc_campus = normalize(uc_campus)
    norm_uc_name = normalize(uc_name)
    
    # Try to match
    for db_campus, db_name in db_courses:
        if db_campus in norm_uc_campus and norm_uc_name in db_name:
            found = True
            break
        elif db_campus in norm_uc_campus and db_name in norm_uc_name:
            found = True
            break
            
    if not found:
        missing.append(orig_line)

with open(r"c:\Users\nawad\OneDrive\Desktop\MeusProjetos\capi_busque\scratch\missing_courses.txt", "w", encoding="utf-8") as f:
    for m in missing:
        f.write(f"{m}\n")
print(f"Total missing courses: {len(missing)}")
