# Guide: Migrating Apps to Coolify v3

Use these steps to move your apps into your legacy Coolify v3 instance.

## 1. Connect your Git Source (GitHub/GitLab)
1.  Click on **Sources** in the sidebar or top navbar.
2.  Click **+ Add**.
3.  Choose **GitHub App** and follow the authorization.

## 2. Add an Application (using Docker Compose)
Coolify v3 handles Docker Compose through the **Applications** menu.

1.  Click on **Applications** in the top/side menu.
2.  Click **+ New Application**.
3.  **Destinations**: Select **Local**.
4.  **Source**: Select your **GitHub Source**.
5.  **Repository**: Choose your `aadikarta-social-media` repo and branch.
6.  **Build Pack**: Select **Docker Compose**.
7.  **YAML**: Paste the contents of your `docker-compose.coolify.yml` here.

## 3. Configure the Domain & SSL
Unlike v4, in v3 you typically set your URL in the **General** settings of the application.

1.  Click the **Settings** or **General** tab for your new resource.
2.  Find the **FQDN (Full Qualified Domain Name)** field.
3.  Enter your URL: `https://aadikarta.org` (or `https://n8n.aadikarta.org`).
4.  **Important**: In a multi-service Compose file, Coolify v3 might require you to set up different Applications or use specific labels. 

## 4. Environment Variables
1.  Go to the **Environment Variables** tab.
2.  Add your secrets and API keys here.

## 5. Deploy
1.  Click **Deploy**.
2.  Watch the build logs.
3.  Once finished, your site will be available at the domain you specified.

---
> [!TIP]
> Since you have 1 CPU core, keep an eye on the **CPU Usage** on the dashboard. Avoid running too many simultaneous builds.
