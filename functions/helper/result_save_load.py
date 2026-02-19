import pandas as pd
import os

def save_results_to_csv(results, agent_name, results_dir):
    """
    Speichert alle Zeitreihen eines Agents als CSV.
    """

    data = {}

    for var, values in results.items():
        data[var] = values

    df = pd.DataFrame(data)

    filename = os.path.join(results_dir,f"{agent_name.replace(' ', '_')}.csv")

    df.to_csv(filename, index=False)

    print(f"[Info] Saved results: {filename}")


def load_results_from_csv(agent_name, results_dir):
    """
    Lädt gespeicherte Agent-Resultate aus CSV.
    """

    filename = os.path.join(
        results_dir,
        f"{agent_name.replace(' ', '_')}.csv"
    )

    if not os.path.exists(filename):
        raise FileNotFoundError(f"Missing file: {filename}")

    df = pd.read_csv(filename)

    results = {
        "results": {}
    }

    for col in df.columns:
        results["results"][col] = df[col].to_numpy()

    print(f"[Info] Loaded results: {filename}")

    return results
