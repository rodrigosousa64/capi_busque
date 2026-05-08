import glob
import json

files = glob.glob('pipeline_dados/dados_processados/**/*.json', recursive=True)
courses = set()

for f in files:
    try:
        with open(f, 'r', encoding='utf-8') as file:
            data = json.load(file)
            inst = data.get('institution', '')
            for offering in data.get('offerings', []):
                course = offering.get('course')
                campus = offering.get('campus')
                shift = offering.get('shift')
                if course:
                    courses.add(f"[{inst}] {course} - {campus} ({shift})")
    except Exception as e:
        print(f"Erro em {f}: {e}")

print(f"Total: {len(courses)} ofertas\n")
for c in sorted(courses):
    print(c)
