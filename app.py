import os
from flask import Flask, render_template
import requests

app = Flask(__name__)


@app.route("/")
def index():
  # Eurostat REST API URL matching the exact documentation structure:
  # {host_url}/{service}/{version}/{response_type}/{datasetCode}?{format}&{lang}&{filters}
  url = "https://ec.europa.eu/eurostat/api/dissemination/statistics/1.0/data/namq_10_gdp?format=JSON&lang=EN&s_adj=SCA&unit=CLV_PCH_PRE&na_item=B1GQ&geo=EA21"

  labels = []
  values = []
  error_message = None

  try:
    response = requests.get(url, timeout=20)
    response.raise_for_status()
    data = response.json()

    # Parse JSON-stat response structure as defined in Eurostat documentation
    dimensions = data["dimension"]
    time_categories = dimensions["time"]["category"]["index"]
    sorted_times = sorted(
        time_categories.keys(), key=lambda t: time_categories[t]
    )
    raw_values = data.get("value", {})

    for t in sorted_times:
      idx = time_categories[t]
      val = (
          raw_values.get(str(idx)) if str(idx) in raw_values else raw_values.get(idx)
      )
      if val is not None:
        labels.append(t)
        values.append(val)

  except Exception as e:
    error_message = f"Failed to fetch data from Eurostat API: {e}"
    print(error_message)

  return render_template(
      "index.html", labels=labels, values=values, error=error_message
  )


if __name__ == "__main__":
  port = int(os.environ.get("PORT", 5034))
  app.run(debug=True, host="0.0.0.0", port=port)