

## 🚀 Getting Started

<div align="center">
  <a href="#-prerequisites">
    <img src="https://img.shields.io/badge/1.-Prerequisites-4CAF50?style=for-the-badge&logo=check-circle&logoColor=white" alt="Prerequisites">
  </a>
  <span>→</span>
  <a href="#%EF%B8%8F-configuration">
    <img src="https://img.shields.io/badge/2.-Configuration-2196F3?style=for-the-badge&logo=cog&logoColor=white" alt="Configuration">
  </a>
  <span>→</span>
  <a href="#-deployment">
    <img src="https://img.shields.io/badge/3.-Deployment-9C27B0?style=for-the-badge&logo=rocket&logoColor=white" alt="Deployment">
  </a>
</div>

### 📋 Prerequisites

<div style="background: #f5f5f5; padding: 15px; border-radius: 8px; margin: 10px 0;">
  <table>
    <tr>
      <td><img src="https://img.icons8.com/color/24/000000/key.png"/></td>
      <td><strong>Groq API Key</strong></td>
      <td><a href="https://console.groq.com/">Get it here</a></td>
    </tr>
    <tr>
      <td><img src="https://img.icons8.com/color/24/000000/grafana.png"/></td>
      <td><strong>Grafana API Key</strong></td>
      <td>Create with <code>dashboards:write</code> permissions</td>
    </tr>
    <tr>
      <td><img src="https://img.icons8.com/color/24/000000/docker.png"/></td>
      <td><strong>Docker</strong> (Optional)</td>
      <td>Recommended for containerized deployment</td>
    </tr>
    <tr>
      <td><img src="https://img.icons8.com/color/24/000000/postgreesql.png"/></td>
      <td><strong>PostgreSQL</strong></td>
      <td>Running instance or use provided Docker setup</td>
    </tr>
  </table>
</div>

### ⚙️ Configuration

<div style="background: #f8f9ff; padding: 20px; border-radius: 8px; border-left: 4px solid #2196F3; margin: 15px 0;">
  <h3>1. Environment Setup</h3>
  <p>Create a <code>.env</code> file in the root directory with your GROQ API key:</p>
  
  ```env
  GROQ_API_KEY=your_groq_api_key_here
  ```
  
  <div style="background: #e3f2fd; padding: 10px; border-radius: 4px; margin: 10px 0;">
    <strong>ℹ️ Note:</strong> This is the only configuration needed in the <code>.env</code> file. All other configurations are managed through the Streamlit UI.
  </div>
</div>

<div style="background: #f8f9ff; padding: 20px; border-radius: 8px; border-left: 4px solid #4CAF50; margin: 15px 0;">
  <h3>2. Streamlit UI Configuration</h3>
  <p>Configure the following settings directly in the Streamlit UI when prompted:</p>
  
  <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 20px; margin: 15px 0;">
    <div style="background: white; padding: 15px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.05);">
      <h4>🔌 Grafana</h4>
      <ul style="margin: 10px 0 0 0; padding-left: 20px;">
        <li>URL: <code>http://localhost:3000</code></li>
        <li>API Key with <code>dashboards:write</code> permissions</li>
      </ul>
    </div>
    
    <div style="background: white; padding: 15px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.05);">
      <h4>📊 Prometheus</h4>
      <ul style="margin: 10px 0 0 0; padding-left: 20px;">
        <li>URL: <code>http://localhost:9090</code></li>
      </ul>
    </div>
    
    <div style="background: white; padding: 15px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.05);">
      <h4>🐘 PostgreSQL</h4>
      <ul style="margin: 10px 0 0 0; padding-left: 20px;">
        <li>Connection String: <code>postgresql://postgres:admin@localhost:5433/sales_db</code></li>
      </ul>
    </div>
  </div>
</div>

**Sample Connection Strings:**
- Grafana: `http://localhost:3000`
- Prometheus: `http://localhost:9090`
- PostgreSQL: `postgresql://postgres:admin@localhost:5433/sales_db`

### 🔍 Sample Database

<div style="background: #f0f7ff; padding: 20px; border-radius: 8px; margin: 20px 0;">
  <h2>🔍 Sample Database</h2>
  
  <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 20px; margin: 15px 0;">
    <div>
      <h3>📂 Included Files</h3>
      <ul>
        <li>Database schema and metadata in <code>metadata/</code> directory</li>
        <li>Sample data in CSV format in the root directory</li>
      </ul>
    </div>
    <div>
      <h3>🔑 Default PostgreSQL Credentials</h3>
      <table style="width:100%; border-collapse: collapse;">
        <tr>
          <td>Database:</td>
          <td><code>sales_db</code></td>
        </tr>
        <tr>
          <td>User:</td>
          <td><code>postgres</code></td>
        </tr>
        <tr>
          <td>Password:</td>
          <td><code>admin</code></td>
        </tr>
        <tr>
          <td>Port:</td>
          <td><code>5433</code></td>
        </tr>
      </table>
    </div>
  </div>
</div>

### 🚀 Deployment

### 🐳 Docker Deployment (Recommended)

<div style="background: #f5f5f5; padding: 20px; border-radius: 8px; margin: 15px 0;">
  <h3>Prerequisites</h3>
  <ul>
    <li>Docker installed on your system</li>
    <li>Docker Compose installed</li>
  </ul>
  
  <h3>Steps</h3>
  
  <div style="background: white; padding: 15px; border-radius: 8px; margin: 10px 0;">
    <h4>1. Navigate to project directory</h4>
    <pre style="background: #2d2d2d; color: #f8f8f2; padding: 10px; border-radius: 4px; overflow-x: auto;">
    cd /path/to/vizgenie</pre>
  </div>
  
  <div style="background: white; padding: 15px; border-radius: 8px; margin: 10px 0;">
    <h4>2. Start the containers</h4>
    <pre style="background: #2d2d2d; color: #f8f8f2; padding: 10px; border-radius: 4px; overflow-x: auto;">
    docker-compose up -d</pre>
  </div>
  
  <div style="background: #e8f5e9; padding: 15px; border-radius: 8px; margin: 15px 0 0 0; display: flex; align-items: center;">
    <div style="margin-right: 15px;">
      <img src="https://img.icons8.com/color/48/000000/info.png" width="24" height="24"/>
    </div>
    <div>
      <strong>Access the application:</strong> Once the containers are running, open your browser and navigate to <a href="http://localhost:8501">http://localhost:8501</a>
    </div>
  </div>
</div>
