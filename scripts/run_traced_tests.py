import json
import urllib.request
import urllib.error

URL = "http://127.0.0.1:8000/query"

tests = [
    {
        "question": "¿Qué es Python y cuáles son las características principales de sus listas?",
        "mode": "research"
    },
    {
        "question": "Explicá cómo funcionan los métodos HTTP de una API REST.",
        "mode": "research"
    },
    {
        "question": "¿Qué diferencias existen entre una clave primaria y una clave foránea en SQL?",
        "mode": "research"
    },
    {
        "question": "Analizá las ventajas y los riesgos de automatizar procesos mediante inteligencia artificial.",
        "mode": "analysis"
    },
    {
        "question": "Explicá cómo Git permite controlar versiones y trabajar con ramas.",
        "mode": "auto"
    }
]

for i, test in enumerate(tests, 1):
    print(f"\n{'=' * 55}")
    print(f"PRUEBA {i}/5 - {test['mode'].upper()}")
    print(f"PREGUNTA: {test['question']}")

    request = urllib.request.Request(
        URL,
        data=json.dumps(test).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST"
    )

    try:
        with urllib.request.urlopen(request, timeout=90) as response:
            result = json.loads(response.read().decode("utf-8"))
            print("HTTP:", response.status)
            print("THREAD:", result.get("thread_id"))
            print("AGENTE:", result.get("agent"))
            print("FUENTES:", len(result.get("sources", [])))
            print("RESPUESTA:", str(result.get("answer", ""))[:350])
    except urllib.error.HTTPError as error:
        print("ERROR HTTP:", error.code)
        print(error.read().decode("utf-8"))
    except Exception as error:
        print("ERROR:", error)

print("\nFINALIZADAS LAS CINCO PRUEBAS")
