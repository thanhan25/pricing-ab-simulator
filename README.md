# ?? Algorithmic Pricing Engine & A/B Testing Simulator

An enterprise-grade analytical pipeline that evaluates how structural pricing changes impact conversion mechanics and gross margins, utilizing frequentist hypothesis testing to validate statistical significance.

## ??? Tech Stack & Architecture
* **Core Language:** Python (`scipy.stats`, `statsmodels`, `pandas`, `numpy`)
* **Interface & BI Visuals:** Streamlit, Plotly Canvas
* **Infrastructure Layer:** Docker Containers
* **Automation Pipeline:** GitHub Actions (CI/CD)

## ?? Core Methodologies Featured
* **Price Elasticity of Demand (PED):** Modeling nonlinear demand curves based on price fluctuations.
* **Power Analysis:** Quantifying sample size limitations required to reach statistical bounds before running experiments.
* **Frequentist Inference:** Executing two-proportion Z-tests to explicitly reject or fail to reject the null hypothesis.
* **Unit Economics:** Mapping conversion lifts directly to Revenue Per Visitor (RPV) and projected net profit margins.

## ?? Quick-Start Docker Deployment
Ensure your local Docker Desktop engine is active, then execute:

```powershell
# Build the production application layer
docker build -t pricing-ab-simulator:v1.0 .

# Run the container isolated on port 8501
docker run -d -p 8501:8501 --name elastic-pricing-engine pricing-ab-simulator:v1.0
Once deployed, navigate to http://localhost:8501 to access the interactive analytics control room.
